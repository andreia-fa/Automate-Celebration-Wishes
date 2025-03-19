import mysql.connector
import datetime
import logging
import os
import pprint

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# ✅ Load database configuration from config.properties
config = {}

config_file_path = os.path.join(os.path.dirname(__file__), "config.properties")

if not os.path.exists(config_file_path):
    logging.error(f"❌ Configuration file not found: {config_file_path}")
    exit(1)

with open(config_file_path, "r") as file:
    for line in file:
        line = line.strip()
        if "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

# ✅ Retrieve values from config BEFORE using them
db_host = config.get("database.url", "localhost")
db_port = int(config.get("database.port", 3306))
db_user = config.get("database.username", "root")
db_password = config.get("database.password", "")
db_name = config.get("database.db_name", "celebrations_bot_db")
contacts_table = config.get("database.contacts_table", "contacts_info")
messages_table = config.get("database.messages_table", "messages")

try:
    # ✅ Connect to the database AFTER defining `db_host`
    cnx = mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database=db_name
    )
    logging.info("✅ Successfully connected to the database.")

    cursor = cnx.cursor()

    # ✅ Fetch user-specific events
    query = f"""
    SELECT * from {contacts_table};
    """


    
    cursor.execute(query)
    rows = cursor.fetchall()  # ✅ Now `rows` is correctly defined

    # ✅ Debugging: Check if rows are fetched
    logging.debug(f"🔍 SQL Query Returned: {len(rows)} rows")

    # ✅ Convert SQL results into a list
    contacts_with_events = []
    for row in rows:
        contacts_with_events.append({
            "username": row[0],
            "mobile": row[1],
            "category": row[2],
            "event_date": row[3],
            "recurrence": row[4],
            "event_type": row[5],
        })

    # ✅ Debugging: Check if contacts are collected
    logging.debug(f"📌 User-specific events collected: {contacts_with_events}")

    # ✅ Add global events dynamically
    global_events = [
        {"event_type": "christmas", "month": 12, "day": 25, "category": "person"},
        {"event_type": "new_year", "month": 12, "day": 31, "category": "person"}
    ]

    today = datetime.datetime.today()

    # ✅ Debugging: Check today's date
    logging.debug(f"📅 Today's Date: {today.strftime('%Y-%m-%d')}")

    for event in global_events:
        if event["month"] == today.month and event["day"] == today.day:
            logging.debug(f"🎉 Adding global event: {event['event_type']}")
            for contact in contacts_with_events:
                if contact["category"] == event["category"]:
                    contacts_with_events.append({
                        "username": contact["username"],
                        "mobile": contact["mobile"],
                        "category": contact["category"],
                        "event_date": None,  # Global events don't have a specific date
                        "recurrence": "annual",
                        "event_type": event["event_type"],
                    })

    # ✅ Debugging: Show the final contacts with events
    logging.info(f"✅ Final List of Contacts with Events:")
    pprint.pprint(contacts_with_events)

except mysql.connector.Error as err:
    logging.error(f"❌ Database error: {err}")

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'cnx' in locals() and cnx.is_connected():
        cnx.close()
        logging.info("🔌 Database connection closed.")
