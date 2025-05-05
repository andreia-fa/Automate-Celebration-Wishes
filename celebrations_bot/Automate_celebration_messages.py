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
        
        for name, (event_date, mobile_number, category, event_type) in contacts_with_events.items():

            # 🔥 NEW: Fetch event_type dynamically from category
            event_type = self.sql_connection.get_event_type(mysql_cnx, name)
            
            # Fetch the last sent message
            last_message_text = self.sql_connection.get_last_sent_message(mysql_cnx, name)
            
            # Fetch a message excluding the last sent one
            message_id, celebration_message = self.sql_connection.get_event_message(mysql_cnx, messages_table, event_type, last_message_text)
            
            if celebration_message:
                if not self.has_message_been_sent(mysql_cnx, name, event_type):
                    # Customize the message
                    customized_message = self.customize_message(celebration_message, name, event_type, event_date)
                    
                    logging.info(f"Sending {event_type} message to {name}. Message: {customized_message}")
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
        Sends nurturing messages to a limited number of 'person' contacts who haven't
        received any messages in the last 60 days and are not celebrating anything today.
        """

        today = datetime.now().date()
        cursor = mysql_cnx.cursor()

        # Daily message cap
        DAILY_NURTURING_LIMIT = 2
        sent_count = 0
        sent_numbers = set()

        # 1️⃣ Fetch all 'person' contacts
        query_contacts = "SELECT id, username, mobile_number, birthday_date, category FROM contacts_info WHERE category = 'person'"
        cursor.execute(query_contacts)
        contacts = cursor.fetchall()

        # Shuffle to avoid same sequence daily
        random.shuffle(contacts)

        # 2️⃣ Load nurturing messages
        query_message = f"SELECT id, text_message FROM {messages_table} WHERE type = 'nurturing'"
        cursor.execute(query_message)
        nurturing_messages = cursor.fetchall()

        if not nurturing_messages:
            logging.error("❌ No nurturing messages found in the database.")
            return

        for contact in contacts:
            contact_id, username, mobile_number, birthday_date, category = contact

            logging.debug(f"👀 Evaluating: {username} (ID {contact_id}) — {mobile_number}")

            # Skip if daily limit reached
            if sent_count >= DAILY_NURTURING_LIMIT:
                logging.info("🛑 Daily nurturing limit reached — stopping.")
                break

            # Skip if birthday is today
            if birthday_date and birthday_date.month == today.month and birthday_date.day == today.day:
                logging.info(f"🎂 {username} has a birthday today. Skipping nurturing.")
                continue

            # Check if any message was sent to this contact recently
            query_last_sent = """
                SELECT date_sent FROM message_log
                WHERE contact_id = %s
                ORDER BY date_sent DESC LIMIT 1
            """
            cursor.execute(query_last_sent, (contact_id,))
            last_sent = cursor.fetchone()

            if last_sent:
                last_sent_date = last_sent[0].date()
                if last_sent_date > (today - timedelta(days=60)):
                    logging.info(f"⏩ Skipping {username}, message already sent within 60 days.")
                    continue

            # Pick and personalize a message
            message_id, template = random.choice(nurturing_messages)
            personalized = self.customize_message(template, username, "nurturing", birthday_date)

            # Send message
            send_status = self.send_msg(username, mobile_number, personalized)

            if send_status == "Success":
                self.sql_connection.log_message_sent(
                    mysql_cnx, username, "nurturing", message_id, personalized
                )
                sent_count += 1
                sent_numbers.add(mobile_number)
                logging.info(f"✅ Nurturing message sent to {username}")
            else:
                logging.error(f"❌ Failed to send nurturing message to {username}")

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





