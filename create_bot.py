import telebot
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)