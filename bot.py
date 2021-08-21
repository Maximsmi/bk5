import telebot   # библитека для работы с telegramm
import os
from boto.telegram.connection import telegramConnection

token = telegramConnection(os.environ['TELEGRAM_TOKEN'])

# Token для телеграмм бота
# token = 'TELEGRAM_TOKEN'
bot = telebot.TeleBot(token)


# Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def ferst_message(message):
    bot.send_message(message.chat.id, "Привет!")


bot.polling(none_stop=True)
