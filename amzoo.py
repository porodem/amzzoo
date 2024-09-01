#telegram zoo game


import telebot
import time # for sleep (don't give dice result in second but wait a little)
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
def begin_game(message):

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
    owned_pets = sql_helper.db_get_owned_pets(message.from_user.id)
    print(list(owned_pets))
    #markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    for p in owned_pets:
        print(p)
        e = str(pet_emoji(p[1]))
        #btn = types.KeyboardButton(e)

        btn = types.InlineKeyboardButton(e,callback_data=p[0])
        markup.add(btn)
    bot.send_message(message.from_user.id, "Ваши питомцы на кнопках.", reply_markup=markup)  
    bot.register_next_step_handler(message, pet_details)

@bot.callback_query_handler(func=lambda call: True)
def pet_details(call):
    print(' - - pet detail func -- : ')
    #print(call)
    sql_helper.db_pet_info(call.data)
    bot.send_message(call.from_user.id, 'What next?')
    #pet_info = sql_helper.db_pet_info(message.text)

# buttons test
@bot.message_handler(commands=['earn_money'])
def do_work(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("⛏ Искать клад")
    btn2 = types.KeyboardButton("⚒ Работать")
    btn3 = types.KeyboardButton("🔙 Назад")
    markup.add(btn1,btn2, btn3)
    bot.send_message(message.from_user.id, "select :", reply_markup=markup)  
    bot.register_next_step_handler(message, search_money)

@bot.message_handler(regexp=".*Работа.*")
def do_work(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("⛏ Искать клад 💪x1")
    btn2 = types.KeyboardButton("⚒ Работать 💪x2")
    btn3 = types.KeyboardButton("🔙 Назад")
    markup.add(btn1,btn2, btn3)
    bot.send_message(message.from_user.id, "Осталось сил :", reply_markup=markup)  
    bot.register_next_step_handler(message, search_money)

def search_money(message):
    if re.match('.*клад.*',message.text):
        tid = message.from_user.id
        d = types.Dice(2,'🎯')
        print(d)
        sql_helper.db_stamina_down(tid, 1)
        bot.register_next_step_handler(message, do_work)
        m = bot.send_dice(tid,'🎲')
        dig_result = m.dice.value
        if dig_result < 5:
            time.sleep(4)
            bot.send_message(tid,'💩 Неповезло, вы ничего не нашли!')
        elif dig_result == 5:
            bot.send_message(tid,'Ура! Клад! 💰 x 1')
            time.sleep(4)
            sql_helper.db_add_money(tid,1)
        elif dig_result == 6:
            time.sleep(4)
            bot.send_message(tid,'Ура! Клад! 💰 x 2')
            sql_helper.db_add_money(tid,1)

    elif re.match('.*Работа.*',message.text):
        bot.reply_to(message, 'work option')
    else:
        print('-- search money none --')
        echo_all(message)

def treasure_dice_result(message):
    print(' - - - treasure dice result ---')
    print(message.dice)

def step_two(message):
    if re.match('.*pet.*',message.text):
        bot.reply_to(message, 'pet option')
    else:
        bot.reply_to(message, 'test option')

# legacy func from previous project
@bot.message_handler(regexp=".*(shit).*")
def attach_ls(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton('show pets'))
    msg = bot.send_message(message.chat.id, "choose type shit", reply_markup=markup)

def pet_emoji(id):
    if id == 1:
        e = "🥚"
    elif id == 2:
        e = "🐭"
    elif id == 3:
        e = "🕷"
    elif id == 4:
        e = "🐈"
    else:
        e = "❌"
    return e


def pet_shop(message):
    print('---------- PET SHOP -----------')
    tid = message.from_user.id
    # define location to show specific shop
    location =  sql_helper.db_check_location(tid)
    if location == 5:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🥚 Яйцо 💰 1",)
        btn2 = types.KeyboardButton("🐭 Мышь 💰 3")
        btn3 = types.KeyboardButton("🕷 Паук 💰 5")
        btn4 = types.KeyboardButton("🐈 Кот 💰 9")
        btn_back = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn2,btn3,btn4,btn_back)
    else:
        print('- - - - UNKNOWN LOCATION  - - - - -')
    bot.send_message(tid, 'Выберите питомца:', reply_markup=markup)  
    bot.register_next_step_handler(message, buy_pet)

def buy_pet(message):
    print(' - - - buy pet - - - ')
    if re.match('.*Яйцо.*',message.text):
        sql_helper.db_buy_pet(message.from_user.id, 1)
    elif re.match('.*Мышь.*',message.text):
        sql_helper.db_buy_pet(message.from_user.id, 2)
    elif re.match('.*Паук.*',message.text):
        sql_helper.db_buy_pet(message.from_user.id, 3)
    elif re.match('.*Кот.*',message.text):
        sql_helper.db_buy_pet(message.from_user.id, 4)  
    else:
        print('noting ...')

def travel(message):
    print('- - - TO DO ---')

def next_option(message):
    print('-- -- NEXT option ----')
    if re.match('.*Питомцы.*',message.text):
        bot.register_next_step_handler(message, show_pets)
    elif re.match('.*Имущество.*',message.text):
        bot.reply_to(message, 'test option')
    elif re.match('.*Работа.*',message.text):
        print(' - - work select - -')
        do_work(message)
    elif re.match('.*Магазин.*',message.text):
        bot.register_next_step_handler(message, pet_shop)
    elif re.match('.*Путешествие.*',message.text):
        bot.register_next_step_handler(message, travel)

def get_statistics(tid):
    pet_cnt = sql_helper.db_check_owned_pets(tid)
    pinfo = sql_helper.db_get_player_info(tid)
    lvl = pinfo[1]
    coins = pinfo[0]
    stamina = pinfo[2]
    player_stats = 'Уровень 🎓:' + str(lvl) + '\nСила 💪: ' + str(stamina) +'\nПитомцы 😺: ' + str(pet_cnt) + '\nДеньги 💰: ' + str(coins)

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
    btn5 = types.KeyboardButton("✈ Путешествие")
    markup.add(btn1,btn2,btn3,btn4,btn5)
    bot.send_message(tid, get_statistics(tid), reply_markup=markup)
    bot.register_next_step_handler(message, next_option)

bot.infinity_polling()

