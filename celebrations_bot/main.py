import configparser
import logging
from Automate_celebration_messages import Automate_messages
from celebration_sql_connection import CelebrationSqlConnection

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(filename)s:%(lineno)d - %(asctime)s - %(levelname)s - %(message)s')

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
        messages_table = config.get('Database', 'database.messages_table')

        # Telegram Configuration
        app_id = config.get('Telegram', 'telegram.api_id')
        app_hash = config.get('Telegram', 'telegram.api_hash')
        session_file_name = config.get('Telegram', 'telegram.session_file_name')

        # Connect to MySQL
        mysql_cnx = CelebrationSqlConnection.connect_to_mysql(host, port, user, password, db)

        # Initialize Automate_messages
        automate_messages = Automate_messages(session_file_name, app_id, app_hash, CelebrationSqlConnection())

        if mysql_cnx:
            # 🔥 Fix: Removed `today_month_day` from function call
            contacts_with_events = automate_messages.sql_connection.get_contacts_for_today_events(mysql_cnx)

            if contacts_with_events:
                message_to_send = automate_messages.should_event_message_be_sent(mysql_cnx, messages_table)
                logging.info(message_to_send)

                # Send nurturing messages
                automate_messages.send_nurturing_messages(mysql_cnx, messages_table)
            else:
                logging.info("No events scheduled for today.")

            # Close the MySQL connection
            mysql_cnx.close()
        else:
            logging.error("Failed to connect to MySQL.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()