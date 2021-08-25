import telebot   # библитека для работы с telegramm
import os

from os import environ
from dotenv import load_dotenv

load_dotenv()
environ.get('t_token_bk5')

# Token для телеграмм бота
# token = 'TELEGRAM_TOKEN'
#bot = telebot.TeleBot('t_token_bk5')
print('t_token_bk5')

# Обрабатываем команду /start
#@bot.message_handler(commands=['start'])
#def ferst_message(message):
#    bot.send_message(message.chat.id, "Привет!")


#bot.polling(none_stop=True)
