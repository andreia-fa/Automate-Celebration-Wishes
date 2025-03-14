import logging
import random
from datetime import datetime, timedelta
from telethon import TelegramClient

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
        
        for name, (event_date, mobile_number, recurrence, event_type) in contacts_with_events.items():
            # 🔥 Fix: Call `get_last_sent_message()` from `sql_connection`
            last_message_text = self.sql_connection.get_last_sent_message(mysql_cnx, name)
            
            # Fetch a message excluding the last sent one
            message_id, celebration_message = self.sql_connection.get_event_message(mysql_cnx, messages_table, event_type, last_message_text)
            
            if celebration_message:
                if not self.has_message_been_sent(mysql_cnx, name, message_id, event_type):
                    # Customize the message
                    customized_message = self.customize_message(
                        celebration_message,
                        name,
                        event_type,
                        event_date
                    )
                    
                    logging.info(f"Sending {event_type} message to {name}. Message: {customized_message}")
                    send_status = self.send_msg(name, mobile_number, customized_message)
                    
                    if send_status == "Success":
                        self.log_message_sent(mysql_cnx, name, customized_message)
                        logging.info(f"Sent {event_type} message to {name}: {customized_message}")
                    else:
                        logging.error(f"Failed to send {event_type} message to {name}")
                else:
                    logging.info(f"{event_type.capitalize()} message (ID: {message_id}) to {name} has already been sent.")
            else:
                logging.error(f"No message found for event type: {event_type}")

        return "Event messages processed."

    def send_nurturing_messages(self, mysql_cnx, messages_table):
        """
        Sends nurturing messages to all contacts who haven't received one in the last two months.
        """
        today = datetime.now()
        cursor = mysql_cnx.cursor()

        # Get all contacts from the contacts table
        query_contacts = "SELECT Username, mobile_number FROM contacts_info"
        cursor.execute(query_contacts)
        contacts = cursor.fetchall()

        # Get a Nurturing message from the messages table
        query_message = f"SELECT text_message FROM {messages_table} WHERE type = 'Nurturing'"
        cursor.execute(query_message)
        nurturing_messages = cursor.fetchall()

        if not nurturing_messages:
            logging.error("No 'Nurturing' messages found in the messages table.")
            return

        for contact in contacts:
            username, mobile_number = contact
            
            # Check if a nurturing message was sent in the last two months
            query_last_sent = """
                SELECT date_sent FROM message_log
                WHERE contact_id = (SELECT id FROM contacts_info WHERE username = %s)
                AND Type = 'Nurturing'
                ORDER BY date_sent DESC
                LIMIT 1
            """
            cursor.execute(query_last_sent, (username,))
            last_sent_result = cursor.fetchone()

            # If a nurturing message was sent within the last two months, skip this contact
            if last_sent_result:
                last_sent_date = last_sent_result[0]
                if last_sent_date > (today - timedelta(days=60)):
                    logging.info(f"Nurturing message for {username} was sent recently, skipping.")
                    continue

            # Randomly choose a nurturing message
            nurturing_message = random.choice(nurturing_messages)[0]

            # Personalize the message with the contact's name
            personalized_message = nurturing_message.replace("(#username#)", username)

            # Send the message using the existing send_msg method from Automate_messages
            send_status = self.send_msg(username, mobile_number, personalized_message)
            
            if send_status == "Success":
                # Log that the message was sent using the existing log_message_sent method
                self.log_message_sent(mysql_cnx, username, personalized_message)
                logging.info(f"Nurturing message sent to {username}.")
            else:
                logging.error(f"Failed to send nurturing message to {username}.")

        cursor.close()

    def customize_message(self, message_template, name, type_, date_str=None):
        """
        Customize message by replacing placeholders.
        """
        # Replace (#username#) placeholder with contact name
        message = message_template.replace('(#username#)', name)
        
        # Replace (#puppy#) or (#baby#) placeholder with the name if applicable
        if type_ == 'puppy':
            message = message.replace('(#puppy#)', name)
        elif type_ == 'baby':
            message = message.replace('(#baby#)', name)
        
        return message

    def has_message_been_sent(self, cnx, person_name, message_id, event_type):
        cursor = cnx.cursor()
        current_year = datetime.now().year
        current_month = datetime.now().month

        logging.debug(f"Checking if a message has been sent for {person_name} ({event_type})")

        # Birthday, Christmas, New Year -> Recurrence every year
        if event_type in ['Birthday', 'Christmas', 'New Year']:
            query = "SELECT COUNT(*) FROM message_log WHERE contact_id = (SELECT id FROM contacts_info WHERE username = %s) AND YEAR(date_sent) = %s"
            params = (person_name, current_year)

        # baby and puppy -> Recurrence every month
        elif event_type in ['baby', 'puppy']:
            query = "SELECT COUNT(*) FROM message_log WHERE contact_id = (SELECT id FROM contacts_info WHERE username = %s) AND YEAR(date_sent) = %s AND MONTH(date_sent) = %s"
            params = (person_name, current_year, current_month)

        else:
            logging.error(f"No message was sent for {person_name} - Event Type: {event_type}")
            return False

        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        cursor.close()

        logging.debug(f"Message sent for {person_name} ({event_type}, message ID: {message_id}): {count}")

        return count > 0

    def send_msg(self, username_receiver, phone_number, msg):
        try:
            logging.debug(f"Attempting to send message to {username_receiver} at {phone_number}: {msg}")

            with TelegramClient(self.session_file_name, self.app_id, self.app_hash) as client:
                client.loop.run_until_complete(client.send_message(phone_number, msg))
                logging.info(f"Message successfully sent to {username_receiver}.")

        except Exception as e:
            logging.error(f"Error sending message to {username_receiver}: {e}")
            return f"Error sending message to: {username_receiver}, error: {e}"
        
        return "Success"
