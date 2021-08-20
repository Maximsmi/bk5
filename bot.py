import telebot   # библитека для работы с telegramm
from telebot import types

# import boto
# from boto.s3.connection import S3Connection
# s3 = S3Connection(os.environ['TELEGRAM_TOKEN'])

# Token для телеграмм бота
# token = ''
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id, 'Меня зовут бот. Чем могу вам помочь?')


bot.polling(none_stop=True)
