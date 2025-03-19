import mysql.connector
import logging
import random
from datetime import datetime

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
            logging.info("✅ Successfully connected to the MySQL database")
            return cnx
        except mysql.connector.Error as err:
            logging.error(f"❌ Error connecting to MySQL database: {err}")
            return None        

    def execute_select_query_and_return_dict_results(self, cnx, table_name):
        if cnx:
            cursor = cnx.cursor()
            query = f"SELECT username, birthday_date FROM {table_name}"
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
                dict_results = {row[0]: row[1].strftime('%Y-%m-%d') for row in rows if row[1]}
                cursor.close()
                logging.debug(f"🔍 Dict results: {dict_results}")
                return dict_results
            except mysql.connector.Error as err:
                logging.error(f"❌ Error executing query: {err}")
                cursor.close()
                return None
        else:
            logging.error("❌ Could not connect to the database")
            return None
            
    def get_contacts_for_today_events(self, cnx):
        if not cnx:
            logging.error("❌ Could not connect to the database")
            return None

        cursor = cnx.cursor()
        query = """
        SELECT c.username, c.mobile_number, c.category,  e.event_date, e.recurrence, e.event_type
        FROM contacts_info c
        JOIN contact_events e ON c.id = e.contact_id
        WHERE 
            (e.recurrence = 'monthly' AND DAY(e.event_date) = DAY(NOW()))
            OR (e.recurrence = 'annual' AND MONTH(e.event_date) = MONTH(NOW()) AND DAY(e.event_date) = DAY(NOW()))
            OR e.event_type IN ('Christmas', 'New Year')
        """
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            contacts_with_events = {
                row[0]: (row[3].strftime('%Y-%m-%d') if row[3] else None, row[1], row[4], row[5]) for row in rows
            }
            logging.debug(f"📅 Contacts with events today: {contacts_with_events}")
            return contacts_with_events
        except mysql.connector.Error as err:
            logging.error(f"❌ Error executing query: {err}")
            return None
        finally:
            cursor.close()

    
    def get_event_type(self, cnx, contact_id):
        """
        Determines the event type based on the contact's category.
        """
        cursor = cnx.cursor()
        query = "SELECT category FROM contacts_info WHERE id = %s"
        try:
            cursor.execute(query, (contact_id,))
            category = cursor.fetchone()
            if category:
                if category[0] == "puppy":
                    return "puppy"
                elif category[0] == "baby":
                    return "baby"
                else:
                    return "birthday"
            else:
                return "birthday"  # Default for persons
        except mysql.connector.Error as err:
            logging.error(f"❌ Error fetching category: {err}")
            return "birthday"  # Fallback default
        finally:
            cursor.close()


    def get_event_message(self, cnx, messages_table, event_type, last_message_text):
        if cnx:
            cursor = cnx.cursor(buffered=True)
            query = f"SELECT id, text_message FROM {messages_table} WHERE type = %s"
            try:
                cursor.execute(query, (event_type,))
                results = cursor.fetchall()
                filtered_results = [result for result in results if result[1] != last_message_text]

                if filtered_results:
                    selected_message = random.choice(filtered_results)
                    return selected_message[0], selected_message[1]
                else:
                    logging.info(f"⚠️ No alternative message found for event type: {event_type}")
                    return None, None
            except mysql.connector.Error as err:
                logging.error(f"❌ Error executing query: {err}")
                return None, None
            finally:
                cursor.close()
        else:
            logging.error("❌ Could not connect to the database")
            return None, None

    def get_last_sent_message(self, cnx, person_name):
        cursor = cnx.cursor()
        query = """
        SELECT sent_message FROM message_log
        WHERE contact_id = (SELECT id FROM contacts_info WHERE username = %s)
        ORDER BY date_sent DESC
        LIMIT 1
        """
        try:
            cursor.execute(query, (person_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except mysql.connector.Error as err:
            logging.error(f"❌ Error fetching last sent message: {err}")
            return None
        finally:
            cursor.close()

    def log_message_sent(self, cnx, person_name, event_type, message_id, message_text):
        cursor = cnx.cursor()
        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 1️⃣ Check event_type Before INSERT
        if not event_type:
            logging.error("🚨 event_type is missing! Skipping log insertion.")
            return

        # 2️⃣ Validate event_type Before INSERT
        if not isinstance(event_type, str):
            logging.error(f"🚨 event_type is not a string! Received: {type(event_type)} - {event_type}")
            return

        # 3️⃣ Double-Check the event_type Data Source
        valid_event_types = {'birthday', 'puppy', 'baby', 'christmas', 'new year'}
        if event_type.lower() not in valid_event_types:
            logging.warning(f"⚠️ Unrecognized event_type: '{event_type}'. Double-check data source.")

        # 4️⃣ Check for Encoding Issues
        try:
            event_type.encode('utf-8')
        except UnicodeEncodeError as e:
            logging.error(f"🚨 Encoding issue detected in event_type: {e}")
            return

        # Ensure event_type does not exceed the database column limit
        if len(event_type) > 50:
            logging.warning(f"🚨 event_type '{event_type}' too long! Trimming to 50 characters.")
            event_type = event_type[:50]

        query = """
        INSERT INTO message_log (contact_id, message_id, sent_message, event_type, date_sent, status)
        VALUES (
            (SELECT id FROM contacts_info WHERE username = %s), 
            %s, %s, %s, %s, 'sent'
        )
        """
        try:
            # Extra logging before execution
            logging.debug(f"⚠️ FINAL INSERT VALUES:")
            logging.debug(f"   Username: {person_name}")
            logging.debug(f"   MessageID: {message_id}")
            logging.debug(f"   EventType: '{event_type}' (Length: {len(event_type)})")
            logging.debug(f"   Sent Message: '{message_text}' (Length: {len(message_text)})")

            cursor.execute(query, (person_name, message_id, event_type, message_text, today))
            cnx.commit()
            logging.info(f"✅ Message logged for {person_name}, Event: {event_type}")

        except Exception as e:
            logging.error(f"❌ Error logging message: {e}")
        finally:
            cursor.close()
