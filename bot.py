import telebot   # библитека для работы с telegramm
import os

token = 'TELEGRAM_TOKEN'

# Token для телеграмм бота
# token = 'TELEGRAM_TOKEN'
bot = telebot.TeleBot(token)


# Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def ferst_message(message):
    bot.send_message(message.chat.id, "Привет!")


bot.polling(none_stop=True)
