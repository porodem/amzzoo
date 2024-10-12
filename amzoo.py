#telegram zoo game

import telebot
import time # for sleep (don't give dice result in second but wait a little)
import re
import sql_helper
# https://pypi.org/project/emoji/
import emoji

from datetime import datetime, timedelta
from telebot import types
from telebot.util import update_types, quick_markup
from pprint import pprint # to investigate what inside objects
import threading # for parallel timer in difrent tasks like pet hunger timer

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

# Timer for all pets to get hunger every 8 hours (28000 sec)
hunger_interval = 8

def get_hunger():
    while True:
        print("- - -  get hunger - - - ")
        sql_helper.db_change_hunger_all()
        time.sleep(hunger_interval * 60 * 60)

thread_hunger = threading.Thread(target=get_hunger)
thread_hunger.daemon = True # This makes sure the thread will exit when the main program does
thread_hunger.start()



# while True:
#     get_hunger()
#     time.sleep(hunger_interval)


# new game
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

# ----------   SHOW PETS 

#TODELETE - DEPRICATED
# @bot.message_handler(commands=['show_pets'])
# def show_pets_old(message):
#     owned_pets = sql_helper.db_get_owned_pets(message.from_user.id)
#     print(list(owned_pets))
#     #markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     markup = types.InlineKeyboardMarkup()
#     markup.row_width = 2
#     btn_pack = []
#     first_pet = owned_pets[0]
#     pet_info = sql_helper.db_pet_info(first_pet[0])
#     btn_lbl = pet_emoji(pet_info[1]) + ' сытость: ' + pet_info[2]  
#     # for p in owned_pets:
#     #     print(p)
#     #     cbdata = 'pet' + str(p[0])
#     #     e = str(pet_emoji(p[1]))
#     #     #btn = types.KeyboardButton(e)

#     #     btn = types.InlineKeyboardButton(e,callback_data=cbdata)
#     #     btn_back = types.InlineKeyboardButton(e,callback_data=cbdata)
#     #     markup.add(btn,btn2)
#     cidx = 0
#     next_cid = 0 if cidx == len(owned_pets) - 1 else cidx + 1
#     btn = types.InlineKeyboardButton('◀')
#     btn2 = types.InlineKeyboardButton('▶')
#     markup.add(btn,btn2)
#     bot.send_message(message.from_user.id, btn_lbl, reply_markup=markup)  
#     bot.register_next_step_handler(message, pet_details)

@bot.callback_query_handler(lambda query: 'pet' in query.data )
def show_pets(query):
    print(' - - show pets function (callback) -- : ')
    if hasattr(query,'data'):
        cidx = int(query.data[-1:])
    else:
        cidx = 0
    print('cidx: ' + str(cidx))
    owned_pets = sql_helper.db_get_owned_pets(query.from_user.id)
    print('owned_pets: ')
    print(list(owned_pets))
    next_cid = 0 if cidx == len(owned_pets) - 1 else cidx + 1
    first_pet = owned_pets[cidx]
    pet_info = sql_helper.db_pet_info(first_pet[0])
    print('pet_info: ')
    print(list(pet_info))
    mood = define_mood(pet_info)
    habitat = habitat_emoji(pet_info[6])
    meal_emj = "🍗" if pet_info[7] == 3 else "🥗"
    btn_lbl = pet_emoji(pet_info[1]) + f"\nнастроение: {mood} \nсытость {meal_emj}: " + str(pet_info[2]) + f"\nздоровье ♥: {pet_info[3]} \nобитает: {habitat}"     
    markup = types.InlineKeyboardMarkup(row_width=2)
    # TODO add SHOW (petting) animated emoji button, FEED button, CURE (heal) button
    if len(owned_pets) > 1:
        btn_backward = types.InlineKeyboardButton('◀',callback_data="pet" + str(cidx-1))
        btn_forward = types.InlineKeyboardButton('▶',callback_data="pet" + str(next_cid))
    btn_feed = types.InlineKeyboardButton('🍽',callback_data="feed" + str(pet_info[0]))

    if len(owned_pets) > 1:
        markup.add(btn_backward, btn_forward, btn_feed)
    else:
        markup.add(btn_feed)

    if hasattr(query,'data'):
        bot.edit_message_text(
            text=btn_lbl,
            chat_id=query.message.chat.id,
            message_id=query.message.id,
            reply_markup=markup
        )
    else:
        bot.send_message(query.from_user.id, btn_lbl, reply_markup=markup)



