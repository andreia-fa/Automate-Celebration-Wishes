from Automate_celebration_messages import Automate_messages
from celebration_sql_connection import CelebrationSqlConnection
import configparser

# Load config from properties file
config = configparser.ConfigParser()
config.read('config.properties')

# Telegram setup
app_id = config.get('Telegram', 'telegram.api_id')
app_hash = config.get('Telegram', 'telegram.api_hash')
session_file_name = config.get('Telegram', 'telegram.session_file_name')

# Initialize bot
sql_connection = CelebrationSqlConnection()
bot = Automate_messages(session_file_name, app_id, app_hash, sql_connection)

# 🎉 Send message to Marina
result = bot.send_msg(
    "Marina", 
    "00351924387148", 
    "🎈 Even though I'm fashionably late, I couldn’t forget to celebrate Alexandre turning 20 months old! 🧸✨ Wishing you both a day full of love, snuggles, and sweet little surprises. 💕"
)

print("Result:", result)
