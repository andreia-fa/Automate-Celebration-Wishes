import mysql.connector
import logging
import random

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
            
    def get_contacts_for_today_events(self, cnx, table_name, today_month_day):
        if not cnx:
            logging.error("Could not connect to the database")
            return None

        cursor = cnx.cursor()
        query = f"""
        SELECT Username, Phone_Number, Birthday_date, Recurrence, Type 
        FROM {table_name}
        WHERE (Recurrence = 'Monthly' AND DATE_FORMAT(Birthday_date, '%d') = %s)
        OR (Recurrence = 'Annual' AND DATE_FORMAT(Birthday_date, '%m-%d') = %s)
        OR (Type IN ('Christmas', 'New Year'))
        """
        # Extract the day part for the 'Monthly' condition and the month-day part for the 'Annual' condition
        today_day = today_month_day[-2:]  # Extract 'dd' for Monthly
        today_month_day_formatted = today_month_day  # Full 'mm-dd' format for Annual
        try:
            cursor.execute(query, (today_day, today_month_day_formatted))
            rows = cursor.fetchall()
            contacts_with_events = {}
            
            for row in rows:
                name, phone_number, event_date, recurrence, event_type = row
                event_date_str = event_date.strftime('%Y-%m-%d') if event_date else None
                contacts_with_events[name] = (event_date_str, phone_number, recurrence, event_type)
            
            logging.debug(f"contacts_with_events: {contacts_with_events}")
            return contacts_with_events

        except mysql.connector.Error as err:
            logging.error(f"Error executing query: {err}")
            return None

        finally:
            cursor.close()

     
    import random

    def get_event_message(self, cnx, messages_table, event_type, last_message_text):
        """
        Fetch a random message for the given event type, excluding the last sent message.
        """
        if cnx:
            cursor = cnx.cursor(buffered=True)
            query = f"SELECT id, text_message FROM {messages_table} WHERE Type = %s"
            try:
                cursor.execute(query, (event_type,))
                results = cursor.fetchall()
                
                # Filter out the last sent message
                filtered_results = [result for result in results if result[1] != last_message_text]

                if filtered_results:
                    # Randomly select a message from the filtered list
                    selected_message = random.choice(filtered_results)
                    message_id = selected_message[0]
                    message_text = selected_message[1]
                    return message_id, message_text
                else:
                    logging.info(f"No alternative message found for event type: {event_type}")
                    return None, None
            except mysql.connector.Error as err:
                logging.error(f"Error executing query: {err}")
                return None, None
            finally:
                cursor.close()
        else:
            logging.error("Could not connect to the database")
            return None, None






