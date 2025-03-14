import mysql.connector
import configparser

# Load database credentials
config = configparser.ConfigParser()
config.read("config.properties")

db_host = config.get("Database", "database.url")
db_user = config.get("Database", "database.username")
db_password = config.get("Database", "database.password")
db_name = config.get("Database", "database.db_name")

# Set an event type to test (change this to test different event types)
event_type_to_test = "birthday"  # Change to "puppy", "baby", etc.

try:
    cnx = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = cnx.cursor()

    # Fetch a message for the given event type
    query = "SELECT text_message FROM messages WHERE type = %s LIMIT 1"
    
    cursor.execute(query, (event_type_to_test,))
    result = cursor.fetchone()

    if result:
        print(f"✅ Message for {event_type_to_test}: {result[0]}")
    else:
        print(f"ℹ️ No predefined message found for event type: {event_type_to_test}")

    cursor.close()
    cnx.close()

except mysql.connector.Error as err:
    print(f"❌ Database query failed: {err}")