@bot.callback_query_handler(func=lambda call: 'feed' in call.data)
def pet_feeding(call):
    print(' - - pet feed -- : ')
    pet_id = extract_numbers(call.data)
    pet_info = sql_helper.db_pet_info(pet_id)
    animal_id = pet_info[1]
    print('animal id: ' + str(animal_id))
    sql_helper.db_change_hunger(pet_id, True, 10)
    bot.send_message(call.from_user.id, '😋')

# - - - - - - SHOP  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@bot.message_handler(regexp=".*Магазин.*")
def shop_select(message):
    print('---------- SELECT SHOP -----------')
    tid = message.from_user.id
    # define location to show specific shop
    location =  sql_helper.db_check_location(tid)
    if location == 5:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Зоомагазин 🐇",)
        btn2 = types.KeyboardButton("Рынок 🏪",)
        btn_back = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn2,btn_back)
    else:
        print('- - - - UNKNOWN LOCATION  - - - - -')
    bot.send_message(tid, 'Куда пойдем?:', reply_markup=markup)  
    bot.register_next_step_handler(message, to_shop)

def to_shop(message):
    print('- - to shop - - ')
    if re.match('.*Зоо.*',message.text):
        
        
        
        pet_shop(message)
    elif re.match('.*Рынок.*', message.text):
        print('- - - bazar selected - - - ')
    else:
        echo_all(message)

def pet_shop(message):
    print('---------- PET SHOP -----------')
    tid = message.from_user.id
    # define location to show specific shop
    location =  sql_helper.db_check_location(tid)

    if location == 5:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        
        pet_space = sql_helper.db_get_player_info(message.from_user.id)[4]
        owned = sql_helper.db_check_owned_pets(message.from_user.id)
        if owned == pet_space: 
            bot.send_message(message.from_user.id,"Нет места для новых питомцев ☹")
            btn_sell = types.KeyboardButton("Продать ")
            btn_back = types.KeyboardButton("🔙 Назад")            
            markup.add(btn_sell,btn_back)
            bot.register_next_step_handler(message,sell_pets(message) )
        else:
            btn1 = types.KeyboardButton("🥚 Яйцо 💰 1",)
            btn2 = types.KeyboardButton("🐭 Мышь 💰 3")
            btn3 = types.KeyboardButton("🕷 Паук 💰 5")
            btn4 = types.KeyboardButton("🐈 Кот 💰 9")
            btn5 = types.KeyboardButton("🐢 Черепаха 💰 15")
            btn6 = types.KeyboardButton("🦃 Индюк 💰 20")
            btn_sell = types.KeyboardButton("Продать ")
            btn_back = types.KeyboardButton("🔙 Назад")
            markup.add(btn1,btn2,btn3,btn4,btn5,btn6,btn_sell,btn_back)
            bot.send_message(tid, 'Выберите питомца:', reply_markup=markup)
            bot.register_next_step_handler(message, buy_pet)
    elif location == 3:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        
        pet_space = sql_helper.db_get_player_info(message.from_user.id)[4]
        owned = sql_helper.db_check_owned_pets(message.from_user.id)
        if owned == pet_space: 
            bot.send_message(message.from_user.id,"Нет места для новых питомцев ☹")
            btn_sell = types.KeyboardButton("Продать ")
            btn_back = types.KeyboardButton("🔙 Назад")            
            markup.add(btn_sell,btn_back)
            bot.register_next_step_handler(message,sell_pets(message) )
        else:
            btn1 = types.KeyboardButton("🦔 Ёж 💰 15",)
            btn2 = types.KeyboardButton("🦉 Сова 💰 20")
            btn3 = types.KeyboardButton("🦇 Летучая мышь 💰 25")
            btn4 = types.KeyboardButton("🦝 Енот 💰 30")
            btn_sell = types.KeyboardButton("Продать ")
            btn_back = types.KeyboardButton("🔙 Назад")
            markup.add(btn1,btn2,btn3,btn4,btn_sell,btn_back)
            bot.send_message(tid, 'Выберите питомца:', reply_markup=markup)
            bot.register_next_step_handler(message, buy_pet)
    else:
        print('- - - - UNKNOWN LOCATION  - - - - -')
      
    

