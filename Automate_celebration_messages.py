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
        contacts_with_events = self.sql_connection.get_contacts_with_event_types(mysql_cnx, contacts_table)
        if not contacts_with_events:
            logging.info("No contact information available.")
            return "No contact information available."

        today = datetime.now().strftime('%Y-%m-%d')
        today_day = datetime.now().strftime('%d')  # Day for monthly events
        logging.debug(f"Today's date: {today}")
        logging.debug(f"Today's day: {today_day}")

        events_today = []
        for name, (event_date, message_rec, recurrence, event_type) in contacts_with_events.items():
            # Check if event_date is a string and convert it to a datetime object
            if isinstance(event_date, str):
                try:
                    event_date_obj = datetime.strptime(event_date, '%Y-%m-%d')
                except ValueError as e:
                    logging.error(f"Error parsing date for {name}: {e}")
                    continue  # Skip this record if the date format is incorrect
            else:
                event_date_obj = event_date  # If already a datetime object

            event_date_full = event_date_obj.strftime('%Y-%m-%d')
            event_date_day = event_date_obj.strftime('%d')

            logging.debug(f"Checking {name}: Event date: {event_date}, Recurrence: {recurrence}, Event type: {event_type}")

            if recurrence == 'Monthly' and today_day == event_date_day:
                events_today.append((name, message_rec, event_type))
                logging.info(f"Monthly event today for {name}: {event_date}")
            elif recurrence == 'Annual' and today == event_date_full:
                events_today.append((name, message_rec, event_type))
                logging.info(f"Annual event today for {name}: {event_date}")

        if not events_today:
            logging.info("No events today.")
            return "No events today."

        for name, message_rec, event_type in events_today:
            if not self.has_message_been_sent(mysql_cnx, name, event_type):
                celebration_message = self.sql_connection.get_event_message(mysql_cnx, messages_table, event_type)
                if not celebration_message:
                    logging.error(f"No message found for event type: {event_type}")
                    continue

                logging.info(f"Sending {event_type} message to {name}. Message: {celebration_message}")
                send_status = self.send_msg(message_rec, celebration_message)
                if send_status == "Success":
                    self.log_message_sent(mysql_cnx, name, event_type, celebration_message)
                    logging.info(f"Sent {event_type} message to {name}: {celebration_message}")
                else:
                    logging.error(f"Failed to send {event_type} message to {name}")
            else:
                logging.info(f"{event_type.capitalize()} message to {name} has already been sent this year.")

        return "Event messages processed."


    def has_message_been_sent(self, cnx, person_name, event_type):
        cursor = cnx.cursor()
        current_year = datetime.now().year
        query = """
        SELECT COUNT(*)
        FROM message_log
        WHERE Username = %s AND YEAR(date_sent) = %s
        """
        cursor.execute(query, (person_name, current_year))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0

    def log_message_sent(self, cnx, person_name, event_type, message):
        cursor = cnx.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        query = "INSERT INTO message_log (Username, message, date_sent) VALUES (%s, %s, %s)"
        cursor.execute(query, (person_name, message, today))
        cnx.commit()
        cursor.close()

    def send_msg(self, username_receiver, msg):
        try:
            with TelegramClient(self.session_file_name, self.app_id, self.app_hash) as client:

                #loop = asyncio.get_event_loop()
                #coroutine = client.get_entity("+351964395489")
                #username = loop.run_until_complete(coroutine)

                logging.info(f"client: %{username}")


                client.loop.run_until_complete(client.send_message(username_receiver, msg))
                logging.info(f"Message sent to {username_receiver}")
        except Exception as e:
            logging.error(f"Error sending message to {username_receiver}: {e}")
            return f"Error sending message to: {username_receiver}, error: {e}"
        return "Success"


