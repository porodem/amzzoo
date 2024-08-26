#telegram zoo game


import telebot
import re
import sql_helper
# https://pypi.org/project/emoji/
import emoji

from datetime import datetime, timedelta
from telebot import types
from telebot.util import update_types
from pprint import pprint # to investigate what inside objects

print('- - - - - S T A R T E D - - - - - - ')

f = open("token.txt","r")
token = f.readline()
token = token.rstrip() # read about function
print(token, type(token))
f.close()
bot = telebot.TeleBot(token, parse_mode=None)




c_start = types.BotCommand('start','Начать')
my_pets_command = types.BotCommand('show_pets','Показать питомцев')
main_menu = types.BotCommand('main_menu','Меню')
main_menu = types.BotCommand('earn_money','Найти деньги')
bot.set_my_commands([my_pets_command,main_menu])

# buttons test
@bot.message_handler(commands=['start'])
def show_pets(message):

    # check if user exists
    if sql_helper.db_check_player_exists(message.from_user.id) is None:
        msg_json = message.json
        print(msg_json)
        # new_member = msg_json["new_chat_member"]
        # tid = new_member["id"]
        # print(new_member)
        # vname = new_member["username"]

        sql_helper.db_new_player(message.from_user.id,message.from_user.username,'x')

    else:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🐇 Питомцы")
        btn2 = types.KeyboardButton("🏫 Имущество")
        btn3 = types.KeyboardButton("⚒ Работа")
        btn4 = types.KeyboardButton("🛒 Магазин")
        markup.add(btn1,btn2,btn3,btn4)
        bot.send_message(message.from_user.id, "select :", reply_markup=markup)  
        bot.register_next_step_handler(message, search_money)

# buttons test
@bot.message_handler(commands=['show_pets'])
def show_pets(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🐣 my pet")
    btn2 = types.KeyboardButton("😀 test")
    markup.add(btn1,btn2)
    bot.send_message(message.from_user.id, "select :", reply_markup=markup)  
    bot.register_next_step_handler(message, step_two)

# buttons test
@bot.message_handler(commands=['earn_money'])
def show_pets(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("⛏ Искать клад")
    btn2 = types.KeyboardButton("⚒ Работать")
    markup.add(btn1,btn2)
    bot.send_message(message.from_user.id, "select :", reply_markup=markup)  
    bot.register_next_step_handler(message, search_money)

def search_money(message):
    if re.match('.*клад.*',message.text):
        bot.reply_to(message, 'pet option')
    else:
        bot.reply_to(message, 'test option')

def step_two(message):
    if re.match('.*pet.*',message.text):
        bot.reply_to(message, 'pet option')
    else:
        bot.reply_to(message, 'test option')

# legacy func from previous project
@bot.message_handler(regexp=".*(pet|пет).*")
def attach_ls(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('show pets'))
    msg = bot.send_message(message.chat.id, "choose type shit", reply_markup=markup)

def pet_shop(message):
    print('---------- PET SHOP -----------')
    tid = message.from_user.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🥚 💰 1")
    btn2 = types.KeyboardButton("🐭 💰 3")
    btn3 = types.KeyboardButton("🕷 💰 5")
    btn4 = types.KeyboardButton("🐈 💰 9")
    markup.add(btn1,btn2,btn3,btn4)
    bot.send_message(tid, 'Выберите питомца:', reply_markup=markup)  
    bot.register_next_step_handler(message, buy_pet)

def buy_pet(message):
    print(' - - - buy pet - - - ')
    if re.match('.*9.*',message.text):
        sql_helper.db_buy_pet(message.from_user.id, 4)
    else:
        print('noting ...')

def next_option(message):
    if re.match('.*Питомцы.*',message.text):
        bot.reply_to(message, '')
    elif re.match('.*Имущество.*',message.text):
        bot.reply_to(message, 'test option')
    elif re.match('.*Работа.*',message.text):
        bot.reply_to(message, 'test option')
    elif re.match('.*Магазин.*',message.text):
        bot.register_next_step_handler(message, pet_shop)

def get_statistics(tid):
    pet_cnt = sql_helper.db_check_owned_pets(tid)
    coins = sql_helper.db_check_owned_coins(tid)
    player_stats = 'Питомцы 🐇: ' + str(pet_cnt) + '\nДеньги 💰: ' + str(coins)

    return player_stats


#anything other messages
@bot.message_handler(func=lambda m:True)
def echo_all(message):
    print('---------- ANYTHING -----------')
    tid = message.from_user.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🐇 Питомцы")
    btn2 = types.KeyboardButton("🏫 Имущество")
    btn3 = types.KeyboardButton("⚒ Работа")
    btn4 = types.KeyboardButton("🛒 Магазин")
    markup.add(btn1,btn2,btn3,btn4)
    bot.send_message(tid, get_statistics(tid), reply_markup=markup)  
    bot.register_next_step_handler(message, next_option)

bot.infinity_polling()

