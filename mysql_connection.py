import mysql.connector
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_mysql(host, port, user, password, db):
    try:
        cnx = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db
        )
        logging.info("Successfully connected to the MySQL database")
        return cnx
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to MySQL database: {err}")
        return None