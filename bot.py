# Подключаем библиотеки
import sqlite3   # библиотека баз данных
import telebot   # библитека для работы с telegramm
import re
import time
import os
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql

from os import environ
from dotenv import load_dotenv

# Token для телеграмм бота
load_dotenv()
token = environ.get('TELEGRAM_TOKEN')

# Token для телеграмм бота
bot = telebot.TeleBot(token)
# 
# подключаемся к базе данных подпищиков
#Данные для подключения к базе данных
# база данных на PostgreSQL
DBNAME = environ.get('DBNAME') #имя базы данных 
HOST = environ.get('HOST')
PASSWORD = environ.get('PASSWORD')
PORT = environ.get('PORT')
DATABASE_URL =  environ.get('DATABASE_URL')

# Подключение к существующей базе данных
connection = psycopg2.connect(DATABASE_URL)
cursor = connection.cursor()

# переменная вывода отладочной информации на экран
# 0 -не выводить;
# 1 - выводить;
test = 1
# -------------------------------- Создание таблиц в базе если их нет ----------------------------------------------------    

# массив для хранения ID сообщений для авторизированого пользователя
cursor.execute('''CREATE TABLE IF NOT EXISTS menu_user_id ( user_id INT PRIMARY KEY,
                                                            menu_id TEXT,
                                                            keyword TEXT);''')

# массив для хранения сообщений от пользователей для совета дома и дмина
cursor.execute('''CREATE TABLE IF NOT EXISTS user_to_admin ( id SERIAL,
                                                             user_id TEXT,
                                                             from_id TEXT,
                                                             date TEXT,
                                                             text TEXT);''')

# массив для хранения сообщений от совета дома и дмина для пользователей
cursor.execute('''CREATE TABLE IF NOT EXISTS admin_to_user ( id SERIAL,
                                                             user_id TEXT,
                                                             from_id TEXT,
                                                             date TEXT,
                                                             text TEXT);''')

# массив для хранения ID сообщений для авторизированого пользователя
# таблица сообщений пользователя
# id: str   -  номер автоматический,
# date: str   -  дата сообщения,
# user_id: str -  id пользователя отправителя, 
# from_id: str -  id пользователя получателя,
# mess_id: str - id сообщения,
# text: str  -  сообщение
cursor.execute('''CREATE TABLE IF NOT EXISTS message_id ( id_n SERIAL,
                                                          date TEXT,
                                                          user_id TEXT,
                                                          from_id TEXT,
                                                          mess_id TEXT,
                                                          text TEXT);''')

# массив для хранения ID сообщений для неавторизированого пользователя
cursor.execute('''CREATE TABLE IF NOT EXISTS users_green ( id_n SERIAL,
                                                           user_id TEXT,
                                                           send_user_id TEXT,
                                                           mess_id TEXT,
                                                           user_name TEXT,
                                                           user_surname TEXT,
                                                           text TEXT);''')

