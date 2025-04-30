import mysql.connector
import configparser

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

    # Fetch messages for different event types
    query = "SELECT type, text_message FROM messages"
    
    cursor.execute(query)
    results = cursor.fetchall()

    if results:
        print("✅ Predefined Messages Found:")
        for row in results:
            print(f"🎉 Event Type: {row[0]} | 📩 Message: {row[1]}")
    else:
        print("ℹ️ No predefined messages found.")

    cursor.close()
    cnx.close()

except mysql.connector.Error as err:
    print(f"❌ Database query failed: {err}")