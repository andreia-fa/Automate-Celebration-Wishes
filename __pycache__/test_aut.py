from telethon import TelegramClient
import os

session_path = '/home/almeidandreia/Automate-Celebration-Wishes/andreia_fa.session'
api_id = 25487110  # ← replace
api_hash = '5771967ffe4b4e8168ffeff58c32bc45'  # ← replace

if not os.path.exists(session_path):
    print("❌ Session file does not exist.")
else:
    print("✅ Session file found.")

client = TelegramClient(session_path, api_id, api_hash)
client.connect()

if client.is_user_authorized():
    print("✅ Session is valid and authenticated!")
else:
    print("❌ Session is NOT authenticated. You’ll need to run it manually once to log in.")

client.disconnect()
