import configparser
import logging
from Automate_birthday_messages import Automate_birthday_messages
from mysql_connection import connect_to_mysql

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_file='config.properties'):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def main():
    try:
        # Load configuration from properties file
        config = load_config()

        # MySQL Configuration
        host = config.get('Database', 'database.url')
        port = config.getint('Database', 'database.port')
        user = config.get('Database', 'database.username')
        password = config.get('Database', 'database.password')
        db = config.get('Database', 'database.db_name')
        contacts_table = config.get('Database', 'database.contacts_table')
        messages_table = config.get('Database', 'database.messages_table')

        # Telegram Configuration
        app_id = config.get('Telegram', 'telegram.api_id')
        app_hash = config.get('Telegram', 'telegram.api_hash')
        session_file_name = config.get('Telegram', 'telegram.session_file_name')

        # Initialize Automate_birthday_messages
        birthday_messenger = Automate_birthday_messages(session_file_name, app_id, app_hash)

        # Connect to MySQL
        mysql_cnx = connect_to_mysql(host, port, user, password, db)

        if mysql_cnx:
            # Get the message to send
            message_to_send = birthday_messenger.should_message_be_send(mysql_cnx, contacts_table, messages_table)
            logging.info(message_to_send)

            # Close the MySQL connection
            mysql_cnx.close()
        else:
            logging.error("Failed to connect to MySQL.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()





'''
from Automate_birthday_messages import Automate_birthday_messages
from mysql_connection import connect_to_mysql
import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Example usage
host = 'localhost'  # Or the IP address of your Docker host
port = 3306  # The exposed port of your MySQL Docker container
user = 'root'
password = 'secretpassword'
db = 'sendlove'
contacts_table = 'contacts_info'
messages_table = 'messages'

# Initialize Automate_birthday_messages
app_id = "25487110"
app_hash = "5771967ffe4b4e8168ffeff58c32bc45"
session_file_name = "andreia_fa"
birthday_messenger = Automate_birthday_messages(session_file_name, app_id, app_hash)

# Connect to MySQL (assuming this is done outside of this class)
mysql_cnx = connect_to_mysql(host, port, user, password, db)

# Get the message to send
message_to_send = birthday_messenger.should_message_be_send(mysql_cnx, contacts_table, messages_table)
logging.info(message_to_send)

# Close the MySQL connection
if mysql_cnx:
    mysql_cnx.close()

'''