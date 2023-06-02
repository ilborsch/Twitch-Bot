from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(raise_error_if_not_found=True))

TMI_TOKEN = os.environ.get('TMI_TOKEN')
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
BOT_NAME = os.environ.get('BOT_NAME')
BOT_PREFIX = os.environ.get('BOT_PREFIX')
DOTA_PLAYER_ID = os.environ.get('DOTA_PLAYER_ID')
VK = os.environ.get('VK')
INSTAGRAM = os.environ.get('INSTAGRAM')
STEAM = os.environ.get('STEAM')
DONATE = os.environ.get('DONATE')
