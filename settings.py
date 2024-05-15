import os
from dotenv import load_dotenv

load_dotenv()
bot_token = os.getenv('BOT_TOKEN', "No token found")
bot_prefix = os.getenv('BOT_PREFIX', "!")

# App Settings
app_host = os.getenv('APP_HOST', "127.0.0.1")
app_port = int(os.getenv('APP_PORT', 7600))

# flask webhook settings
webhook_url = os.getenv('WEBHOOK_URL', "No webhook found")
webhook_login = os.getenv('WEBHOOK_LOGIN', "No webhook found")
webhook_logout = os.getenv('WEBHOOK_LOGOUT', "No webhook found")
webhook_respawn = os.getenv('WEBHOOK_RESPAWN', "No webhook found")
webhook_killed = os.getenv('WEBHOOK_KILLED', "No webhook found")
webhook_admincommand = os.getenv('WEBHOOK_ADMINCOMMAND', "No webhook found")
webhook_adminspectate = os.getenv('WEBHOOK_ADMINSPECTATE', "No webhook found")
webhook_playerchat = os.getenv('WEBHOOK_PLAYERCHAT', "No webhook found")
webhook_playerdamage = os.getenv('WEBHOOK_PLAYERDAMAGE', "No webhook found")
webhook_playerreport = os.getenv('WEBHOOK_PLAYERREPORT', "No webhook found")
webhook_playerleave = os.getenv('WEBHOOK_PLAYERLEAVE', "No webhook found")
webhook_waystone = os.getenv('WEBHOOK_WAYSTONE', "No webhook found")
webhook_questcomplete = os.getenv('WEBHOOK_QUESTCOMPLETE', "No webhook found")
webhook_questfailed = os.getenv('WEBHOOK_QUESTFAILED', "No webhook found")
# webhook_restart = os.getenv('WEBHOOK_RESTART', "No webhook found")