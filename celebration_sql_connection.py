import mysql.connector
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(filename)s:%(lineno)d - %(asctime)s - %(levelname)s - %(message)s')

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
            
    def get_contacts_with_event_types(self, cnx, table_name):
        if cnx:
            cursor = cnx.cursor()
            query = f"SELECT Username, Message_receiver, Birthday_date, Recurrence, Type FROM {table_name}"
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                contacts_with_events = {}
                
                for row in rows:
                    name = row[0]
                    event_date = row[2].strftime('%Y-%m-%d')
                    message_rec = row[1]
                    recurrence = row[3]
                    event_type = row[4]  # This is the new field added
                    contacts_with_events[name] = (event_date, message_rec, recurrence, event_type)
                    
                cursor.close()
                logging.debug(f"contacts_with_events: {contacts_with_events}")
                return contacts_with_events
            
            except mysql.connector.Error as err:
                logging.error(f"Error executing query: {err}")
                cursor.close()
                return None
        else:
            logging.error("Could not connect to the database")
            return None



            
    def get_event_message(self, cnx, messages_table, event_type):
        if cnx:
            cursor = cnx.cursor()
            query = f"SELECT text_message FROM {messages_table} WHERE Type = %s"
            try:
                cursor.execute(query, (event_type,))
                result = cursor.fetchone()
                if result:
                    ret = result[0]  # Assuming Message is the first column
                    #cursor.close()
                    return ret  
                else:
                    logging.info(f"No message found for event type: {event_type}")
                    return None
            except mysql.connector.Error as err:
                logging.error(f"Error executing query: {err}")
                cursor.close()
                return None
        else:
            logging.error("Could not connect to the database")
            return None



