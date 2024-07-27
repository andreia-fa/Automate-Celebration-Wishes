from telethon import TelegramClient
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Automate_messages:
    def __init__(self, session_file_name, app_id, app_hash, sql_connection):
        self.session_file_name = session_file_name
        self.app_id = app_id
        self.app_hash = app_hash
        self.sql_connection = sql_connection

    def should_birthday_message_be_send(self, mysql_cnx, contacts_table, messages_table):
        dict_results = self.sql_connection.execute_select_query_and_return_dict_results(mysql_cnx, contacts_table)
        if not dict_results:
            return "No contact information available."

        today = datetime.now().strftime('%Y-%m-%d')
        birthdays_today = [name for name, birth_date in dict_results.items() if birth_date == today]

        if not birthdays_today:
            return "No birthdays today."

        celebration_messages = self.sql_connection.get_celebration_messages(mysql_cnx, messages_table)
        if not celebration_messages:
            return "No celebration messages found."

        celebration_message = celebration_messages[0][0]

        for name in birthdays_today:
            if not self.has_message_been_sent(mysql_cnx, name):
                send_status = self.send_msg(name, celebration_message)
                if send_status == "Success":
                    self.log_message_sent(mysql_cnx, name, celebration_message)
                    logging.info(f"Sent celebration message to {name}: {celebration_message}")
                else:
                    logging.error(f"Failed to send celebration message to {name}")
            else:
                logging.info(f"Celebration message to {name} has already been sent this year.")

        return "Celebration messages processed."

    def has_message_been_sent(self, cnx, person_name):
        cursor = cnx.cursor()
        current_year = datetime.now().year
        query = "SELECT COUNT(*) FROM message_log WHERE Username = %s AND YEAR(date_sent) = %s"
        cursor.execute(query, (person_name, current_year))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0

    def log_message_sent(self, cnx, person_name, message):
        cursor = cnx.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        query = "INSERT INTO message_log (Username, message, date_sent) VALUES (%s, %s, %s)"
        cursor.execute(query, (person_name, message, today))
        cnx.commit()
        cursor.close()

    def send_msg(self, username_receiver, msg):
        try:
            with TelegramClient(self.session_file_name, self.app_id, self.app_hash) as client:
                client.loop.run_until_complete(client.send_message(username_receiver, msg))
                logging.info(f"Message sent to {username_receiver}")
        except Exception as e:
            logging.error(f"Error sending message to {username_receiver}: {e}")
            return f"Error sending message to: {username_receiver}, error: {e}"
        return "Success"


