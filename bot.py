import telebot   # библитека для работы с telegramm
from telebot import types

# Token для телеграмм бота
token = 'TELEGRAM_TOKEN'

# Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id, 'Меня зовут бот. Чем могу вам помочь?')


bot.polling(none_stop=True)