def buy_pet(message):
    print(' - - - buy pet - - - ')
    coins = sql_helper.db_get_player_info(message.from_user.id)
    if re.match('.*Яйцо.*',message.text):
        ok = sql_helper.db_buy_pet(message.from_user.id, 1)
        if ok:
            bot.send_message(message.from_user.id, "🎉 Петомец куплен!")
        else:
            bot.send_message(message.from_user.id, "❌ Нехватает денег!")
    elif re.match('.*Мышь.*',message.text):
        ok = sql_helper.db_buy_pet(message.from_user.id, 2)
        if ok:
            bot.send_message(message.from_user.id, "🎉 Петомец куплен!")
        else:
            bot.send_message(message.from_user.id, "❌ Нехватает денег!")
    elif re.match('.*Паук.*',message.text):
        ok = sql_helper.db_buy_pet(message.from_user.id, 3)
        if ok:
            bot.send_message(message.from_user.id, "🎉 Петомец куплен!")
        else:
            bot.send_message(message.from_user.id, "❌ Нехватает денег!")
    elif re.match('.*Кот.*',message.text):
        ok = sql_helper.db_buy_pet(message.from_user.id, 4)
        if ok:
            bot.send_message(message.from_user.id, "🎉 Петомец куплен!")
        else:
            bot.send_message(message.from_user.id, "❌ Нехватает денег!")
    elif re.match('.*Черепаха.*',message.text):
        ok = sql_helper.db_buy_pet(message.from_user.id, 5)
        if ok:
            bot.send_message(message.from_user.id, "🎉 Петомец куплен!")
        else:
            bot.send_message(message.from_user.id, "❌ Нехватает денег!")
    elif re.match('.*Индюк.*',message.text):
        ok = sql_helper.db_buy_pet(message.from_user.id, 6)
        if ok:
            bot.send_message(message.from_user.id, "🎉 Петомец куплен!")
        else:
            bot.send_message(message.from_user.id, "❌ Нехватает денег!")
    elif re.match('.*Ёж.*',message.text):
        ok = sql_helper.db_buy_pet(message.from_user.id, 7)
        if ok:
            bot.send_message(message.from_user.id, "🎉 Петомец куплен!")
        else:
            bot.send_message(message.from_user.id, "❌ Нехватает денег!")
    elif re.match('.*Сова.*',message.text):
        ok = sql_helper.db_buy_pet(message.from_user.id, 8)
        if ok:
            bot.send_message(message.from_user.id, "🎉 Петомец куплен!")
        else:
            bot.send_message(message.from_user.id, "❌ Нехватает денег!")
    elif re.match('.*Летучая.*',message.text):
        ok = sql_helper.db_buy_pet(message.from_user.id, 9)
        if ok:
            bot.send_message(message.from_user.id, "🎉 Петомец куплен!")
        else:
            bot.send_message(message.from_user.id, "❌ Нехватает денег!")
    elif re.match('.*Енот.*',message.text):
        ok = sql_helper.db_buy_pet(message.from_user.id, 10)
        if ok:
            bot.send_message(message.from_user.id, "🎉 Петомец куплен!")
        else:
            bot.send_message(message.from_user.id, "❌ Нехватает денег!")
    elif re.match('.*Продать.*',message.text):
        pet_list = sql_helper.db_get_owned_pets(message.from_user.id)
        if len(pet_list) == 0:
            bot.send_message(message.from_user.id, "🚫 У вас нет питомцев!")
            #time.sleep(1)
            echo_all(message)
        else:
            sell_pets(message)  
    else:
        echo_all(message)

def sell_pets(message):
    print('- - - - sell pets function - - - - ')
    owned_pets = sql_helper.db_get_owned_pets(message.from_user.id)
    #print(list(owned_pets))
    #markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_pack = []
    for p in owned_pets:
        print(p)
        pet_price = str(int(p[2] / 2)) # sell price its original price / 2
        emj = str(pet_emoji(p[1]) + " 💰+" + pet_price)
        cb_prefix = 'sel'
        btn = types.InlineKeyboardButton(emj,callback_data=cb_prefix + str(p[0]))
        btn_pack.append(btn)
        print(type(btn_pack))
    # very interesting and useful trick with asterisk (*) operator https://www.geeksforgeeks.org/python-star-or-asterisk-operator/
    markup.add(*btn_pack)
    bot.send_message(message.from_user.id, "Кого продать?", reply_markup=markup)  
    bot.register_next_step_handler(message, echo_all)

