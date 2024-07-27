import mysql.connector
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CelebrationSqlConnection:

    def __init__(self):
        pass
    
    def connect_to_mysql(host, port, user, password, db):
        try:
            cnx = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db
            )
            logging.info(" Successfully connected to the MySQL database")
            return cnx
        except mysql.connector.Error as err:
            logging.error(f"Error connecting to MySQL database: {err}")
            return None        

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
            
    def get_celebration_messages(cnx, messages_table):
        if cnx:
            cursor = cnx.cursor()
            query = f"SELECT text_message FROM {messages_table} WHERE type = 'birthday'"
            try:
                cursor.execute(query)
                messages = cursor.fetchall()
                cursor.close()
                if messages:
                    logging.debug(f"Celebration messages: {messages}")
                    return messages
                else:
                    logging.info("No celebration messages found.")
                    return None
            except mysql.connector.Error as err:
                logging.error(f"Error executing query: {err}")
                cursor.close()
                return None
        else:
            logging.error("Could not connect to the database")
            return None

