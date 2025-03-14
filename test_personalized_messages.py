import mysql.connector
import configparser
import random
from datetime import datetime

# Load database credentials
config = configparser.ConfigParser()
config.read("config.properties")

db_host = config.get("Database", "database.url")
db_user = config.get("Database", "database.username")
db_password = config.get("Database", "database.password")
db_name = config.get("Database", "database.db_name")

def calculate_months_since(event_date):
    """Calculate the number of months since a given date."""
    if event_date:
        today = datetime.now()
        months = (today.year - event_date.year) * 12 + today.month - event_date.month
        return max(months, 0)  # Ensure we don’t get negative numbers
    return None

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

    # Fetch events and all available messages for each type
    query = """
        SELECT ci.username, ce.event_type, ce.event_date, m.text_message
        FROM contacts_info ci
        JOIN contact_events ce ON ci.id = ce.contact_id
        JOIN messages m ON ce.event_type = m.type
        WHERE DATE_FORMAT(ce.event_date, '%m-%d') = %s
    """
    
    cursor.execute(query, (today_date,))
    results = cursor.fetchall()

    # Store messages by contact and event type
    messages_dict = {}

    for username, event_type, event_date, message_template in results:
        key = (username, event_type)
        if key not in messages_dict:
            messages_dict[key] = []
        messages_dict[key].append((event_date, message_template))

    if messages_dict:
        print("✅ Personalized Messages for Today:")
        for (username, event_type), message_templates in messages_dict.items():
            # Pick a random message from the list
            event_date, selected_message = random.choice(message_templates)
            # Personalize the message with the user's name
            personalized_message = selected_message.replace("{name}", username)

            # If it's a "baby" or "puppy" event, replace {#month_count#}
            if event_type in ["baby", "puppy"]:
                months_since = calculate_months_since(event_date)
                if months_since is not None:
                    personalized_message = personalized_message.replace("#{month_count}", str(months_since))

            print(f"👤 {username} | 🎉 {event_type} | 📩 {personalized_message}")
    else:
        print("ℹ️ No events scheduled for today.")

    cursor.close()
    cnx.close()

except mysql.connector.Error as err:
    print(f"❌ Database query failed: {err}")