@bot.callback_query_handler(lambda query: 'sel' in query.data )
def pet_selling(query):
    print(' - - pet sell func -- : ')
    #pet_it = query.data[-1:]
    pet_it = extract_numbers(query.data)
    sql_helper.db_sell_pet(pet_it)    
    bot.answer_callback_query(query.id,text='You sold pet')
    bot.send_message(query.from_user.id, "Петомец продан")

#  - - - - - - - - - - - - E A R N I N G  M O N E Y  - - - - - - - - - - - - - - - - - -

# TODO rename all work mentions to getmoney
@bot.message_handler(regexp=".*Работа.*")
def do_work(message):
    print(' - - - do work - - -')
    tid = message.from_user.id
    stamina = sql_helper.db_get_player_info(message.from_user.id)[2]
    if stamina == 0:
        stamina = check_relax(tid)
    else:
        print('nothing')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if stamina == 1:
        btn1 = types.KeyboardButton("🎲 удачный кубик 💪x1")
        btn3 = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn3)
        bot.send_message(message.from_user.id, "Твои силы : " + str(stamina), reply_markup=markup) 
        bot.register_next_step_handler(message, search_money)
    elif stamina == 2:
        btn1 = types.KeyboardButton("🎲 удачный кубик 💪x1")
        btn2 = types.KeyboardButton("🎯 удачный дартс 💪x2")
        btn3 = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn2,btn3)
        bot.send_message(message.from_user.id, "Твои силы : " + str(stamina), reply_markup=markup) 
        bot.register_next_step_handler(message, search_money)
    elif stamina > 2:
        btn1 = types.KeyboardButton("🎲 удачный кубик 💪x1")
        btn2 = types.KeyboardButton("🎯 удачный дартс 💪x2")
        btn3 = types.KeyboardButton("🎳 удачный боулинг 💪x3")
        btn_back = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn2, btn3, btn_back)
        bot.send_message(message.from_user.id, "Твои силы : " + str(stamina), reply_markup=markup)
        bot.register_next_step_handler(message, search_money) 
    else:
        bot.send_message(message.from_user.id, "😪 Ты устал, наберись сил :", reply_markup=markup)  
        bot.register_next_step_handler(message, echo_all)

def search_money(message):
    if re.match('.*удачн.*',message.text):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("Ещё")
        markup.add(btn)
        tid = message.from_user.id
        if re.match('.*🎲.*',message.text):
            m = bot.send_dice(tid,'🎲')
            pwr = 1
        elif re.match('.*🎯.*',message.text):
            m = bot.send_dice(tid,'🎯')
            pwr = 2
        elif re.match('.*🎳.*',message.text):
            m = bot.send_dice(tid,'🎳')
            pwr = 3
        #print(d)
        sql_helper.db_stamina_down(tid, pwr)
        bot.register_next_step_handler(message, do_work)
        # m = bot.send_dice(tid,'🎲')
        dig_result = m.dice.value
        if dig_result < 5:
            # TODO this and other sleep() stops all other players!
            time.sleep(4)
            bot.send_message(tid,'💩 Неповезло, бывает!',  reply_markup=markup)
        elif dig_result == 5:
            time.sleep(4)
            bot.send_message(tid,'Ура! Приз! 💰 x 1')
            sql_helper.db_add_money(tid,1)
        elif dig_result == 6:
            time.sleep(4)
            bot.send_message(tid,'Ура! Приз! 💰 x 2')
            sql_helper.db_add_money(tid,2)

    elif re.match('.*Работа.*',message.text):
        m = bot.send_dice(tid,'🎳')
        bot.reply_to(message, 'work option')
    else:
        print('-- search money none --')
        echo_all(message)

def treasure_dice_result(message):
    print(' - - - treasure dice result ---')
    print(message.dice)

