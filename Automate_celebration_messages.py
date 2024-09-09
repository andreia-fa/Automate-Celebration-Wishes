from telethon import TelegramClient
from datetime import datetime, timedelta
import asyncio
import logging
import random


# Configure loggingcustomize_message

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
                    # Customize the message
                    personal_relationship = self.get_personal_relationship(mysql_cnx, name, contacts_table)
                    customized_message = self.customize_message(
                        celebration_message,
                        name,
                        event_type,
                        event_date
                    )
                    
                    logging.info(f"Sending {event_type} message to {name}. Message: {customized_message}")
                    send_status = self.send_msg(name, phone_number, customized_message)
                    
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

    def send_nurturing_messages(mysql_cnx, contacts_table, messages_table, birthday_messenger):
        """
        Sends nurturing messages to all contacts who haven't received one in the last two months.
        """
        today = datetime.now()
        cursor = mysql_cnx.cursor()

        # Get all contacts from the contacts table
        query_contacts = f"SELECT Username, Phone_Number FROM {contacts_table}"
        cursor.execute(query_contacts)
        contacts = cursor.fetchall()

        # Get a Nurturing message from the messages table
        query_message = f"SELECT text_message FROM {messages_table} WHERE Type = 'Nurturing'"
        cursor.execute(query_message)
        nurturing_messages = cursor.fetchall()

        if not nurturing_messages:
            logging.error("No 'Nurturing' messages found in the messages table.")
            return

        for contact in contacts:
            username, phone_number = contact
            
            # Check if a nurturing message was sent in the last two months
            query_last_sent = """
                SELECT date_sent FROM message_log
                WHERE Username = %s AND Type = 'Nurturing'
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
            send_status = birthday_messenger.send_msg(username, phone_number, personalized_message)
            
            if send_status == "Success":
                # Log that the message was sent using the existing log_message_sent method
                birthday_messenger.log_message_sent(mysql_cnx, username, personalized_message)
                logging.info(f"Nurturing message sent to {username}.")
            else:
                logging.error(f"Failed to send nurturing message to {username}.")

        cursor.close()

    def calculate_months_since(self, date_str):
            """Calculate the number of months since a given date."""
            try:
                birth_date = datetime.strptime(date_str, '%Y-%m-%d')
                today = datetime.now()
                months = (today.year - birth_date.year) * 12 + today.month - birth_date.month
                return months
            except ValueError:
                return None
            

    def customize_message(self, message_template, name, type_, date_str=None):
        """
        Customize message by replacing placeholders.

        :param message_template: The message template with placeholders.
        :param name: The name to replace (#username#) placeholder.
        :param personal_relationship: The personal relationship to replace (#username#) placeholder.
        :param type_: Type of message, used to replace (#puppy#) or (#baby#) placeholder.
        :param date_str: Date string used to calculate months for (#monthplaceholder#).
        :return: Customized message.
        """
        # Replace (#username#) placeholder with personal relationship
        message = message_template.replace('(#username#)', name)
        
        # Replace (#puppy#) or (#baby#) placeholder with the name if applicable
        if type_ == 'puppy':
            message = message.replace('(#puppy#)', name)
        elif type_ == 'baby':
            message = message.replace('(#baby#)', name)
        
        # Replace (#monthplaceholder#) with the number of months followed by "months"
        if date_str:
            months = self.calculate_months_since(date_str)
            if months is not None:
                message = message.replace('(#monthplaceholder#)', f"{months} months")
            else:
                message = message.replace('(#monthplaceholder#)', 'unknown months')
        
        return message


    def get_personal_relationship(self, cnx, person_name, table_name):
        """Fetch personal relationship for a given person from the contact table."""
        cursor = cnx.cursor()
        query = f"SELECT Personal_relationship FROM {table_name} WHERE Username = %s"
        try:
            cursor.execute(query, (person_name,))
            result = cursor.fetchone()
            if result:
                return result[0]
            return "Friend"  # Default value if not found
        except mysql.connector.Error as err:
            logging.error(f"Error fetching personal relationship: {err}")
            return "Friend"
        finally:
            cursor.close()

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



