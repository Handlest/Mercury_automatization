import telebot
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

bot = telebot.TeleBot(os.environ.get("API_TOKEN"))

def send_message(message):
    bot.send_message(os.environ.get("MY_CHAT_ID"), message)
    # bot.send_message(os.environ.get("MY_MOM_CHAT_ID"), message)
