from telethon import TelegramClient
from datetime import datetime
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(filename)s:%(lineno)d - %(asctime)s - %(levelname)s - %(message)s')

class Automate_messages:
    def __init__(self, session_file_name, app_id, app_hash, sql_connection):
        self.session_file_name = session_file_name
        self.app_id = app_id
        self.app_hash = app_hash
        self.sql_connection = sql_connection  

    def should_event_message_be_sent(self, mysql_cnx, contacts_table, messages_table):
        today_month_day = self.get_today_date_details()
        
        contacts_with_events = self.sql_connection.get_contacts_for_today_events(mysql_cnx, contacts_table, today_month_day)
        if not contacts_with_events:
            logging.info("No contacts with events today.")
            return "No contacts with events today!!!"
        
        for name, (event_date, phone_number, recurrence, event_type) in contacts_with_events.items():
            # Get the last sent message for the user
            last_message_text = self.get_last_sent_message(mysql_cnx, name)
            
            # Fetch a message excluding the last sent one
            message_id, celebration_message = self.sql_connection.get_event_message(mysql_cnx, messages_table, event_type, last_message_text)
            
            if celebration_message:
                if not self.has_message_been_sent(mysql_cnx, name, message_id, event_type):
                    logging.info(f"Sending {event_type} message to {name}. Message: {celebration_message}")
                    send_status = self.send_msg(name, phone_number, celebration_message)
                    if send_status == "Success":
                        self.log_message_sent(mysql_cnx, name, celebration_message)
                        logging.info(f"Sent {event_type} message to {name}: {celebration_message}")
                    else:
                        logging.error(f"Failed to send {event_type} message to {name}")
                else:
                    logging.info(f"{event_type.capitalize()} message (ID: {message_id}) to {name} has already been sent.")
            else:
                logging.error(f"No message found for event type: {event_type}")

        return "Event messages processed."


    def get_today_date_details(self):
        today = datetime.now()
        #today_date_str = today.strftime('%Y-%m-%d')
        #today_day = today.strftime('%d')
        today_month_day = today.strftime('%m-%d')
        return today_month_day

    
    def has_message_been_sent(self, cnx, person_name, message_id, event_type):
        cursor = cnx.cursor()
        current_year = datetime.now().year
        current_month = datetime.now().month
        current_day = datetime.now().day

        logging.debug(f"Checking if a message has been sent for {person_name} ({event_type}) on {current_year}-{current_month}-{current_day}")

        # Birthday, Christmas, New Year -> Recurrence every year
        if event_type in ['Birthday', 'Christmas', 'New Year']:
            query = """
            SELECT COUNT(*)
            FROM message_log
            WHERE Username = %s AND YEAR(date_sent) = %s
            """
            params = (person_name, current_year)
            period = "year"

        # baby and puppy -> Recurrence every month
        elif event_type in ['baby', 'puppy']:
            query = """
            SELECT COUNT(*)
            FROM message_log
            WHERE Username = %s AND YEAR(date_sent) = %s AND MONTH(date_sent) = %s
            """
            params = (person_name, current_year, current_month)
            period = "month"  # Adjust to reflect monthly recurrence

        # nurturing -> Recurrence every two months
        elif event_type == 'nurturing':
            previous_two_months = (current_month - 2) % 12 or 12  # Handle month wrap-around
            query = """
            SELECT COUNT(*)
            FROM message_log
            WHERE Username = %s AND YEAR(date_sent) = %s 
            AND MONTH(date_sent) BETWEEN %s AND %s
            """
            params = (person_name, current_year, previous_two_months, current_month)
            period = "two months"

        else:
            logging.error(f"No message was sent for {person_name} - Event Type: {event_type} on {current_year}-{current_month}-{current_day}")
            return False

        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        cursor.close()

        logging.debug(f"Message sent for {person_name} ({event_type}, message ID: {message_id}): {count}")

        if count > 0:
            logging.info(f"{event_type.capitalize()} message (ID: {message_id}) to {person_name} has already been sent this {period}.")
            return True
        return False

    def log_message_sent(self, cnx, person_name, message_text):
        cursor = cnx.cursor()
        today = datetime.now().strftime('%Y-%m-%d')

        logging.debug(f"Logging message sent for {person_name}")

        # Insert the message text into the message_log table
        query = """
        INSERT INTO message_log (Username, message, date_sent)
        VALUES (%s, %s, %s)
        """
        
        # Execute query with person_name, message_text, and today's date
        cursor.execute(query, (person_name, message_text, today))
        cnx.commit()
        cursor.close()

    
    def get_last_sent_message(self, cnx, person_name):
        """
        Fetch the last message sent to the person from the message_log.
        """
        cursor = cnx.cursor()
        query = """
        SELECT message FROM message_log
        WHERE Username = %s
        ORDER BY date_sent DESC
        LIMIT 1
        """
        try:
            cursor.execute(query, (person_name,))
            result = cursor.fetchone()
            if result:
                return result[0]  # Return the message text
            return None
        except mysql.connector.Error as err:
            logging.error(f"Error fetching last sent message: {err}")
            return None
        finally:
            cursor.close()


    def send_msg(self, username_receiver, Phone_Number, msg):
        try:
            logging.debug(f"Attempting to send message to {username_receiver} at {Phone_Number}: {msg}")

            with TelegramClient(self.session_file_name, self.app_id, self.app_hash) as client:
                client.loop.run_until_complete(client.send_message(Phone_Number, msg))
                logging.info(f"Message successfully sent to {username_receiver}.")

        except Exception as e:
            logging.error(f"Error sending message to {username_receiver}: {e}")
            return f"Error sending message to: {username_receiver}, error: {e}"
        
        return "Success"



