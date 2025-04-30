import mysql.connector
import configparser
from datetime import datetime

# Load database credentials
config = configparser.ConfigParser()
config.read("config.properties")

db_host = config.get("Database", "database.url")
db_user = config.get("Database", "database.username")
db_password = config.get("Database", "database.password")
db_name = config.get("Database", "database.db_name")

try:
    cnx = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = cnx.cursor()

    # Get today's date in MM-DD format
    today_date = datetime.now().strftime('%m-%d')

    # Fetch events scheduled for today
    query = """
        SELECT ci.username, ce.event_type, ce.event_date
        FROM contacts_info ci
        JOIN contact_events ce ON ci.id = ce.contact_id
        WHERE DATE_FORMAT(ce.event_date, '%m-%d') = %s
    """
    
    cursor.execute(query, (today_date,))
    results = cursor.fetchall()

    if results:
        print("✅ Events found for today:")
        for row in results:
            print(f"👤 {row[0]} | 🎉 Event: {row[1]} | 📅 Date: {row[2]}")
    else:
        print("ℹ️ No events scheduled for today.")

    cursor.close()
    cnx.close()

except mysql.connector.Error as err:
    print(f"❌ Database query failed: {err}")
