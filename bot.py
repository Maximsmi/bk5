import telebot   # библитека для работы с telegramm
import os

# Token для телеграмм бота
# token = 'TELEGRAM_TOKEN'
#bot = telebot.TeleBot('t_token_bk5')
print (os.environ.get('TELEGRAM_TOKEN', none))

# Обрабатываем команду /start
#@bot.message_handler(commands=['start'])
#def ferst_message(message):
#    bot.send_message(message.chat.id, "Привет!")


#bot.polling(none_stop=True)