def check_relax(tid):
    info = sql_helper.db_get_player_info(tid)
    last_work = info[3]
    stamina_before = info[2]
    if stamina_before == 10:
        return
    print('last work: ' + str(last_work))
    print('- ts -')
    #ts = datetime.fromisoformat(last_work)
    #print(ts)
    time_diff = datetime.now() - last_work
    print('time dif:' + str(time_diff))
    hours_rest = time_diff.days * 24 + time_diff.seconds // 3600
    print('hours: ' + str(hours_rest))
    if hours_rest > 0:
        if hours_rest > 8: 
            print('hours over 8 - -')
            profit = sql_helper.db_get_profit(tid)  
            bot.send_message(tid,"Доход зоопарка 💰 " + str(profit))
        hours_rest = hours_rest if (hours_rest + stamina_before) < 11 else 10 - stamina_before
        print('hours rest ' + str(hours_rest))
        sql_helper.db_stamina_up(tid,hours_rest)
    else:
        print('hours rest ' + str(hours_rest) + 'not enough')
    return hours_rest

def travel(message):
    print('- - - TO DO ---')

# - - - - - - -  U T I L S - - - - - - - 

def extract_numbers(str):
    numbers = re.findall(r'\d+',str)
    print('extracted: ' + numbers[0])
    return numbers[0]


def pet_emoji(id):
    if id == 1:
        e = "🥚"
    elif id == 2:
        e = "🐭"
    elif id == 3:
        e = "🕷"
    elif id == 4:
        e = "🐈"
    elif id == 5:
        e = "🐢"
    elif id == 6:
        e = "🦃"
    elif id == 7:
        e = "🦔"
    elif id == 8:
        e = "🦉"
    elif id == 9:
        e = "🦇"
    elif id == 10:
        e = "🦝"
    elif id == 0:
        e = "☠"
    else:
        e = "❌"
    return e

# values(1,'desert'),(2,'field'),(3,'forest'),(4,'water'),(5,'any')
def habitat_emoji(id):
    if id == 1:
        e = "🏜"
    elif id == 2:
        e = "🛣" # maby don't use at all
    elif id == 3:
        e = "🌲"
    elif id == 4:
        e = "🌊"
    else:
        e = "🌐"
    return e


def define_mood(pet: list, environment: list=None):
    hunger = pet[2]
    health = pet[3]
    habitat = pet[6]
    sum_points = hunger + health
    mood = "😐"
    if hunger == 0 or health == 1:
        mood = "😢"
    elif sum_points < 5:
        mood = "🙁"
    elif sum_points < 8:
        mood = "😐"
    elif sum_points >  12:
        mood = "🙂"
    elif sum_points > 16:
        mood = "☺"
    return mood

# - - - - - - -  M A I N  M E N U  - - - - - - - 

def next_option(message):
    print('-- -- NEXT option ----')
    if re.match('.*Питомцы.*',message.text):
        #bot.register_next_step_handler(message, show_pets)
        show_pets(message)
    elif re.match('.*Имущество.*',message.text):
        bot.reply_to(message, 'test option')
    elif re.match('.*Деньги.*',message.text):
        print(' - - work select - -')
        do_work(message)
    elif re.match('.*Магазин.*',message.text):
        bot.register_next_step_handler(message, shop_select)
    elif re.match('.*Путешествие.*',message.text):
        bot.register_next_step_handler(message, travel)

def get_statistics(tid):
    pet_cnt = sql_helper.db_check_owned_pets(tid)
    check_relax(tid)
    pinfo = sql_helper.db_get_player_info(tid)
    lvl = pinfo[1]
    coins = pinfo[0]
    stamina = pinfo[2]    
    pet_space = pinfo[4]
    player_stats = 'Уровень 🎓:' + str(lvl) + '\nСила 💪: ' + str(stamina) +'\nПитомцы 😺: ' + str(pet_cnt) + ' / ' + str(pet_space) + '\nДеньги 💰: ' + str(coins)

    return player_stats



#anything other messages
@bot.message_handler(func=lambda m:True)
def echo_all(message):
    print('---------- ANYTHING -----------')
    tid = message.from_user.id
 
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🐇 Питомцы")
    btn2 = types.KeyboardButton("🏫 Имущество")
    btn3 = types.KeyboardButton("💸 Деньги")
    btn4 = types.KeyboardButton("🛒 Магазин")
    btn5 = types.KeyboardButton("✈ Путешествие")
    markup.add(btn1,btn3,btn4,btn5)
    bot.send_message(tid, get_statistics(tid), reply_markup=markup)
    #bot.register_next_step_handler(message, next_option)
    next_option(message)

bot.infinity_polling()


