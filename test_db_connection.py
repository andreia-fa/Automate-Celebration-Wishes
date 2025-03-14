import mysql.connector
import configparser

# Load database credentials from config.properties
config = configparser.ConfigParser()
config.read("config.properties")

db_host = config.get("Database", "database.url")
db_user = config.get("Database", "database.username")
db_password = config.get("Database", "database.password")
db_name = config.get("Database", "database.db_name")

# Try connecting using the correct credentials
try:
    cnx = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    print("✅ Connected successfully!")
    cnx.close()
except mysql.connector.Error as err:
    print(f"❌ Database connection failed: {err}")
