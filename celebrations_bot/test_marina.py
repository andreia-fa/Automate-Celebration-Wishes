import configparser
import logging
import time
import os
from Automate_celebration_messages import Automate_messages
from celebration_sql_connection import CelebrationSqlConnection

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load config from properties file
config = configparser.ConfigParser()
config.read('../config.properties')  # Assuming script is inside celebrations_bot/

# Telegram setup
app_id = config.get('Telegram', 'telegram.api_id')
app_hash = config.get('Telegram', 'telegram.api_hash')
session_file_name = config.get('Telegram', 'telegram.session_file_name')

# Initialize bot
sql_connection = CelebrationSqlConnection()
bot = Automate_messages(session_file_name, app_id, app_hash, sql_connection)

# ✅ SEND TEST MESSAGE TO MIMI
result = bot.send_msg(
    "Mimi",
    "004915127926917",
    "🎈 Thought I’d drop in with some love today — hope everything’s going beautifully for you and Viaan. 💕"
)

print("Result:", result)
