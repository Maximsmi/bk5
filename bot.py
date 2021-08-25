# Подключаем библиотеки
import sqlite3   # библиотека баз данных
import telebot   # библитека для работы с telegramm
import re
import time


from os import environ
from dotenv import load_dotenv

load_dotenv()
token = environ.get('TELEGRAM_TOKEN')

# Token для телеграмм бота
# token = 'TELEGRAM_TOKEN'
#bot = telebot.TeleBot(token)
#print(token)

# Token для телеграмм бота
bot = telebot.TeleBot(token)

# подключаемся к базе данных подпищиков
connection = sqlite3.connect("./db/database_id.db", check_same_thread=False)
cursor = connection.cursor()

# массив для хранения ID сообщений для авторизированого пользователя
cursor.execute('''CREATE TABLE IF NOT EXISTS menu_user_id (\
                                                            user_id INT PRIMARY KEY,\
                                                            menu_id TEXT,\
                                                            keyword TEXT);''')

# массив для хранения сообщений от пользователей для совета дома и дмина
cursor.execute('''CREATE TABLE IF NOT EXISTS user_to_admin (\
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                            user_id TEXT,\
                                                            from_id TEXT,\
                                                            date TEXT,\
                                                            text TEXT);''')

# массив для хранения сообщений от совета дома и дмина для пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS user_to_admin (\
                                                            id INTEGER PRIMARY KEY AUTOINCREMENT,\
                                                            user_id TEXT,\
                                                            from_id TEXT,\
                                                            date TEXT,\
                                                            text TEXT);''')

# массив для хранения ID сообщений для авторизированого пользователя
cursor.execute('''CREATE TABLE IF NOT EXISTS message_id ( \
                        id_n INTEGER PRIMARY KEY AUTOINCREMENT,\
                        date TEXT,\
                        user_id TEXT,\
                        mess_id TEXT,\
                        text TEXT);''')

# массив для хранения ID сообщений для неавторизированого пользователя
cursor.execute('''CREATE TABLE IF NOT EXISTS users_green ( \
                        id_n INTEGER PRIMARY KEY AUTOINCREMENT,\
                        user_id TEXT,\
                        send_user_id TEXT,\
                        mess_id TEXT,\
                        user_name TEXT,\
                        user_surname TEXT,\
                        text TEXT);''')

# проверяем есть ли таблица в базе, если нет то создаем
cursor.execute('''CREATE TABLE IF NOT EXISTS users ( \
                        user_id INT PRIMARY KEY,\
                        user_name TEXT,\
                        user_surname TEXT,\
                        username TEXT,\
                        user_kv TEXT,\
                        phonenumber TEXT);''')

# проверяем есть ли база, если нет то создаем
#  id - id записи в базе,
#  mess_id - id сообщения
#  content_type - тип сообщения
#  user_id - данный о юзере
#  user_first_name - данные о юзере
#  user_username - данные о юзере
#  user_last_name - данные о юзере
#  date - ????
#  mess_text - текст сообщения  
cursor.execute('''CREATE TABLE IF NOT EXISTS messages( id INT PRIMARY KEY,\
                        mess_id TEXT,\
                        content_type TEXT,\
                        user_id TEXT,\
                        user_first_name TEXT,\
                        user_username TEXT,\
                        user_last_name TEXT,\
                        date TEXT,\
                        mess_text TEXT);''')

# проверяем есть ли таблица в базе, если нет то создаем
# таблица стандартного текста для ответов
cursor.execute('''CREATE TABLE IF NOT EXISTS mess ( id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, text TEXT, group_id TEXT, description TEXT);''')

connection.commit()

# процедура занесения данных о пользователе в базу данных
# таблица сообщений не зарегистрированного пользователя
# id: str   -  номер автоматический,
# title: str   -  переменная,
# text: str -  текст,
# group: str - группа,
# description: str  -  описание
def read_text_mess (title: str):
    cursor.execute("SELECT * FROM mess WHERE title = ?", [(title)])
    records = cursor.fetchone()
    print(records)  # выводим все значения таблицы на экран
    return (records)

# процедура занесения данных о пользователе в базу данных
# таблица сообщений не зарегистрированного пользователя
# id: str   -  номер автоматический,
# title: str   -  переменная,
# text: str -  текст,
# group: str - группа,
# description: str  -  описание
#def mess_to_user (title: str):
#    cursor.execute("SELECT * FROM mess WHERE title = ?", [(title)])
#    records = cursor.fetchone()
#    print(records)  # выводим все значения таблицы на экран
#    return (records)


# процедура занесения данных о пользователе в базу данных
# таблица сообщений не зарегистрированного пользователя
# user_id: str   -  id пользователя,
# mess_id: str   -  id сообщения пользователя,
# user_name: str -  имя пользователя,
# user_surname: str - фамилия пользователя,
# text: str  -  текст
def db_table_val_users_green (user_id: str, send_user_id: str,  mess_id: str, user_name:str, user_surname:str, text:str):
    cursor.execute("INSERT INTO users_green ( user_id, send_user_id, mess_id, user_name, user_surname, text) VALUES (?,?,?,?,?,?);",\
                       (user_id, send_user_id, mess_id, user_name, user_surname, text))
    connection.commit() # сохраняем изменения в таблице
    cursor.execute("SELECT * FROM users_green ")  # Выбираем все значения в таблице
    print(cursor.fetchall())  # выводим все значения таблицы на экран

# процедура занесения данных о пользователе в базу данных
# таблица сообщений не зарегистрированного пользователя
# user_id: str   -  id пользователя,
# mune_id: str   -  id меню,
# keyword: str   -  ключевое слово
# flag - 1:добавить пользователя; 2: изменить menu_id; 3: удалить пользователя
def db_table_menu_user_id (user_id: str, menu_id: str, keyword: str, flag: int):
    print ("")
    print ("db_table_menu_user_id:")
    print (" > user_id: ", user_id)
    print (" > menu_id: ", menu_id)
    print (" > keyword: ", keyword)
    print (" > flag: ", flag)
    if flag == 1:
        sql = "SELECT * FROM menu_user_id WHERE user_id = ?"
        cursor.execute(sql, [(user_id)])
        records = cursor.fetchone()
        menu_id = 1
        if (records == None):
            cursor.execute("INSERT INTO menu_user_id ( user_id, menu_id, keyword) VALUES (?,?,?);", (user_id, menu_id, keyword))
            print ("    >> добавление в базу menu_user_id: ", user_id, "  menu_id: ", menu_id, "  keyword: ", keyword)
        else:
            sql = """UPDATE menu_user_id SET menu_id = ? WHERE user_id = ?, keyword = ? """
            cursor.execute(sql, (menu_id, user_id, keyword))
            print ("    >> Пользователь есть в базе menu_user_id! Настройки сброшены!")
    elif flag == 2:
        sql = "SELECT * FROM menu_user_id WHERE user_id = ?"
        cursor.execute(sql, [(user_id)])
        records = cursor.fetchone()
        if not (records == None):
            sql = """UPDATE menu_user_id SET menu_id = ?, keyword = ? WHERE user_id = ?"""
            cursor.execute(sql, (menu_id, keyword,  user_id))
            print ("    >> в таблице menu_user_id! Изменены данные: ",user_id,",  menu_id: " ,menu_id,",  keyword: " ,keyword)
    elif flag == 3:
        sql = "DELETE FROM menu_user_id WHERE user_id = ?"
        cursor.execute(sql, [(user_id)])
        print ("    >> в таблице menu_user_id! Удалены данные пользователя: ",user_id)
   
    connection.commit() # сохраняем изменения в таблице    

# процедура занесения данных о пользователе в базу данных
# таблица сообщений не зарегистрированного пользователя
# user_id: str   -  id пользователя,
# mess_id: str   -  id сообщения пользователя,
def db_table_message_id (date:str, user_id: str, mess_id: str, text: str):
    cursor.execute("INSERT INTO message_id ( date, user_id, mess_id, text) VALUES (?,?,?,?);", (date, user_id, mess_id, text))
    connection.commit() # сохраняем изменения в таблице    

def db_table_message_id_dell (user_id: str):
    sql = "SELECT * FROM message_id WHERE user_id = ?"
    cursor.execute(sql, [(user_id)])
    records = cursor.fetchall()
    for row in records:
        print("Delete  ->  ID:", row[2], "  mess_id:", row[3], "  test: " ,row[4])
        bot.delete_message(row[2], row[3])   # удалим ранее присланые сообщения, т.к. пользователь отказался далее использовать бота
        sql = "DELETE FROM message_id WHERE mess_id = ?"
        cursor.execute(sql, [(row[3])])

    connection.commit() # сохраняем изменения в таблице    
    

# процедура занесения данных о пользователе в базу данных
# Таблица зарегистрированных пользователей
# user_id  -  id пользователя,
# user_name  -  имя пользователя,
# user_surname  -  фамилия пользователя,
# username  -  никнэййм пользователя,
# user_kv  -  номер квартиры пользоваателя,
# phonenumber  -  номер телефона пользователя
def db_table_val (user_id: int, user_name: str, user_surname: str, username: str, user_kv: str, phonenumber: str):
    cursor.execute("INSERT INTO users ( user_id,\
                                        user_name,\
                                        user_surname,\
                                        username,\
                                        user_kv,\
                                        phonenumber) VALUES (?, ?, ?, ?, ?, ?);", \
                                        (user_id, user_name, user_surname, username, user_kv, phonenumber))           
    connection.commit()
    cursor.execute("SELECT * FROM users ")
    print(cursor.fetchall())

# процедура занесения данных о сообщениях в базу данных
def db_table_val_mess (mess_id: str, content_type: str,\
                  user_id: str, user_first_name: str,\
                  user_username: str, user_last_name: str,\
                  date: str, mess_text: str,):
    cursor.execute("INSERT INTO messages (  id,\
                                            mess_id,\
                                            content_type,\
                                            user_id,\
                                            user_first_name,\
                                            user_username,\
                                            user_last_name,\
                                            date,\
                                            mess_text) VALUES (?,?,?,?,?,?,?,?,?);", \
    ( id, mess_id, content_type, user_id, user_first_name,user_username,user_last_name, date, mess_text))
    connection.commit()
    cursor.execute("SELECT * FROM messages ")
    print(cursor.fetchone())


unknown_text: str = "Ничего не понятно, но очень интересно.\nПопробуй команду /help"

#  Ответ на любое неожидаемое сообщение"""
#@bot.message_handler()
#async def unknown_message(message):
#     await message.answer(msg.unknown_text, reply_markup=s.MAIN_KB)

# Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def ferst_message(message):
    
    print ("Яляется ли пользователь ботом = ", message.from_user.is_bot)
    if not(message.from_user.is_bot):  # Проверяем является ользователь ботом или нет
        # проверяем есть ли пользователь в базе зарегистрированных
        sql = "SELECT * FROM users WHERE user_id = ?"
        cursor.execute(sql, [(message.from_user.id)])
        records = cursor.fetchone()
        print ("message.from_user.id = ", message.from_user.id)
        print ("Есть ли пользователь в базе = ", records)
        if not (records == None):
            print ("К боту присоединился: ", records [1], " ", records [2], " из квартиры: ", records [4])
            welcome_message (message)
        else:
            start_message (message)

# Обрабатываем команду /stop
@bot.message_handler(commands=['stop'])
def stop_message(message):
    print ("Яляется ли пользователь ботом = ", message.from_user.is_bot)
    bot.send_message(message.chat.id, "Раздел находиться в разработке!")
 
#if not(message.from_user.is_bot):  # Проверяем является ользователь ботом или нет
        # проверяем есть ли пользователь в базе зарегистрированных
    #    sql = "SELECT * FROM users WHERE user_id = ?"
    #    cursor.execute(sql, [(message.from_user.id)])
        #print ("message.from_user.id = ", message.from_user.id)
    #    records = cursor.fetchone()
    #    print ("От бота отключился ", records[1], " ", records[2], " из квартиры: ", records [4])
       # exit(0)
        #handler_state(False)
        #client.disconnect()
# -------------------------------- Отправка группового сообщения----------------------------------------------------    
# --------------------------------КОНЕЦ - Отправка группового сообщения----------------------------------------------------    

# -------------------------------- Обрабатываем команду /help ----------------------------------------------------    

# Обрабатываем команду /help
@bot.message_handler(commands=['help'])
def help_message(message):
    print("")
    print("help_message(message):")
    print (" < < message: ", message)
    user_id = message.from_user.id  # id пользователя
    text = message.text
    print ("  >> user_id: ", user_id, "  text: ", text)
    print ("  >> Яляется ли пользователь ботом: ", message.from_user.is_bot)
    if not (message.from_user.is_bot):  # Проверяем является ользователь ботом или нет
        #bot.send_message(message.chat.id, "Раздел находиться в разработке!")
    
        # проверка есть ли пользователь в списке админив или нет
        sql = "SELECT * FROM admin_table WHERE id_user = ?"  # находим в таблице меню список пунктов 
        cursor.execute(sql, [(user_id)]) #, {"row_id": from_mess})
        records_id = cursor.fetchone()
        print ("  >> records_id: ", records_id)
        # проверка есть ли пользователь в списке зарегистрированных 
        sql = "SELECT * FROM users WHERE user_id = ?"  # находим в таблице меню список пунктов 
        cursor.execute(sql, [(user_id)]) #, {"row_id": from_mess})
        records_user = cursor.fetchone()
        print ("  >> records_user: ", records_user)
        if not (records_id == None):
            print ("    >> Пользователь присутствует в базе админов!")
            sql = "SELECT * FROM command_bot WHERE admin = 'true'"  # находим в таблице меню список пунктов 
            cursor.execute(sql)
            records_com = cursor.fetchall()
            print ("  >> /help >> команды:" )
            text = ""
            for row in records_com:
                print ("    >>  - ", row)
                text = text + str(row[1]) + " " + row[2] + "\n"
            print ("  >> text:" , text)
            res = bot.send_message(user_id, 'Список доступных Вам команд:\n'+text, reply_markup=telebot.types.ReplyKeyboardRemove())
            print (" > >  message: ", res)
            print ("  >> user_id: ", res.chat.id, "  text:", res.text)
        elif not (records_user == None):
            print ("    >> Пользователь присутствует в базе пользователей!")
            sql = "SELECT * FROM command_bot WHERE user = 'true'"  # находим в таблице меню список пунктов 
            cursor.execute(sql)
            records_com = cursor.fetchall()
            print ("  >> /help >> команды:" )
            text = ""
            for row in records_com:
                print ("    >>  - ", row)
                text = text + str(row[1]) + " " + row[2] + "\n"
            print ("  >> text:" , text)
            res = bot.send_message(user_id, 'Список доступных Вам команд:\n'+text, reply_markup=telebot.types.ReplyKeyboardRemove())
            print (" > >  message: ", res)
            print ("  >> user_id: ", res.chat.id, "  text:", res.text)
        else:
            print ("    >> Пользователь не подключен к боту!")
            res = bot.send_message(user_id, 'Вам доступна комманда: /start', reply_markup=telebot.types.ReplyKeyboardRemove())
            print (" > >  message: ", res)
            print ("  >> user_id: ", res.chat.id, "  text:", res.text)

            
            

            
# --------------------------------КОНЕЦ - Обрабатываем команду /help ---------------------------------------------    


# -------------------------------- Отправка группового сообщения----------------------------------------------------    
# Обрабатываем команду /mess - отправка сообщений всем пользователям
@bot.message_handler(commands=['mess'])
def send_all_message(message):
    print("")
    print("send_all_message(message):")
    print (" < < message: ", message)
    user_id = message.from_user.id  # id пользователя
    text = message.text
    print ("  >> user_id: ", user_id, "  text: ", text)
    print ("  >> Яляется ли пользователь ботом: ", message.from_user.is_bot)
    if not (message.from_user.is_bot):  # Проверяем является ользователь ботом или нет
        #bot.send_message(message.chat.id, "Раздел находиться в разработке!")
    
        # проверка есть ли пользователь в списке админив или нет
        sql = "SELECT * FROM admin_table WHERE id_user = ?"  # находим в таблице меню список пунктов 
        cursor.execute(sql, [(user_id)]) #, {"row_id": from_mess})
        records_id = cursor.fetchone()
        print ("  >> records_id: ", records_id)
        if not (records_id == None):
            print ("    >> Пользователь присутствует в базе админов!")
                # поинтересуемся у пользователя, действительно хочет отправить сообщение всем!
            keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            keyboard.add(telebot.types.KeyboardButton ("Да"), telebot.types.KeyboardButton ("Нет"))                
            #keyboard.add(telebot.types.KeyboardButton ("Нет"))                
            res = bot.send_message(message.chat.id, 'Вы точно хотите отпраить сообщение всем пользователям?', reply_markup=keyboard)
            print (" > >  message: ", res)
            print ("  >> user_id: ", res.chat.id, "  text:", res.text)
            bot.register_next_step_handler(res , mess_true)
        else:
            res = bot.send_message(message.chat.id,\
                               'У Вас нет польномочий отправлять сообщения пользователям! Обратитесь к Администраторам!',\
                               reply_markup=telebot.types.ReplyKeyboardRemove())
            print (" > >  message: ", res)
            print ("  >> user_id: ", res.chat.id, "  text:", res.text)
            db_table_menu_user_id (user_id=message.chat.id, menu_id=1, keyword = "", flag=2) #сбрасываем индекс меню пользователя в default
            user_menu (message,"")

# Определяем ответ пользователя на вопрос
def mess_true(message):
    print ("")
    print ("mess_true(message): ")
    print (" < < message: ", message)
    user_id = message.from_user.id  # id пользователя
    text = message.text
    print ("  >> user_id: ", user_id, "  text:", text)
    if (text == "Да"):
        print ("    >> Приглашение ввести текст для пользователей!")
        res = bot.send_message(message.chat.id, 'Введите текст, который хотите отправить пользователям:', reply_markup=telebot.types.ReplyKeyboardRemove())
        print (" > >  message: ", res)
        print ("  >> user_id: ", res.chat.id, "  text:", res.text)
        bot.register_next_step_handler(res , mess_true_text) # ждем набора текста и отправляем
    else: # (text == "Нет"):
        db_table_menu_user_id (user_id=message.chat.id, menu_id=1, keyword = "", flag=2) #сбрасываем индекс меню пользователя в default
        user_menu (message,"")
    
# Рассылка текста пользователям от админов
def mess_true_text(message):
    print ("")
    print ("mess_true_text(message): ")
    print (" < < message: ", message)
    user_id = message.from_user.id  # id пользователя
    text = message.text
    print ("  >> user_id: ", user_id, "  text:", text)
    # Определим от чьего имени отправим текст
    sql = "SELECT * FROM admin_table WHERE id_user = ?"  # находим в таблице меню список пунктов 
    cursor.execute(sql, [(user_id)]) #, {"row_id": from_mess})
    records_id = cursor.fetchone()
    print ("  >> records_id: ", records_id)

    sql = "SELECT * FROM admin_table WHERE id_user = '0'"  # находим в таблице меню список пунктов 
    cursor.execute(sql) #, {"row_id": from_mess})
    records_data = cursor.fetchone()
    print ("  >> records_data: ", records_data)
    
    i: int = 0
    for row in records_id:
        if row == "true":
            user_sdmin_id = i
            print ("    >> отправитель: " + str (user_sdmin_id) + ",  row: " + str(row) + ",  data: " + str(records_data[i]))
            break
        i = i+1
    
    sql = "SELECT user_id FROM users"  # находим в таблице меню список пунктов 
    cursor.execute(sql) #, {"row_id": from_mess})
    records_users = cursor.fetchall()
    print ("  >> records_data: ", records_users)
    text = text + "\nС уважением, " + str(records_data[i]) + "!"
    print ("text: ", text)
    # Рассылка сообщений пользователям
    i=0
    for row in records_users:
        print ("    >> Отправка сообщения пользователю: ", row[0])
        res = bot.send_message(row[0], text, reply_markup=telebot.types.ReplyKeyboardRemove())
        print (" > >  message: ", res)
        i=i+1
        print ("\n  >> Отправлено: ", i ," сообщений!")
    # Уведомление что сообщение разослано
    res = bot.send_message(user_id, "Ваше сообщение разослано!", reply_markup=telebot.types.ReplyKeyboardRemove())
    print (" > >  message: ", res)
# --------------------------------КОНЕЦ - Отправка группового сообщения----------------------------------------------------    
    

# Обрабатываем команду /dell
@bot.message_handler(commands=['dell'])
def dell_user(message):
    user_id = message.from_user.id
    print ("")
    print ("dell_user:")
    print (" > user_id: ", user_id)
    sql = "DELETE FROM users WHERE user_id = ?"
    cursor.execute(sql, [(user_id)])
    connection.commit()
    sql = "DELETE FROM users_green WHERE user_id = ?"
    cursor.execute(sql, [(user_id)])
    connection.commit()

    print ("    >> в таблице users! Удалены данные пользователя: ",user_id)    
    db_table_menu_user_id (user_id, 0, "", 3) # добавляем индекс меню пользователя в базу
    bot.send_message(message.chat.id, 'Вы покинули чат и ваша запись стерта из базы!',  reply_markup=telebot.types.ReplyKeyboardRemove())
    print (' >>> !!!  Пользователь: ',user_id,' удалился из базы! !!! <<< ')
 
# Обрабатываем команду /start
#@bot.message_handler(commands=['start'])

def welcome_message(message):
    # Узнаем имя пользователя
    db_table_message_id (date=message.date, user_id = message.chat.id, mess_id = message.message_id, text = message.text)
    us_name = message.from_user.first_name
    us_sname = message.from_user.last_name
    usname = message.from_user.last_name
     # Печатаем приветственный текст для пользователя.
    text: str = read_text_mess("start_welcome") #'С возвращением, ' + us_name
    text_2 = re.sub(r'(?i)us_name(?=\W)', us_name, text[2])
    res = bot.send_message(message.chat.id, text_2, reply_markup=telebot.types.ReplyKeyboardRemove()) #'Добро пожаловать, ' us_name ' ' us_sname)
    db_table_message_id (date=res.date, user_id = message.chat.id, mess_id = res.message_id, text = res.text)
    print(message.chat.id)
    db_table_menu_user_id (user_id=message.chat.id, menu_id=1, keyword = "", flag=2) #сбрасываем индекс меню пользователя в default
    user_menu (message,"")

def start_message(message):
    # Узнаем имя пользователя
    us_name = message.from_user.first_name
    us_sname = message.from_user.last_name
    usname = message.from_user.username
     # Печатаем приветственный текст для пользователя.
    text: str = read_text_mess("start_new_id") #'Добро пожаловать, ' + us_name + '. Вы хотите подключиться ' +\
    text_2 = re.sub(r'(?i)us_name(?=\W)', us_name, text[2])
    
    db_table_val_users_green ( message.from_user.id,\
                                message.from_user.id,\
                                message.message_id,\
                                message.from_user.first_name,\
                                message.from_user.last_name,\
                                message.text)    
    res = bot.send_message(message.chat.id, text_2, reply_markup=telebot.types.ReplyKeyboardRemove()) #'Добро пожаловать, ' us_name ' ' us_sname)
    print (res)
    db_table_val_users_green ( message.from_user.id,\
                              res.from_user.id,\
                              res.message_id,\
                              res.from_user.first_name,\
                              res.from_user.last_name,\
                              res.text)    

    
    # Создаем 2 кнопки с принятием решения
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row (telebot.types.InlineKeyboardButton ('> ввести № квартиры', callback_data = 'get-yes'))
    keyboard.row (telebot.types.InlineKeyboardButton ('> не согласен с условиями! Пока! ', callback_data = 'get-no'))
    
   # db_table_val_mess_green ( message.from_user.id, message.message_id)    
    res = bot.send_message ( message.chat.id, 'Выберите ответ:', reply_markup=keyboard )
    db_table_val_users_green ( message.from_user.id,\
                              res.from_user.id,\
                              res.message_id,\
                              res.from_user.first_name,\
                              res.from_user.last_name,\
                              res.text)    

# Обрабатываем ответ пользователя
@bot.callback_query_handler (func=lambda call: True)
def iq_callback(query):
    data = query.data
    print (query)
    print (data)
    
    if data.startswith ('get-'):
        get_answer_start (query)
    elif data.startswith ('kv-'):
        get_answer_kv (query)
    elif data.startswith ('menu-'):
        get_answer_menu (query)
        
# функция ответа пользователю если он не зарегистрирован еще
def get_answer_start (query):
    bot.answer_callback_query(query.id)
    print (query.id)
    # если пользователь согласился предоставить данные, то заносим его в базу
    if query.data[4:] == 'yes':
        #dell_message (query)
        dell_message (query.message)
        res = bot.send_message ( query.message.chat.id, 'Отлично!' )
        # Создаем клавиатуру с цифрами для набора номера кв.
        #keyboard = telebot.types.ReplyKeyboardMarkup()
        #keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        #keyboard.row('Привет', 'Пока')
        
        #res = bot.send_message ( query.message.chat.id , 'Отлично! Теперь введите № квартиры:') #, reply_markup=keyboard)
        #print (res)
        db_table_val_users_green ( query.from_user.id,\
                              res.from_user.id,\
                              res.message_id,\
                              res.from_user.first_name,\
                              res.from_user.last_name,\
                              res.text)
        type_nomber_kv (res)
         # db_table_val_mess_green ( message.from_user.id, message.message_id)    
  
    # Если пользователь отказывается от использования бота, то удаляем все ранее присланые сообщения.
    elif query.data[4:] == 'no':
        dell_message (query.message)
        res = bot.send_message ( query.message.chat.id, 'Жаль. До скорой встречи!' )
        db_table_val_users_green ( query.from_user.id,\
                              res.from_user.id,\
                              res.message_id,\
                              res.from_user.first_name,\
                              res.from_user.last_name,\
                              res.text)

        res = bot.send_message ( query.message.chat.id, 'воспользуйтесь меню или /start' )
        db_table_val_users_green ( query.from_user.id,\
                              res.from_user.id,\
                              res.message_id,\
                              res.from_user.first_name,\
                              res.from_user.last_name,\
                              res.text)

def type_nomber_kv (message):
    res = bot.send_message ( message.chat.id, 'Теперь введите № квартиры: '); #, reply_markup=keyboard )
    db_table_val_users_green ( message.chat.id,\
                               res.from_user.id,\
                               res.message_id,\
                               res.from_user.first_name,\
                               res.from_user.last_name,\
                               res.text)
    bot.register_next_step_handler(res , kv)

def kv(message):
    kv = message.text
    db_table_val_users_green ( message.chat.id,\
                               message.from_user.id,\
                               message.message_id,\
                               message.from_user.first_name,\
                               message.from_user.last_name,\
                               message.text)

    if kv.isdigit():  # проверяем являеться ли числом введеное значение
        kv_2 = int(kv)
        print ("Номер квартиры: ", kv)
        if (kv_2 > 0) and (kv_2 < 753):
            dell_message (message)
            bot.send_message ( message.chat.id, ' Вы ввели № квартиры - ' + kv )
            # добавляем пользователя в базу 
           
            us_id = message.from_user.id
            us_name = message.from_user.first_name
            us_sname = message.from_user.last_name
            username = message.from_user.username
            
            print ("id = ", us_id)
            print ("first_name = ", us_name)
            print ("last_name = ", us_sname)
            print ("username = ", username)
            print ("kv = ", kv)
         
            sql = """SELECT * FROM users WHERE user_id=?"""
            cursor.execute(sql, [(us_id)])
            res = cursor.fetchone()
            print(res) # or use fetchone()
            
            if (res == None):
                db_table_val( user_id=us_id,\
                              user_name=us_name,\
                              user_surname=us_sname,\
                              username = username,\
                              user_kv = kv, phonenumber = "")
            bot.send_message(message.chat.id, 'Отлично! Вы зарегистрированы в базе.')
            
            keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_phone = telebot.types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
            #button_geo = telebot.types.KeyboardButton(text="Отправить местоположение", request_location=True)
            otkaz = telebot.types.KeyboardButton ('нет, не хочу!')
            keyboard.add(button_phone, otkaz)
            res = bot.send_message(message.chat.id, "Не хотите поделиться своим номером телефона?", reply_markup=keyboard)
            db_table_val_users_green ( message.chat.id,\
                                               res.from_user.id,\
                                               res.message_id,\
                                               res.from_user.first_name,\
                                               res.from_user.last_name,\
                                               res.text)

        else:
            dell_message (message)
            print ("Введен не корректный номер квартиры")
            res = bot.send_message ( message.chat.id, ' Вы указали неверный номер квартиры. Попробуйте еще.' )
            db_table_val_users_green ( message.chat.id,\
                               res.from_user.id,\
                               res.message_id,\
                               res.from_user.first_name,\
                               res.from_user.last_name,\
                               res.text)

            type_nomber_kv (res)
    else:
        dell_message (message)
        print ("Введен не корректный номер квартиры")
        res = bot.send_message ( message.chat.id, ' Вы указали неверный номер квартиры. Воспользуйтесь коммандой: /start.' )
        db_table_val_users_green ( message.chat.id,\
                               res.from_user.id,\
                               res.message_id,\
                               res.from_user.first_name,\
                               res.from_user.last_name,\
                               res.text)

def get_answer_menu (message):
    db_table_message_id_dell (user_id = message.from_user.id)
    print (message.data[5:])
    print (message)
    sql = "SELECT * FROM menu_user WHERE keyword = ?"  # находим в таблице юзера
    cursor.execute(sql, [(message.data[5:])])
    records = cursor.fetchone()
    text = records[4]
    print ("menu_user: ", records)
    sql = """UPDATE menu_user_id SET menu_id = ? WHERE user_id = ?"""
    cursor.execute(sql, (records[5], message.from_user.id))
    connection.commit()

    sql = "SELECT * FROM menu_user_id WHERE user_id = ?"  # находим в таблице юзера
    cursor.execute(sql, [(message.from_user.id)])
    records = cursor.fetchone()
    print ("Пользователь: ", records[0], "  вошел в меню:", records[1])
    user_id = records[0]
    menu_id = records[1]
    
    sql = "SELECT * FROM menu_user WHERE group_id = ?"  # находим в таблице юзера
    cursor.execute(sql, [(menu_id)])
    records = cursor.fetchall()
    print (records)
    print (len (records))
    keyboard = telebot.types.InlineKeyboardMarkup()
    for row in records:
        if row[7] == "1": # проверяем включено ли меню
            print ("info = ", row[1])
            # Создаем кнопки с принятием решения
            keyboard.row (telebot.types.InlineKeyboardButton (text=row[1], callback_data = 'menu-'+row[2]))
    # выводим кнопки на экран
    #user_menu (message)
    res = bot.send_message ( message.from_user.id, text, reply_markup=keyboard )
    print(res)
    db_table_message_id (date= res.date, user_id = res.chat.id, mess_id = res.message_id, text= res.text)

#bot.send_message(message.chat.id,'You send me message')

def dell_message (result):
    #bot.delete_message(query.message.chat.id, query.message.message_id)
    print ('user_id = ', result.chat.id)
    sql = "SELECT * FROM users_green WHERE user_id=?"
    cursor.execute(sql, [(result.chat.id)])
    #print(cursor.fetchall()) # or use fetchone()
    records = cursor.fetchall()
    print(records)
    print("Всего строк:  ", len(records))
    for row in records:
        print("Delete  ->  ID:", row[1], "  mess_id:", row[3])
        bot.delete_message(row[1], row[3])   # удалим ранее присланые сообщения, т.к. пользователь отказался далее использовать бота
        sql = "DELETE FROM users_green WHERE mess_id = ?"
        cursor.execute(sql, [(row[3])])
        
    connection.commit()
    #bot.send_message ( query.message.chat.id, 'Жаль. До скорой встречи!' )
    #bot.send_message ( query.message.chat.id, 'воспользуйтесь меню или /start' )

# функция ответа пользователю при вводе № квартиры
def get_answer_kv (query):
    bot.answer_callback_query(query.id)

    user_id_kv = query.from_user.id
    message_id_kv = query.message.message_id
    reply_markup_kv = query.message.reply_markup
    print("Rename  ->  ID:", user_id_kv, "  mess_id:", message_id_kv)

    text = query.message.text
    print(text)
    

            
@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        bot.send_message(message.chat.id, 'Вы успешно отправили свой номер', reply_markup=telebot.types.ReplyKeyboardRemove())
  
        phonenumber = str(message.contact.phone_number)
        user_id = str(message.contact.user_id)
        print ("phonenumber = ", phonenumber)
        print ("user_id =", user_id)
        
        db_table_menu_user_id (user_id=message.from_user.id, menu_id=1, keyword = "", flag=1) # добавляем индекс меню пользователя в базу

        #sql = "SELECT * FROM users WHERE user_id=?"
        #cursor.execute(sql, user_id)
        #print(cursor.fetchone()) # or use fetchone()
 
        sql = """UPDATE users SET phonenumber = ? WHERE user_id = ?"""
        #cur.execute(sql, (nicjname, record_id))
        cursor.execute(sql, (phonenumber, user_id))
        connection.commit()
        #global phonenumber
        user_menu (message,"")
        
        
#        sq l = """SELECT * FROM users WHERE user_id=?"""
#        cursor.execute(sql, [(user_id)])
#        print(cursor.fetchall()) # or use fetchone()

  
  
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print("")
    print("get_text_messages(message):")
    if message.text.lower() == 'нет, не хочу!':
        print("  >> text: ", message.text.lower())
        db_table_val_users_green ( message.chat.id,\
                                   message.from_user.id,\
                                   message.message_id,\
                                   message.from_user.first_name,\
                                   message.from_user.last_name,\
                                   message.text)
        dell_message (message)
        bot.send_message(message.chat.id, 'Ну чтож, на нет и суда нет!)', reply_markup=telebot.types.ReplyKeyboardRemove())
        db_table_menu_user_id (user_id=message.from_user.id, menu_id=1, keyword="", flag=1) # добавляем индекс меню пользователя в базу
        user_menu (message,"")
        print("  >> переходим > user_menu ()")
    else:
        print ("  >> Проверяем яляется ли пользователь ботом = ", message.from_user.is_bot)
        if not(message.from_user.is_bot):  # Проверяем является ользователь ботом или нет
            print ("    >>> Пользователь не бот.")
            # проверяем есть ли пользователь в базе зарегистрированных
            sql_2 = "SELECT * FROM users WHERE user_id = :id"
            cursor.execute(sql_2, {"id": message.from_user.id})
            records = cursor.fetchone()
            print ("  >> message.from_user.id = ", message.from_user.id)
            print ("  >> Есть ли пользователь в базе = ", records)
            if not (records == None):
                print ("    >>> Пользователь есть в базе.")
                # проверяем ввел ли пользователь слово из меню
                text = str(message.text.lower())
                print ("    >> text = ", text)
                sql_3 = "SELECT * FROM menu_user WHERE name = :name"
                cursor.execute(sql_3, {"name": text})
                records_ans = cursor.fetchone()
                print ("    >> select menu: ", records_ans)
                #exit(0)
                if not (records_ans == None):
                    # если слово присутствует в базе меню то переходим дальше
                    keyword = records_ans[2]
                    print ("      >> keyword: ", keyword)                    
                    text_user = records_ans[4]
                    print ("      >> text_answ: ", text_user)
                    next_menu = records_ans[5]
                    print ("      >> next_menu: ", next_menu)
                    sql_2 = """UPDATE menu_user_id SET menu_id = ?, keyword = ? WHERE user_id = ?"""
                    cursor.execute(sql_2, (next_menu, keyword, message.from_user.id))
                    connection.commit()
                    user_menu (message, text_user)
                   
                else:
                    welcome_message (message)
                    print ("  >> К боту присоединился: ", records [1], " ", records [2], " из квартиры: ", records [4], "  <<")
                    db_table_menu_user_id (user_id=message.from_user.id, menu_id=1, keyword = "", flag=2) #сбрасываем индекс меню пользователя в default
                    user_menu (message, "")
            else:
                print ("    >>> Пользователя нет в базе.")
                keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                start = telebot.types.KeyboardButton ('/start')
                keyboard.add(start)                
                bot.send_message(message.chat.id, 'вы не прошли регистрацию! Воспользуйтесь командой /start)', reply_markup=keyboard)
                #start_message (message)


#db_table_message_id (date=res.date, user_id = message.chat.id, mess_id = res.message_id, text = res.text)


def user_menu (message, text: str):
    print ("")
    print ("user_menu (message, text: str):")
    print ("  >> message: ", message)
    print ("  >> text: ", text)
    sql = "SELECT * FROM menu_user_id WHERE user_id = ?"  # находим в таблице юзера
    cursor.execute(sql, [(message.from_user.id)])
    records = cursor.fetchone()
    print ("  >> Пользователь: ", records[0], "  вошел в меню:", records[1], " <<")
    user_id = records[0]
    menu_id = records[1]
    
    sql = "SELECT * FROM menu_user WHERE group_id = ?"  # находим в таблице меню список пунктов 
    cursor.execute(sql, [(menu_id)])
    records = cursor.fetchall()
    if not (menu_id == "0"):
        #print (records)
        #print (len (records))
        # Если текст в меню не задан, то напишем прость "Выберите меню:"
        if (text == ""):
            text = 'Выберите меню:'
        # создаем кнопки для меню
        #keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for row in records:
            if row[7] == "1": # проверяем включено ли меню
                print ("  >> info = ", row[1])
                # Создаем кнопки с принятием решения
                #keyboard.row (telebot.types.InlineKeyboardButton (text=row[1], callback_data = 'menu-'+row[2]))
                key = telebot.types.KeyboardButton (text=row[1])
                # выводим кнопки на экран
                keyboard.add(key)
    
        res = bot.send_message ( message.chat.id, text , reply_markup=keyboard )
    else:
        # если меню "0" то пишем текст
        res_2 = bot.send_message ( message.chat.id, text , reply_markup=telebot.types.ReplyKeyboardRemove() )
        # ждем написание текста пользоателем
        bot.register_next_step_handler(res_2 , type_mess)
    
    
# обраьботка текста написаного пользователем
def type_mess(message):
    print ("")
    print ("type_mess(message):")
    print ("  >> message", message)
    
    
    tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x)) #Конвертация даты в читабельный вид
    date_mess = str(tconv(message.date))
    print ("  >> date: ", date_mess)
    # узнаем текст и данные о пользователе
    us_id = message.from_user.id
    type_text = message.text
    print("    >> us_id = ", us_id)
    print("    >> type_text = ", type_text)
    
    sql_6 = "SELECT * FROM menu_user_id WHERE user_id = ?"  # находим в таблице меню список пунктов 
    cursor.execute(sql_6, [(us_id)])
    records_user = cursor.fetchone()
    print("  >> records_user = ", records_user)
    from_mess = records_user[2]
    print("    >> from_mess = ", from_mess)
    
    sql_7 = "SELECT * FROM menu_user WHERE keyword = ?"  # находим в таблице меню список пунктов 
    cursor.execute(sql_7, [(from_mess)])
    records_from = cursor.fetchone()
    print("  >> records_from = ", records_from)
    from_name = records_from[1]
    print("    >> from_name = ", from_name)
    
    
   # находим людей в базе данных кому адресовано сообщение
    sql_5 = "SELECT * FROM admin_table WHERE " + from_mess + " = 'true'"  # находим в таблице меню список пунктов 
    print ("  >> sql_5: ", sql_5)
    cursor.execute(sql_5) #, {"row_id": from_mess})
    records_id = cursor.fetchall()
    print ("  >> records_id: ", records_id)
    # формируем текст отправляемый для получателя
    send_text = "Пользователь: " + str(us_id) +"\n" + \
                "Сообщение для: " + from_name + "\n" + \
                "Отправлено: " + date_mess + "\n" + \
                "Сообщение: " + type_text
    for row in records_id:
        print ("  >> id :", row)
        res_2 = bot.send_message ( row[0], send_text)
        print ("  >> res_2 :", res_2)
    
    res_2 = bot.send_message ( us_id , "Ваше сообщение отправлено адресату!")
    db_table_menu_user_id (user_id = us_id, menu_id = 1, keyword = "" , flag = 2)
    user_menu (message, "")
    
    
#@bot.message_handler(content_types=['text'])
#def get_text_messages(message):
#    if message.text.lower() == 'привет':
#        bot.send_message(message.chat.id, 'Привет! Ваше имя добавлено в базу')
#            
#        us_id = message.from_user.id
#        us_name = message.from_user.first_name
#        us_sname = message.from_user.last_name
#        username = message.from_user.username
            
#        db_table_val( user_id=us_id,\
#                      user_name=us_name,\
#                      user_surname=us_sname,\
#                      username = username)
    
bot.polling(none_stop=True)

# закрываем соединение с базой
#connection.close()