# проверяем есть ли таблица в базе, если нет то создаем
cursor.execute('''CREATE TABLE IF NOT EXISTS users ( user_id INT PRIMARY KEY,
                                                     user_name TEXT,
                                                     user_surname TEXT,
                                                     username TEXT,
                                                     user_kv TEXT,
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
cursor.execute('''CREATE TABLE IF NOT EXISTS messages( id INT PRIMARY KEY,
                                                       mess_id TEXT,
                                                       content_type TEXT,
                                                       user_id TEXT,
                                                       user_first_name TEXT,
                                                       user_username TEXT,
                                                       user_last_name TEXT,
                                                       date TEXT,
                                                       mess_text TEXT);''')

# проверяем есть ли таблица в базе, если нет то создаем
# таблица стандартного текста для ответов
cursor.execute('''CREATE TABLE IF NOT EXISTS mess ( id SERIAL,
                                                    title TEXT,
                                                    text TEXT,
                                                    group_id TEXT,
                                                    description TEXT);''')

# проверяем есть ли таблица в базе, если нет то создаем
# список ID администраторов и принадлежность к группе
# user_id - ID пользователя;
# admin BOOL - администраторы бота;
# sov_dom BOOL - пользователи в совете дома;
# uk BOOL - пользователи от управляющей компании;
# dvor BOOL - поьзователи от уборки дома;
# konserj BOOL - пользователи от коньсъержек;
# ohrana BOOL - пользователи от охраны дома
cursor.execute('''CREATE TABLE IF NOT EXISTS admin_table ( user_id INT PRIMARY KEY,
                                                           admin BOOL,
                                                           sov_dom BOOL,
                                                           uk BOOL,
                                                           dvor BOOL,
                                                           konserj BOOL,
                                                           ohrana BOOL);''')


cursor.execute('''CREATE TABLE IF NOT EXISTS admin_table_name ( name TEXT PRIMARY KEY,
                                                                text TEXT,
                                                                description TEXT);''')

# Таблица список доступных команд для пользователей и администраторов
# id SERIAL - № п/п
# command TEXT - имя комманды
# text TEXT - поясняющий текст
# user BOOL - метка принадлежности для юзера
# admin BOOL - метка принадлежности для админа
# description TEXT - коментарий
cursor.execute('''CREATE TABLE IF NOT EXISTS command ( id SERIAL,
                                                       command TEXT,
                                                       text TEXT,
                                                       user_flag BOOL,
                                                       admin_flag BOOL,
                                                       description TEXT);''')

# Таблица, список меню для зарегистрированных пользователей
# id SERIAL - № п/п
# name TEXT - название кнопки
# keyword TEXT - сокращеное название
# group_id TEXT - индификатор группы
# text TEXT - текст для пользователя
# next_group TEXT - ID для перехода к группе
# description TEXT - описание
# onoff BOOL - вкл/выкл отображения у пользователя
cursor.execute('''CREATE TABLE IF NOT EXISTS menu_user ( id SERIAL,
                                                         name TEXT,
                                                         keyword TEXT,
                                                         group_id TEXT,
                                                         text TEXT,
                                                         next_group TEXT,
                                                         description TEXT,
                                                         onoff BOOL);''')

# Таблица, список перехода пользователя по группам меню
# user_id INT PRIMARY KEY - id пользователя
# menu_id TEXT - id группы меню
# keyword TEXT - сокращеное название
cursor.execute('''CREATE TABLE IF NOT EXISTS menu_user_id ( user_id INT PRIMARY KEY,
                                                            menu_id TEXT,
                                                            keyword TEXT);''')


connection.commit() # сохраняем изменения в базе
# --------------------------------КОНЕЦ - Создание таблиц в базе если их нет----------------------------------------------------    

#=================================================================================================================================

# -------------------------------- Процедуры чтения данных из таблицы ----------------------------------------------------    
# процедура чтения данных из базы данных
# таблица сообщений для пользователя
# id: str   -  номер автоматический,
# title: str   -  переменная,
# text: str -  текст,
# group_id: str - группа,
# description: str  -  описание
def read_text_mess (title: str):
    cursor.execute(''' SELECT *
                       FROM mess
                       WHERE title = %s;
                    ''', [(title)])
    records = cursor.fetchone()
    if (test):
        print(records)  # выводим все значения таблицы на экран
    return (records)
# --------------------------------КОНЕЦ - Процедуры чтения данных из таблицы----------------------------------------------------    

#=================================================================================================================================

# -------------------------------- Запись данных в таблицы ----------------------------------------------------    
# процедура занесения данных о сообщениях пользователя в базу данных
# таблица сообщений пользователя
# id: str   -  номер автоматический,
# date: str   -  дата сообщения,
# user_id: str -  id пользователя отправителя, 
# from_id: str -  id пользователя получателя,
# mess_id: str - id сообщения,
# text: str  -  сообщение
def add_mess_id (message):
    if (test): # отладка
        print ("")
        print ("def add_mess_id (message):")
        print ("  >> message:", message)
    user_id = message.from_user.id
    from_id = message.chat.id
    mess_id = message.id
    text = message.text
    tconv = lambda x: time.strftime("%H:%M:%S %d.%m.%Y", time.localtime(x)) #Конвертация даты в читабельный вид
    date = str(tconv(message.date))
    if (test): # Отладка
        print ("  >> date: ", date)
        print ("  >> user_id: ", user_id)
        print ("  >> from_id: ", from_id)
        print ("  >> mess_id: ", mess_id)
        #print ("  >> text: ", text)   
    # запишем данные в таблицу
    insert = '''INSERT
                INTO message_id (date, user_id, from_id, mess_id, text)
                VALUES (%s, %s, %s, %s, %s)
             '''
    cursor.execute(insert, (date, user_id, from_id, mess_id, text))
    connection.commit() # сохраняем изменения в таблице
    if (test): # отладка
        print ("  >> Данные записаны в таблицу message_id!!! <<")


# процедура занесения данных о пользователе в базу данных
# таблица сообщений не зарегистрированного пользователя
# user_id: str   -  id пользователя,
# mess_id: str   -  id сообщения пользователя,
# user_name: str -  имя пользователя,
# user_surname: str - фамилия пользователя,
# text: str  -  текст
def db_table_val_users_green (user_id: str, send_user_id: str,  mess_id: str, user_name:str, user_surname:str, text:str):
    
    #columns = [user_id, send_user_id, mess_id, user_name, user_surname, text]
    
    insert = '''INSERT
                INTO users_green (user_id, send_user_id, mess_id, user_name, user_surname, text)
                VALUES (%s, %s, %s, %s, %s, %s)
             '''
    cursor.execute(insert, (user_id, send_user_id, mess_id, user_name, user_surname, text))
    connection.commit() # сохраняем изменения в таблице
    cursor.execute('SELECT * FROM users_green ')  # Выбираем все значения в таблице
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
        sql = ''' SELECT *
                  FROM menu_user_id
                  WHERE user_id = '%s'
              '''
        cursor.execute(sql, [(user_id)])
        records = cursor.fetchone()
        menu_id = 1
        if (records == None):
            cursor.execute(''' INSERT INTO menu_user_id ( user_id, menu_id, keyword) VALUES (%s,%s,%s);''', (user_id, menu_id, keyword))
            print ("    >> добавление в базу menu_user_id: ", user_id, "  menu_id: ", menu_id, "  keyword: ", keyword)
        else:
            sql = '''UPDATE menu_user_id
                     SET menu_id = '%s'
                     WHERE user_id = '%s', keyword = %s
                  '''
            cursor.execute(sql, (menu_id, user_id, keyword))
            print ("    >> Пользователь есть в базе menu_user_id! Настройки сброшены!")
    elif flag == 2:
        sql = ''' SELECT *
                  FROM menu_user_id
                  WHERE user_id = '%s'
              '''
        cursor.execute(sql, [(user_id)])
        records = cursor.fetchone()
        if not (records == None):
            sql = ''' UPDATE menu_user_id
                      SET menu_id = '%s', keyword = %s
                      WHERE user_id = '%s'
                  '''
            cursor.execute(sql, (menu_id, keyword,  user_id))
            print ("    >> в таблице menu_user_id! Изменены данные: ",user_id,",  menu_id: " ,menu_id,",  keyword: " ,keyword)
    elif flag == 3:
        sql = ''' DELETE
                  FROM menu_user_id
                  WHERE user_id = '%s'
              '''
        cursor.execute(sql, [(user_id)])
        print ("    >> в таблице menu_user_id! Удалены данные пользователя: ",user_id)
   
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
    print ("")
    print ("def db_table_val():")
    sql = ''' INSERT INTO users ( user_id,
                                  user_name,
                                  user_surname,
                                  username,
                                  user_kv,
                                  phonenumber)
              VALUES (%s, %s, %s, %s, %s, %s);
           '''
    cursor.execute(sql, (user_id, user_name, user_surname, username, user_kv, phonenumber))           
    connection.commit()
    cursor.execute(''' SELECT *
                       FROM users
                   ''')
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
# -------------------------------- КОНЕЦ Запись данных в таблицы ----------------------------------------------------    

#=================================================================================================================================

# -------------------------------- Удаление данных из таблицы ----------------------------------------------------    

# Процедура удаления сообщений с экрана пользователя
# user_id - id пользователя 
def dell_mess_id (user_id: str):
    if (test):
        print ("")
        print ("def dell_mess_id (user_id: str):")
        print ("  >> user_id: ", user_id)
    # Запрашиваем данные в таблице с сообщениями для user_id
    sql = '''SELECT *
             FROM message_id
             WHERE from_id = '%s';
          '''
    cursor.execute(sql, (user_id,))
    records = cursor.fetchall()
    if (test):
        print ("  >> Кол-во записей: ", len (records))
    for row in records:
        if (test): 
            print("    >> Delete  ->  ID:", row[3], "  mess_id:", row[4])
        bot.delete_message(row[3], row[4])   # удалим ранее присланые сообщения, т.к. пользователь отказался далее использовать бота
        sql = '''DELETE
                 FROM message_id
                 WHERE mess_id = %s;
              '''
        cursor.execute(sql, (row[4],)) # удаляем из базы сообщения
    connection.commit() # сохраняем изменения в таблице
    if (test):
        print ("    >> Сообщения удалены")
    
# удаление сообщений для не зарегистрированных пользователей
def dell_message (result):
    if (test):
        print ("")
        print ("def dell_message (result):")
        print ('  >> user_id = ', result.chat.id)
    sql = '''SELECT *
             FROM users_green
             WHERE user_id = '%s'
          '''
    cursor.execute(sql, [(result.chat.id)])
    records = cursor.fetchall()
    if (test):
        print("  >> Всего строк:  ", len(records))
    for row in records:
        if (test):
            print("    >> Delete  ->  ID:", row[1], "  mess_id:", row[3])
        bot.delete_message(row[1], row[3])   # удалим ранее присланые сообщения, т.к. пользователь отказался далее использовать бота
        sql = '''DELETE
                 FROM users_green
                 WHERE mess_id = %s;
              '''
        cursor.execute(sql, [(row[3])])
    connection.commit()
# -------------------------------- КОНЕЦ Удаление данных из таблицы ----------------------------------------------------    



unknown_text: str = "Ничего не понятно, но очень интересно.\nПопробуй команду /help"

# Обрабатываем команду /start
@bot.message_handler(commands=['start'])
def ferst_message(message):
    if (test):
        print ("")
        print ("def ferst_message(message):")
        print ("  >> Яляется ли пользователь ботом = ", message.from_user.is_bot)
    if not(message.from_user.is_bot):  # Проверяем является ользователь ботом или нет
        user_id = message.from_user.id
        # проверяем есть ли пользователь в базе зарегистрированных
        sql = '''SELECT * FROM users WHERE user_id = '%s';'''
        cursor.execute(sql, (user_id,))
        records = cursor.fetchone()
        if (test):
            print ("  >> user_id: ", user_id)
            print ("  >> Есть ли пользователь в базе = ", records)
        if not (records == None):
            # Пользователь есть в базе зарегистрированных
            if (test):
                print ("    >> К боту присоединился: ", records [1], " ", records [2], " из квартиры: ", records [4])
            dell_mess_id (user_id) # удаляем ранее присланые сообщения
            add_mess_id (message) # добаляем сообщение пользователя в базу
            welcome_message (message)
        else:
            start_message (message)

# Обрабатываем команду /stop
@bot.message_handler(commands=['stop'])
def stop_message(message):
    print ("Яляется ли пользователь ботом = ", message.from_user.is_bot)
    bot.send_message(message.chat.id, "Раздел находиться в разработке!")

# Обрабатываем команду /stop
#@bot.message_handler(commands=['upp'])
#def stop_message(message):
#    sql = ''' UPDATE menu_user SET keyword = 'admin' WHERE keyword = 'admin_bot';'''
#    cursor.execute(sql)
#    connection.commit()

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
    if (test): # Отладка
        print("")
        print("help_message(message):")
        print (" < < message: ", message)
    user_id = message.from_user.id  # id пользователя
    text = message.text
    dell_mess_id (user_id) # удаляем ранее присланые сообщения
    add_mess_id (message) # добаляем сообщение пользователя в базу
    if (test):  # Отладка
        print ("  >> user_id: ", user_id, "  text: ", text)
        print ("  >> Яляется ли пользователь ботом: ", message.from_user.is_bot)
    if not (message.from_user.is_bot):  # Проверяем является ользователь ботом или нет
        #bot.send_message(message.chat.id, "Раздел находиться в разработке!")
    
        # проверка есть ли пользователь в списке админив или нет
        sql = '''SELECT *
                 FROM admin_table
                 WHERE user_id = '%s'
              ''' # находим в таблице меню список пунктов 
        cursor.execute(sql, [(user_id)]) #, {"row_id": from_mess})
        records_id = cursor.fetchone()
        print ("  >> records_id: ", records_id)
        
        # проверка есть ли пользователь в списке зарегистрированных 
        sql = ''' SELECT *
                  FROM users
                  WHERE user_id = '%s'
              ''' # находим в таблице меню список пунктов 
        cursor.execute(sql, [(user_id)]) #, {"row_id": from_mess})
        records_user = cursor.fetchone()
        print ("  >> records_user: ", records_user)
        if not (records_id == None):
            print ("    >> Пользователь присутствует в базе админов!")
            sql = ''' SELECT *
                      FROM command
                      WHERE admin_flag = 'true'
                  '''  # находим в таблице меню список пунктов 
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
            add_mess_id (res) # добаляем сообщение пользователя в базу
        elif not (records_user == None):
            print ("    >> Пользователь присутствует в базе пользователей!")
            sql = ''' SELECT *
                      FROM command
                      WHERE user_flag = 'true'
                  '''  # находим в таблице меню список пунктов 
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
            add_mess_id (res) # добаляем сообщение пользователя в базу

        else:
            print ("    >> Пользователь не подключен к боту!")
            res = bot.send_message(user_id, 'Вам доступна комманда: /start', reply_markup=telebot.types.ReplyKeyboardRemove())
            print (" > >  message: ", res)
            print ("  >> user_id: ", res.chat.id, "  text:", res.text)
            add_mess_id (res) # добаляем сообщение пользователя в базу
            
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
        sql = ''' SELECT *
                  FROM admin_table
                  WHERE user_id = %s;
              ''' # находим в таблице меню список пунктов 
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
    sql = ''' SELECT *
              FROM admin_table
              WHERE user_id = %s
          ''' # находим в таблице меню список пунктов 
    cursor.execute(sql, [(user_id)]) #, {"row_id": from_mess})
    records_id = cursor.fetchone()
    print ("  >> records_id: ", records_id)

    
    i: int = 0
    for row in records_id:
        if row == True:
            user_sdmin_id = i
            print ("    >> отправитель: " + str (user_sdmin_id) + ",  row: " + str(row))
            break
        i = i+1

    print ("  >> user_sdmin_id: ", str(user_sdmin_id))
    sql = ''' SELECT *
              FROM admin_table_name
              WHERE id = %s;
          ''' # находим в таблице меню список пунктов 
    cursor.execute(sql, str(user_sdmin_id)) #, {"row_id": from_mess})
    records_data = cursor.fetchone()
    print ("  >> records_data: ", records_data)


    sql = ''' SELECT user_id
              FROM users
          '''  # находим в таблице меню список пунктов 
    cursor.execute(sql) #, {"row_id": from_mess})
    records_users = cursor.fetchall()
    print ("  >> records_users: ", records_users)
    text = text + "\nС уважением, " + str(records_data[1]) + "!"
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
    print ("def dell_user:")
    print (" > user_id: ", user_id)
    sql = ''' DELETE FROM users
              WHERE user_id = '%s'
          '''
    cursor.execute(sql, [(user_id)])
    connection.commit()
    
    sql = ''' DELETE FROM users_green
              WHERE user_id = '%s'
          '''
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
    us_name = message.from_user.first_name
    us_sname = message.from_user.last_name
    usname = message.from_user.last_name
    user_id = message.from_user.id
    if (test):
        print ("")
        print ("def welcome_message(message):")
        print ("  >> us_name: ", us_name)
        print ("  >> us_sname: ", us_sname)
        print ("  >> usname: ", usname)
    # Печатаем приветственный текст для пользователя.
    text: str = read_text_mess("start_welcome") #'С возвращением, ' + us_name
    text_2 = re.sub(r'(?i)us_name(?=\W)', us_name, text[2])
    res = bot.send_message(message.chat.id, text_2, reply_markup=telebot.types.ReplyKeyboardRemove()) #'Добро пожаловать, ' us_name ' ' us_sname)
    if (test):
        print ("  >> message: ", res)
#    dell_mess_id (user_id) # удаляем ранее присланые сообщения
    add_mess_id (res) # добаляем сообщение пользователя в базу
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
    print ("")
    print ("def type_nomber_kv (message):")
    res = bot.send_message ( message.chat.id, 'Теперь введите № квартиры: '); #, reply_markup=keyboard )
    db_table_val_users_green ( message.chat.id,\
                               res.from_user.id,\
                               res.message_id,\
                               res.from_user.first_name,\
                               res.from_user.last_name,\
                               res.text)
    bot.register_next_step_handler(res , kv)

def kv(message):
    print ("")
    print ("def kv(message):")
    kv = message.text
    db_table_val_users_green ( message.chat.id,\
                               message.from_user.id,\
                               message.message_id,\
                               message.from_user.first_name,\
                               message.from_user.last_name,\
                               message.text)

    if kv.isdigit():  # проверяем являеться ли числом введеное значение
        kv_2 = int(kv)
        print ("  >> Номер квартиры: ", kv)
        if (kv_2 > 0) and (kv_2 < 753):
            dell_message (message)
            bot.send_message ( message.chat.id, ' Вы ввели № квартиры - ' + kv )
            # добавляем пользователя в базу 
           
            us_id = message.from_user.id
            us_name = message.from_user.first_name
            us_sname = message.from_user.last_name
            username = message.from_user.username
            
            print ("    >> id = ", us_id)
            print ("    >> first_name = ", us_name)
            print ("    >> last_name = ", us_sname)
            print ("    >> username = ", username)
            print ("    >> kv = ", kv)
         
            sql = ''' SELECT *
                      FROM users
                      WHERE user_id='%s'
                  '''
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
            print ("  >> Введен не корректный номер квартиры")
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
        print ("  >> Введен не корректный номер квартиры")
        res = bot.send_message ( message.chat.id, ' Вы указали неверный номер квартиры. Воспользуйтесь коммандой: /start.' )
        db_table_val_users_green ( message.chat.id,\
                                   res.from_user.id,\
                                   res.message_id,\
                                   res.from_user.first_name,\
                                   res.from_user.last_name,\
                                   res.text)



    #bot.send_message ( query.message.chat.id, 'Жаль. До скорой встречи!' )
    #bot.send_message ( query.message.chat.id, 'воспользуйтесь меню или /start' )

# функция ответа пользователю при вводе № квартиры
def get_answer_kv (query):
    print ("")
    print ("def get_answer_kv (query):")
    
    bot.answer_callback_query(query.id)

    user_id_kv = query.from_user.id
    message_id_kv = query.message.message_id
    reply_markup_kv = query.message.reply_markup
    print("  >> Rename  ->  ID:", user_id_kv, "  mess_id:", message_id_kv)

    text = query.message.text
    print(text)
    

            
@bot.message_handler(content_types=['contact'])
def contact(message):
    print ("")
    print ("def contact(message):")
    if message.contact is not None:
        bot.send_message(message.chat.id, 'Вы успешно отправили свой номер', reply_markup=telebot.types.ReplyKeyboardRemove())
  
        phonenumber = str(message.contact.phone_number)
        user_id = str(message.contact.user_id)
        print ("  >> phonenumber = ", phonenumber)
        print ("  >> user_id =", user_id)
        
        db_table_menu_user_id (user_id=message.from_user.id, menu_id=1, keyword = "", flag=1) # добавляем индекс меню пользователя в базу

        #sql = "SELECT * FROM users WHERE user_id=?"
        #cursor.execute(sql, user_id)
        #print(cursor.fetchone()) # or use fetchone()
 
        sql = '''UPDATE users
                 SET phonenumber = %s
                 WHERE user_id = %s
              '''
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
    if (test):
        print("")
        print("get_text_messages(message):")
        print ("  >> Проверяем яляется ли пользователь ботом = ", message.from_user.is_bot)
    if not(message.from_user.is_bot):  # Проверяем является ользователь ботом или нет
        # данные о поьзователе
        user_id = message.from_user.id
        chat_id = message.chat.id
        text_lower = message.text.lower()
        mess_id = message.message_id
        user_first = message.from_user.first_name
        user_last = message.from_user.last_name
        text = message.text
        if (test):
            print ("    >>> Пользователь не бот.")
            print("  >> user_id: ", user_id)
            print("  >> chat_id: ", chat_id)
            print("  >> text_lower: ", text_lower)
            print("  >> mess_id: ", mess_id)
            print("  >> user_first: ", user_first)
            print("  >> user_last: ", user_last)
            print("  >> text: ", text)
        
        if (text_lower == 'нет, не хочу!'):
            db_table_val_users_green ( chat_id, user_id, mess_id, user_first, user_last, text)
            dell_message (message)
            res = bot.send_message(message.chat.id, 'Ну чтож, на нет и суда нет!)', reply_markup=telebot.types.ReplyKeyboardRemove())
            add_mess_id (res) # добаляем сообщение пользователя в базу
            db_table_menu_user_id (user_id=message.from_user.id, menu_id=1, keyword="", flag=1) # добавляем индекс меню пользователя в базу
            user_menu (message,"")
            #print("  >> переходим > user_menu ()")
        else:
            dell_mess_id (user_id) # удаляем ранее присланые сообщения
            add_mess_id (message) # добаляем сообщение пользователя в базу
            # проверяем есть ли пользователь в базе зарегистрированных
            sql_2 = ''' SELECT *
                        FROM users
                        WHERE user_id = '%s';
                    '''
            cursor.execute(sql_2, (user_id,))
            records = cursor.fetchone()
            if (test):
                print ("  >> user_id = ", user_id)
                print ("  >> Есть ли пользователь в базе = ", records)
            if not (records == None):
                if (test):
                    print ("    >>> Пользователь есть в базе.")
                    #text = str(message.text.lower())
                    print ("    >> text = ", text_lower)
                # проверяем ввел ли пользователь слово из меню
                sql_3 = ''' SELECT *
                            FROM menu_user
                            WHERE name = %s;
                        '''
                cursor.execute(sql_3, (text_lower,))
                records_ans = cursor.fetchone()
                if (test):
                    print ("    >> select menu: ", records_ans)
                #exit(0)
                if not (records_ans == None):
                    # если слово присутствует в базе меню то переходим дальше
                    keyword = records_ans[2]
                    text_user = records_ans[4]
                    next_menu = records_ans[5]
                    if (test):
                        print ("      >> keyword: ", keyword)                    
                        print ("      >> text_answ: ", text_user)
                        print ("      >> next_menu: ", next_menu)
                    sql_2 = ''' UPDATE menu_user_id
                                SET menu_id = %s, keyword = %s
                                WHERE user_id = %s;
                            '''
                    cursor.execute(sql_2, (next_menu, keyword, user_id))
                    connection.commit()
                    user_menu (message, text_user)
                   
                else:
                    if (test):
                        print ("  >> К боту присоединился: ", records [1], " ", records [2], " из квартиры: ", records [4], "  <<")
                    db_table_menu_user_id (user_id=message.from_user.id, menu_id=1, keyword = "", flag=2) #сбрасываем индекс меню пользователя в default
                    #user_menu (message, "")
                    welcome_message (message)
            else:
                print ("    >>> Пользователя нет в базе.")
                keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                start = telebot.types.KeyboardButton ('/start')
                keyboard.add(start)                
                bot.send_message(message.chat.id, 'вы не прошли регистрацию! Воспользуйтесь командой /start)', reply_markup=keyboard)
                #start_message (message)


#            dell_mess_id (user_id) # удаляем ранее присланые сообщения
#            add_mess_id (message) # добаляем сообщение пользователя в базу
 
# отображение меню для пользователя
def user_menu (message, text: str):
    if (test):
        print ("")
        print ("def user_menu (message, text: str):")
        print ("  >> message: ", message)
        print ("  >> text: ", text)
    # находим в таблице юзера
    sql = ''' SELECT *
              FROM menu_user_id
              WHERE user_id = %s;
          ''' 
    cursor.execute(sql, [(message.from_user.id)])
    records = cursor.fetchone()
    if (test):
        print ("  >> Пользователь: ", records[0], "  вошел в меню:", records[1], " <<")
    user_id = records[0]
    menu_id = records[1]
    # находим в таблице меню список пунктов 
    sql = ''' SELECT *
              FROM menu_user
              WHERE group_id = %s;
          '''
    cursor.execute(sql, [(menu_id)])
    records = cursor.fetchall()
    if (test):
        print ("  >> menu: ")
        for row in records:
            print ("     > ", row[1])
        
        print ("  >> menu_id: ", menu_id)
        
    if not (menu_id == "0"):
        #print (records)
        if (test):
            print ("  >> кол-во кнопок: ", len (records))
        # Если текст в меню не задан, то напишем прость "Выберите меню:"
        if (text == ""):
            text = 'Выберите меню:'
        # создаем кнопки для меню
        #keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        for row in records:
            if row[7] == True: # проверяем включено ли меню
                if (test):
                    print ("  >> info = ", row[1])
                # Создаем кнопки с принятием решения
                #keyboard.row (telebot.types.InlineKeyboardButton (text=row[1], callback_data = 'menu-'+row[2]))
                key = telebot.types.KeyboardButton (row[1])
                # выводим кнопки на экран
                keyboard.add(key)
                
        #dell_mess_id (user_id) # удаляем ранее присланые сообщения    
        res = bot.send_message ( message.chat.id, text , reply_markup=keyboard )
        add_mess_id (res) # добаляем сообщение пользователя в базу
    else:
        # если меню "0" то пишем текст
        dell_mess_id (user_id) # удаляем ранее присланые сообщения
        res_2 = bot.send_message ( message.chat.id, text , reply_markup=telebot.types.ReplyKeyboardRemove() )
        add_mess_id (res_2) # добаляем сообщение пользователя в базу
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
    # находим в таблице меню список пунктов 
    sql_6 = ''' SELECT *
                FROM menu_user_id
                WHERE user_id = %s;
            ''' 
    cursor.execute(sql_6, (us_id,))
    records_user = cursor.fetchone()
    print("  >> records_user = ", records_user)
    from_mess = records_user[2]
    print("    >> from_mess = ", from_mess)
    
    # находим в таблице меню список пунктов 
    sql_7 = ''' SELECT *
                FROM menu_user
                WHERE keyword = %s;
            ''' 
    cursor.execute(sql_7, [(from_mess)])
    records_from = cursor.fetchone()
    print("  >> records_from = ", records_from)
    from_name = records_from[1]
    print("    >> from_name = ", from_name)
    
    
   # находим людей в базе данных кому адресовано сообщение
    # находим в таблице меню список пунктов 
    sql_5 = ''' SELECT *
                FROM admin_table
                WHERE {} = true;
            ''' .format(from_mess)
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



