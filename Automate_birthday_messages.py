from telethon import TelegramClient
from datetime import datetime
from mysql_connection import connect_to_mysql
import mysql.connector
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Automate_birthday_messages:
    def __init__(self, session_file_name, app_id, app_hash):
        self.session_file_name = session_file_name
        self.app_id = app_id
        self.app_hash = app_hash

    def execute_select_query_and_return_dict_results(self, cnx, table_name):
        if cnx:
            cursor = cnx.cursor()
            query = f"SELECT Username, Birthday_date FROM {table_name}"
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                dict_results = {}
                
                for row in rows:
                    name = row[0]
                    date_str = row[1].strftime('%Y-%m-%d')
                    dict_results[name] = date_str
                cursor.close()
                logging.debug(f"dict_results: {dict_results}")

                return dict_results
            
            except mysql.connector.Error as err:
                logging.error(f"Error executing query: {err}")
                cursor.close()
                return None
        else:
            logging.error("Could not connect to the database")
            return None

    def should_message_be_send(self, mysql_cnx, contacts_table, messages_table):
        dict_results = self.execute_select_query_and_return_dict_results(mysql_cnx, contacts_table)
        
        if not dict_results:
            return "No contact information available."

        today = datetime.now().strftime('%Y-%m-%d')
        birthdays_today = [name for name, birth_date in dict_results.items() if birth_date == today]

        if not birthdays_today:
            return "No birthdays today."

        cursor = mysql_cnx.cursor()
        cursor.execute(f"SELECT text_message FROM {messages_table} WHERE type = 'birthday'")
        birthday_messages = cursor.fetchall()

        if not birthday_messages:
            cursor.close()
            return "No birthday messages found."

        birthday_message = birthday_messages[0][0]

        for name in birthdays_today:
            if not self.has_message_been_sent(mysql_cnx, name):
                send_status = self.send_msg(name, birthday_message)
                if send_status == "Success":
                    self.log_message_sent(mysql_cnx, name, birthday_message)
                    logging.info(f"Sent birthday message to {name}: {birthday_message}")
                else:
                    logging.error(f"Failed to send birthday message to {name}")
            else:
                logging.info(f"Birthday message to {name} has already been sent this year.")

        cursor.close()
        return "Birthday messages processed."

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
