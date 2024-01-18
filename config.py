import os
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv('BOT_TOKEN', "No token found")
bot_prefix = os.getenv('BOT_PREFIX', "!")
bot_status = os.getenv('BOT_STATUS', "the Server")
footer = os.getenv('FOOTER', 'Path of Titans Bot')
version = os.getenv('VERSION', 'v1.0.0')