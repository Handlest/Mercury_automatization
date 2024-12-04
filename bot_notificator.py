import telebot
import os
from dotenv import load_dotenv

from main import get_reply_and_use

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

bot = telebot.TeleBot(os.environ.get("API_TOKEN"))


def send_message(message, chat_id: str):
    if chat_id is None or chat_id.strip() == "":
        chat_id = "954179273"
    bot.send_message("954179273", message)
    if str(chat_id) != "954179273":
        bot.send_message(chat_id, message)


def send_photo(photo_name: str):
    msg = bot.send_photo(chat_id="954179273", photo=open(f"./{photo_name}", "rb"))
    bot.register_next_step_handler(msg, get_reply_and_use)
