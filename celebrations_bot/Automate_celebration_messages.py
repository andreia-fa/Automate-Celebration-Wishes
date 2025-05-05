import logging
import random
from datetime import datetime, timedelta
from telethon import TelegramClient
import os
import time




# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(filename)s:%(lineno)d - %(asctime)s - %(levelname)s - %(message)s')

class Automate_messages:
    def __init__(self, session_file_name, app_id, app_hash, sql_connection):
        self.session_file_name = session_file_name
        self.app_id = app_id
        self.app_hash = app_hash
        self.sql_connection = sql_connection  

    def should_event_message_be_sent(self, mysql_cnx, messages_table):
        contacts_with_events = self.sql_connection.get_contacts_for_today_events(mysql_cnx)
        if not contacts_with_events:
            logging.info("No contacts with events today.")
            return "No contacts with events today!!!"

        for name, (event_date, mobile_number, category, event_type_from_event_table) in contacts_with_events.items():

            # ✅ Get correct contact_id for this username
            contact_id_query = "SELECT id FROM contacts_info WHERE username = %s"
            cursor = mysql_cnx.cursor()
            cursor.execute(contact_id_query, (name,))
            result = cursor.fetchone()
            cursor.close()

            if result:
                contact_id = result[0]
                # ✅ Now correctly determine event_type using contact_id (fixes 'baby' detection)
                event_type = self.sql_connection.get_event_type(mysql_cnx, contact_id)
            else:
                logging.warning(f"⚠️ Could not resolve contact_id for {name}, using fallback event_type from event table.")
                event_type = event_type_from_event_table or "birthday"

            # ✅ Get last sent message (to avoid repeats)
            last_message_text = self.sql_connection.get_last_sent_message(mysql_cnx, name)

            # ✅ Pick a new message excluding last one
            message_id, celebration_message = self.sql_connection.get_event_message(mysql_cnx, messages_table, event_type, last_message_text)

            if celebration_message:
                if not self.has_message_been_sent(mysql_cnx, name, event_type):
                    # ✅ Correctly personalize the message including #{month_count} if needed
                    customized_message = self.customize_message(celebration_message, name, event_type, event_date)

                    logging.info(f"📨 Sending {event_type} message to {name}. Message: {customized_message}")
                    send_status = self.send_msg(name, mobile_number, customized_message)

                    if send_status == "Success":
                        self.sql_connection.log_message_sent(mysql_cnx, name, event_type, message_id, customized_message)
                        logging.info(f"✅ Sent {event_type} message to {name}: {customized_message}")
                    else:
                        logging.error(f"❌ Failed to send {event_type} message to {name}")
                else:
                    logging.info(f"⚠️ {event_type.capitalize()} message (ID: {message_id}) to {name} has already been sent.")
            else:
                logging.error(f"❌ No message found for event type: {event_type}")

        return "Event messages processed."



    def send_nurturing_messages(self, mysql_cnx, messages_table):
        """ 
        Sends nurturing messages to all contacts who haven't received *any* message 
        (birthday, nurturing, etc.) in the last two months,
        and are not receiving a birthday message today.
        Only sends messages to persons (not puppies or babies). 
        """
        today = datetime.now().date()
        cursor = mysql_cnx.cursor()

        # Get all contacts of type 'person'
        query_contacts = "SELECT id, username, mobile_number, birthday_date FROM contacts_info WHERE category = 'person'"
        cursor.execute(query_contacts)
        contacts = cursor.fetchall()

        # Get a list of nurturing messages
        query_message = f"SELECT id, text_message FROM {messages_table} WHERE type = 'nurturing'"
        cursor.execute(query_message)
        nurturing_messages = cursor.fetchall()

        if not nurturing_messages:
            logging.error("❌ No 'nurturing' messages found in the messages table.")
            return

        # ✅ Shuffle contacts to avoid always starting with same people
        random.shuffle(contacts)

        daily_limit = 2
        sent_today = 0

        for contact in contacts:
            if sent_today >= daily_limit:
                logging.info("🛑 Daily nurturing limit reached — stopping.")
                break

            contact_id, username, mobile_number, birthday_date = contact
            logging.debug(f"👀 Evaluating: {username} (ID {contact_id}) — {mobile_number}")

            # 1️⃣ Skip if today is their birthday
            if birthday_date and birthday_date.month == today.month and birthday_date.day == today.day:
                logging.info(f"🎂 {username} has a birthday today. Skipping nurturing message.")
                continue

            # 2️⃣ Skip if any message was sent recently (birthday, nurturing, anything)
            query_last_sent = """
                SELECT date_sent FROM message_log
                WHERE contact_id = %s
                ORDER BY date_sent DESC LIMIT 1
            """
            cursor.execute(query_last_sent, (contact_id,))
            last_sent_result = cursor.fetchone()

            if last_sent_result:
                last_sent_date = last_sent_result[0].date()
                if last_sent_date > (today - timedelta(days=60)):
                    logging.info(f"⏩ Skipping {username}, message already sent within 60 days.")
                    continue

            # 3️⃣ Select and personalize a nurturing message
            message_id, message_text = random.choice(nurturing_messages)
            personalized_message = message_text.replace("{name}", username)

            # 4️⃣ Send message
            send_status = self.send_msg(username, mobile_number, personalized_message)

            # ✅ Log only on successful send
            if send_status == "Success":
                self.sql_connection.log_message_sent(
                    mysql_cnx, username, "nurturing", message_id, personalized_message
                )
                logging.info(f"✅ Nurturing message sent to {username}.")
                sent_today += 1
            else:
                logging.error(f"❌ Failed to send nurturing message to {username}.")

        cursor.close()


    def customize_message(self, message_template, name, type_, date_str=None):
        """
        Customize message by replacing placeholders, including {month_count}.
        """
        message = message_template.replace("{name}", name)

        if type_ in ["puppy", "baby"] and date_str:
            event_date = datetime.strptime(date_str, "%Y-%m-%d")
            month_count = (datetime.now().year - event_date.year) * 12 + (datetime.now().month - event_date.month)
            message = message.replace("#{month_count}", str(month_count))

        return message


    def has_message_been_sent(self, cnx, person_name, event_type):
        cursor = cnx.cursor()
        now = datetime.now()

        if event_type in ["birthday", "new year", "Christmas"]:
            query = """
                SELECT COUNT(*) FROM message_log 
                WHERE contact_id = (SELECT id FROM contacts_info WHERE username = %s) 
                AND event_type = %s
                AND YEAR(date_sent) = %s
            """
            params = (person_name, event_type, now.year)

        elif event_type in ["puppy", "baby"]:
            query = """
                SELECT COUNT(*) FROM message_log 
                WHERE contact_id = (SELECT id FROM contacts_info WHERE username = %s) 
                AND event_type = %s
                AND MONTH(date_sent) = %s AND YEAR(date_sent) = %s
            """
            params = (person_name, event_type, now.month, now.year)

        else:  # nurturing or other future cases
            time_threshold = now - timedelta(days=60)
            query = """
                SELECT COUNT(*) FROM message_log 
                WHERE contact_id = (SELECT id FROM contacts_info WHERE username = %s) 
                AND event_type = %s
                AND date_sent > %s
            """
            params = (person_name, event_type, time_threshold)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0



    def send_msg(self, username_receiver, phone_number, msg):
        try:
            logging.debug(f"📩 Attempting to send message to {username_receiver} at {phone_number}: {msg}")

            base_dir = os.path.dirname(os.path.abspath(__file__))
            session_file_path = os.path.join(base_dir, self.session_file_name)

            client = TelegramClient(session_file_path, self.app_id, self.app_hash)
            client.loop.run_until_complete(client.connect())

            authorized = client.loop.run_until_complete(client.is_user_authorized())
            if not authorized:
                logging.warning(f"⚠️ Session is not authorized. Trying manual login...")

                try:
                    client.loop.run_until_complete(client.start())
                    logging.info("✅ Successfully re-authorized session after reconnect.")

                    # 💤 Give Telegram time to stabilize session
                    time.sleep(5)

                except Exception as auth_error:
                    logging.error(f"❌ Failed to re-authorize session: {auth_error}")
                    return "Session re-authorization failed. Manual intervention needed."

            # Double check after login
            authorized = client.loop.run_until_complete(client.is_user_authorized())
            if not authorized:
                logging.error("❌ Still not authorized after manual login.")
                return "Session not authorized after login."

            # ✅ Retry logic: maximum 2 tries
            for attempt in range(1, 3):  # 1 and 2
                try:
                    logging.debug(f"🚀 Attempt {attempt}: Sending message to {username_receiver}...")
                    client.loop.run_until_complete(client.send_message(phone_number, msg))
                    logging.info(f"✅ Message successfully sent to {username_receiver} on attempt {attempt}.")
                    break  # ✅ Success, exit the loop
                except Exception as send_error:
                    logging.error(f"⚠️ Attempt {attempt} failed to send message to {username_receiver}: {send_error}")
                    if attempt == 1:  # Only wait if we're on the first failure
                        logging.info(f"⏳ Waiting 5 seconds before retrying...")
                        time.sleep(5)
                    else:
                        logging.error(f"❌ Second attempt also failed for {username_receiver}. Giving up.")

        except Exception as e:
            logging.error(f"❌ General error sending message to {username_receiver}: {e}")
            return f"General error sending message to: {username_receiver}, error: {e}"

        finally:
            if 'client' in locals():
                client.disconnect()

        return "Success"





