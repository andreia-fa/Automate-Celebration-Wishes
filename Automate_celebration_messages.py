import logging
import random
from datetime import datetime, timedelta
from telethon import TelegramClient
import os



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
        """ Sends nurturing messages to all contacts who haven't received one in the last two months,
        and are not receiving a birthday message today.
        Only sends messages to persons (not puppies or babies). """

        today = datetime.now().date()
        cursor = mysql_cnx.cursor()

        # Get all contacts of type 'person'
        query_contacts = "SELECT id, Username, mobile_number, birthday_date FROM contacts_info WHERE category = 'person'"
        cursor.execute(query_contacts)
        contacts = cursor.fetchall()

        # Get a list of nurturing messages
        query_message = f"SELECT id, text_message FROM {messages_table} WHERE type = 'nurturing'"
        cursor.execute(query_message)
        nurturing_messages = cursor.fetchall()

        if not nurturing_messages:
            logging.error("❌ No 'nurturing' messages found in the messages table.")
            return

        for contact in contacts:
            contact_id, username, mobile_number, birthday_date = contact

            # 1️⃣ Skip if today is their birthday
            if birthday_date and birthday_date.month == today.month and birthday_date.day == today.day:
                logging.info(f"🎂 {username} has a birthday today. Skipping nurturing message.")
                continue

            # 2️⃣ Skip if a nurturing message was sent recently
            query_last_sent = """
                SELECT date_sent FROM message_log
                WHERE contact_id = %s AND event_type = 'nurturing'
                ORDER BY date_sent DESC LIMIT 1
            """
            cursor.execute(query_last_sent, (contact_id,))
            last_sent_result = cursor.fetchone()

            if last_sent_result:
                last_sent_date = last_sent_result[0].date()
                if last_sent_date > (today - timedelta(days=60)):
                    logging.info(f"⚠️ Nurturing message for {username} was sent recently, skipping.")
                    continue

            # Select and personalize a message
            message_id, message_text = random.choice(nurturing_messages)
            personalized_message = message_text.replace("{name}", username)

            # Send message
            send_status = self.send_msg(username, mobile_number, personalized_message)

            if send_status == "Success":
                self.sql_connection.log_message_sent(
                    mysql_cnx, username, "nurturing", message_id, personalized_message
                )
                logging.info(f"✅ Nurturing message sent to {username}.")
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
        today = datetime.now().date()

        logging.debug(f"Checking if a message has been sent today for {person_name} ({event_type})")

        query = """
        SELECT COUNT(*) FROM message_log 
        WHERE contact_id = (SELECT id FROM contacts_info WHERE username = %s) 
        AND event_type = %s
        AND DATE(date_sent) = %s
        """
        params = (person_name, event_type, today)

        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        cursor.close()

        return count > 0


    def send_msg(self, username_receiver, phone_number, msg):
        try:
            logging.debug(f"📩 Attempting to send message to {username_receiver} at {phone_number}: {msg}")

            # Dynamically build absolute path to session file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            session_file_path = os.path.join(base_dir, self.session_file_name)

            with TelegramClient(session_file_path, self.app_id, self.app_hash) as client:
                client.loop.run_until_complete(client.send_message(phone_number, msg))
                logging.info(f"✅ Message successfully sent to {username_receiver}.")

        except Exception as e:
            logging.error(f"❌ Error sending message to {username_receiver}: {e}")
            return f"Error sending message to: {username_receiver}, error: {e}"
        
        return "Success"

