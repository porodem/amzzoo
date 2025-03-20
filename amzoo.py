#telegram zoo game

import telebot
import time # for sleep (don't give dice result in second but wait a little)
import re
import sql_helper
from  zoo_emoji import *
import random # for flu illnes
import math

from datetime import datetime, timedelta
from telebot import types, apihelper
from telebot.util import update_types, quick_markup
from pprint import pprint # to investigate what inside objects
import threading # for parallel timer in difrent tasks like pet hunger timer
from pathlib import Path
from collections import defaultdict # anticheat - protect from very frequently messages

print('- - - - - S T A R T E D - - - - - - ')

f = open("token_test.txt","r")
token = f.readline()
token = token.rstrip() # read about function
print(token, type(token))
master_tid = f.readline()
master_tid = int(master_tid.rsplit()[0])
f.close()
bot = telebot.TeleBot(token, parse_mode=None)

with open("update_note.md", 'r', encoding='utf-8') as f:
    note_text = f.readlines()

with open("game_help.md", 'r', encoding='utf-8') as f:
    help_text = f.readlines()
#print(list(note_text))

# Rate limit configuration
MESSAGE_LIMIT = 4  # Maximum number of messages allowed
TIME_WINDOW = 5   # Time window in seconds

# Dictionary to keep track of user message counts and timestamps
user_message_count = defaultdict(lambda: {'count': 0, 'first_time': time.time()})

c_start = types.BotCommand('start','Начать')
help_command = types.BotCommand('show_help','Справка')
patch_notes_command = types.BotCommand('patch_notes','Что нового')
feedback = types.BotCommand('feedback','Написать разработчику')
#main_menu = types.BotCommand('main_menu','Меню')
#main_menu = types.BotCommand('earn_money','Найти деньги')
bot.set_my_commands([help_command, patch_notes_command, feedback])

@bot.message_handler(commands=['show_help','patch_notes','feedback'])
def show_help(message):
    print('000000')
    print(message.text)
    if message.text == '/show_help':
        #bot.send_message(message.from_user.id, ''.join(help_text), parse_mode='markdown' )
        game_guide(message)
    elif message.text == '/patch_notes':
        print('-------- NOTE SHOW')
        bot.send_message(message.from_user.id, ''.join(note_text), parse_mode='markdown' )
    elif message.text == '/feedback':
        print('-- feedback option')
        bot.send_message(message.from_user.id, "Напишите сообщение и отправьте (💰-3):")        
        bot.register_next_step_handler(message, send_feedback)

def send_feedback(message):
    sql_helper.db_save_feedback(message.from_user.id, 0, message.text)
    coins = sql_helper.db_check_owned_coins(message.from_user.id)
    if coins < 3:
        bot.send_message(message.from_user.id, '💰 Нужно 3 монеты. Попробуйте сыграть в мини-играх 🍀')
    else:
        if len(message.text) > 10: 
            sql_helper.db_remove_money(message.from_user.id,3)
            bot.send_message(message.from_user.id, '📨 Сообщение разработчику отправлено! -3💰')
            bot.send_message(master_tid, message.text)
        else:
            bot.send_message(message.from_user.id, 'Слишком короткое сообщение')

@bot.message_handler(commands=['announce'])
def admin_announce(message):
    print('annou')
    if (message.from_user.id == master_tid):
        all_players = sql_helper.db_get_all_tids()
        announce_text = 'empty' if len(message.text[10:]) == 0 else message.text[10:]
        #bot.send_message(master_tid, announce_text) # testing line for developer only
        for player in all_players:
            print('ANNOUNCE to: ' + str(player))
            try:
                bot.send_message(player, announce_text)
            except apihelper.ApiTelegramException:
                sql_helper.db_blocker_player(player)
                print('announce Error: Fucking dickhed banned this bot ' + str(player))
    else:
        bot.send_message(message.from_user.id, "Restricted! It is admin function only!")
        print(f"announce: {master_tid} " + str(message.from_user.id))

# Timer for all pets to get hunger every 8 hours (28000 sec)
hunger_interval = 4

def get_hunger():


    while True:
        print(str(datetime.now()) + f";GET_HUNGER" )

        previous_epidemic_day = None
        previous_fire_day = None    
        prev_refil_pits_day = None
        prev_asteroid_month = None
        is_asteroid = False
        target_location = 0
        #prev_refil_pits_day = int(sql_helper.event_get('refill')[1])
        today = datetime.now().day
        print(f"EVENT STATES: {prev_refil_pits_day} and today: {today}")

        if prev_refil_pits_day == today:
                print('TEST OK')
                is_refiling_pits = False

        prev_asteroid_month = int(sql_helper.event_get('asteroid')[2])
        this_month = datetime.now().month

        # asteroid alarm
        asteroid_chance = random.randrange(1,100)
        print(f"asteroid_chance: {asteroid_chance};{datetime.now()}")
        if asteroid_chance > 85 and 8 < datetime.now().hour < 19:
            is_asteroid = True

        if prev_asteroid_month == this_month:
                is_asteroid = False

        if is_asteroid:
            target_location = random.randrange(1,8) 
            target_location = 4 if target_location == 2 else target_location
            tloc_icon = habitat_emoji(target_location)
            astronomers = sql_helper.tech_players_with(1,tech_lvl_req=1)
            print(f"astronomers: {astronomers}")
            for a in astronomers:
                try:
                    bot.send_message(a[0], f"☄️ Внимание! Обнаружен опасный астероид! Расчетное место падения: {tloc_icon}. Астероид упадет примерно через {hunger_interval} часа.")
                except apihelper.ApiTelegramException:
                    print('ERROR notify dead of hunger ' + str(player[0]) )

        time.sleep(hunger_interval * 60 * 60)
        #time.sleep(hunger_interval * 4)
        hungry_animals = sql_helper.db_change_hunger_all()
        for player in hungry_animals:
            print(list(player))
            health = player[2]
            if player[1] == 0:
                try:
                    bot.send_message(player[0], pet_emoji(player[1]) + " Один из питомцев умер 😥")
                except apihelper.ApiTelegramException:
                    print('ERROR notify dead of hunger ' + str(player[0]) )
            elif health < 6:
                try:
                    bot.send_message(player[0],f"Ваш {pet_emoji(player[1])} заболел! Срочно вылечите его!💊 ")
                except apihelper.ApiTelegramException:
                    print('ERROR notify ill of hunger ' + str(player[0]) )
            else:
                try:
                    bot.send_message(player[0],f"Ваш {pet_emoji(player[1])} голоден! Покормите его!")
                except apihelper.ApiTelegramException:
                    print('ERROR notify hunger ' + str(player[0]) )
        
        prev_refil_pits_day = int(sql_helper.event_get('refill')[1])
        previous_epidemic_day = int(sql_helper.event_get('epidemic')[1])
        previous_fire_day = int(sql_helper.event_get('fire')[1])

        today = datetime.now().day  
        
        
        if is_asteroid:
            print('ASTEROID_EXECUTION')
            sql_helper.event_exe('asteroid')
            
            victims = sql_helper.db_get_nearby_players(target_location)
            print("victim list:")
            # TODO hit pets more lethal 
            sql_helper.db_infect_pets(target_location) 
            for v in victims:
                tid = v[0]
                uname = v[1]
                print(f"{uname} gets asteroid damage")
                dmg_percent = 25
                impact_damage = int(dmg_percent / 100 * sql_helper.db_get_player_info(tid)[0])
                sql_helper.db_remove_money(tid,impact_damage)
                try:
                    bot.send_message(tid,"☄️ Тревога! Неожидано с неба упал астероид! Ваши животные и имущество пострадали! Если бы вы обнаружили астероид заранее, возможно вы бы знали куда он упадет.")
                except apihelper.ApiTelegramException:
                    print('ERROR notify ill of hunger ' + str(player[0]) )
        else:
            print('this month asteroid was already')
        
        # if is_asteroid and datetime.now().hour > 8:
        #     print('ASTEROID')
        #     sql_helper.event_exe('asteroid')
            
        #     victims = sql_helper.db_get_nearby_players(target_location)
        #     print("victim list:")
        #     sql_helper.db_infect_pets(target_location)
        #     for v in victims:
        #         tid = v[0]
        #         uname = v[1]
        #         print(f"{uname} gets asteroid damage")
        #         dmg_percent = 25
        #         impact_damage = int(dmg_percent / 100 * sql_helper.db_get_player_info(tid)[0])
        #         sql_helper.db_remove_money(tid,impact_damage)
        # else:
        #     print('this month asteroid was already')

        
        is_epidemic = today % 9 == 0 # every 9 18 21 day of month
        if previous_epidemic_day == today:
            print('epidemic today was already executed')
            is_epidemic = False

        is_fire = today % 7 == 0
        if previous_fire_day == today:
            is_fire = False

        is_refiling_pits = today % 5 == 0
        if prev_refil_pits_day == today:
            is_refiling_pits = False

        if is_refiling_pits:
            print("REFILING HOLES")
            sql_helper.event_exe('refill')
            #prev_refil_pits_day = today
            sql_helper.db_refil_pits()
            
        # WARNING if bot restarts epidemic executes again !
        if is_epidemic:
            print(f" - - - - - E P I D E M I C today: {today}")
            #previous_epidemic_day = today
            sql_helper.event_exe('epidemic')
            infected_pets = sql_helper.db_infect_pets()
            players = []
            for p in infected_pets:
                print('player: ' + str(p[0]))
                try:
                    bot.send_message(p[0],'🦠 Эпидемия! Проверьте питомцев!')
                except apihelper.ApiTelegramException:
                        print('EXEPTION tid error')
                players.append(p[0])
            print(list(infected_pets))

        if is_fire:
            print(f" - - - - - fire FIRE today: {today}")
            dmg_percent = 15
            #previous_fire_day = today
            sql_helper.event_exe('fire')
            burned_tids = sql_helper.db_get_all_tids()
            begin = random.randrange(0,2) 
            friquency = 3 # every this number select tid for execute fire
            fire_jumps = len(burned_tids) // friquency 
            print(f"begin {begin} jumps {fire_jumps}")
            for i in range(fire_jumps):
                tid = burned_tids[begin]
                
                fire_protect = sql_helper.db_check_owned_item(tid,11) # check if has fire extinguisher
                if fire_protect > 0:
                    print(f"{tid} have fire extinguisher")
                    dmg_percent = 8
                    fire_damage = int(dmg_percent / 100 * sql_helper.db_get_player_info(tid)[0])
                    sql_helper.db_remove_money(tid,fire_damage)
                    try:
                        bot.send_message(tid, f"🔥 Пожар в зоопарке! -{fire_damage}💰")
                    except apihelper.ApiTelegramException:
                        print('EXEPTION tid error')
                    sql_helper.db_remove_property(fire_protect)
                else:
                    print(f"{tid} HAVE NO fire extinguisher")
                    fire_damage = int(dmg_percent / 100 * sql_helper.db_get_player_info(tid)[0])
                    sql_helper.db_remove_money(tid,fire_damage)
                    try:
                        bot.send_message(tid, f"🔥 Пожар в зоопарке! -{fire_damage}💰")
                    except apihelper.ApiTelegramException:
                        print('EXEPTION tid error')
                print(f"Fire {burned_tids[begin]} every {fire_jumps}")
                begin +=friquency


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

        print(message.from_user.__dict__)
        username = message.from_user.first_name if message.from_user.username is None else message.from_user.username

        sql_helper.db_new_player(message.from_user.id,username,'x')

        # show help for new player
        bot.send_message(message.from_user.id, '''Привет!
Зарабатывай деньги в мини играх и покупай 🐇 питомцев.
💪 Сила восстанавливается 1 в час.
✈ Путешествуй чтобы купить других животных!
💰 Каждый следующий день, ты получишь доход если у тебя есть питомцы и вчера ты тратил силы. Больше информации смотри в меню Справка''')
        bot.send_message(message.from_user.id, "Введите код приглашения и нажмите отправить.")
        bot.register_next_step_handler(message, check_invite)
        

    else:

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🐇 Питомцы")
        btn2 = types.KeyboardButton("🏫 Имущество")
        btn3 = types.KeyboardButton("⚒ Работа")
        btn4 = types.KeyboardButton("🛒 Магазин")
        markup.add(btn1,btn2,btn3,btn4)
        bot.send_message(message.from_user.id, "select :", reply_markup=markup)  
        bot.register_next_step_handler(message, search_money)

def check_invite(message):
    invite_tid = message.text
    if re.match('^\d{9,10}$',invite_tid):
        ex = sql_helper.db_check_player_exists(invite_tid)
        if ex is None:
            bot.send_message(message.from_user.id, "❌ код не сработал!")
        else:
            sql_helper.db_get_item(invite_tid,14)
            sql_helper.db_get_item(invite_tid,14)
            sql_helper.db_add_money(message.from_user.id,5)
            bot.send_message(message.from_user.id, "✅ Успешно! +5💰")
            bot.send_message(invite_tid, "Получено 🥫🥫")
        echo_all(message)
    else:
        bot.send_message(message.from_user.id, "❌ код не сработал!")
        echo_all(message)
        #bot.register_next_step_handler(message, check_invite)

@bot.callback_query_handler(lambda query: 'guide' in query.data)
def game_guide(query):
    topics = ['🐣Начало','💰Деньги','🌟Опыт','🏆Рейтинг','😈Преступления','⚠️События','💻Исследования','❔Помощь']
    tid = query.from_user.id
    btns = []
    if hasattr(query,'data'):
        print('guide has data')
        selection = int(extract_numbers(query.data))
        print(f"data:{selection}")
        if selection == 100:
            bot.delete_message(query.message.chat.id, query.message.id)
            return
        elif selection == 0:
            with open("docs/start.txt", 'r', encoding='utf-8') as f:
                help_text = f.readlines()
            bot.delete_message(query.message.chat.id, query.message.id)
            bot.send_message(query.from_user.id, ''.join(help_text), parse_mode='markdown' )
        elif selection == 1:
            with open("docs/money.txt", 'r', encoding='utf-8') as f:
                help_text = f.readlines()
            bot.delete_message(query.message.chat.id, query.message.id)
            bot.send_message(query.from_user.id, ''.join(help_text), parse_mode='markdown' )
        elif selection == 2:
            with open("docs/exp.txt", 'r', encoding='utf-8') as f:
                help_text = f.readlines()
            bot.delete_message(query.message.chat.id, query.message.id)
            bot.send_message(query.from_user.id, ''.join(help_text), parse_mode='markdown' )
        elif selection == 3:
            with open("docs/rating.txt", 'r', encoding='utf-8') as f:
                help_text = f.readlines()
            bot.delete_message(query.message.chat.id, query.message.id)
            bot.send_message(query.from_user.id, ''.join(help_text), parse_mode='markdown' )
        elif selection == 4:
            with open("docs/crime.txt", 'r', encoding='utf-8') as f:
                help_text = f.readlines()
            bot.delete_message(query.message.chat.id, query.message.id)
            bot.send_message(query.from_user.id, ''.join(help_text), parse_mode='markdown' )
        elif selection == 5:
            with open("docs/events.txt", 'r', encoding='utf-8') as f:
                help_text = f.readlines()
            bot.delete_message(query.message.chat.id, query.message.id)
            bot.send_message(query.from_user.id, ''.join(help_text), parse_mode='markdown' )
        elif selection == 6:
            with open("docs/tech.txt", 'r', encoding='utf-8') as f:
                help_text = f.readlines()
            bot.delete_message(query.message.chat.id, query.message.id)
            bot.send_message(query.from_user.id, ''.join(help_text), parse_mode='markdown' )
        else:
            bot.delete_message(query.message.chat.id, query.message.id)
            bot.send_message(query.from_user.id, 'Скоро появится' )
        
    markup = types.InlineKeyboardMarkup(row_width=2)
    counter = 0
    for topic in topics:
        btn = types.InlineKeyboardButton(topic,callback_data=f"guide_{counter}")
        counter +=1
        btns.append(btn)
    btn_exit = types.InlineKeyboardButton('✖️Закрыть',callback_data=f"guide_100")
    markup.add(*btns,btn_exit)
    bot.send_message(tid, 'ℹ️ Справка:',reply_markup=markup)
    #bot.delete_message(query.message.chat.id, query.message.id)


# ----------   SHOW PETS 

@bot.callback_query_handler(lambda query: 'pet' in query.data )
def show_pets(query):
    print(' - - show pets function (callback) -- : ')
    owned_pets = sql_helper.db_get_owned_pets(query.from_user.id)
    total_pets_price = 0
    total_pets_hunger = 0
    total_feed_price = 0
    for pet in owned_pets:
        #total_pets_price = total_pets_price + pet[2]
        #total_pets_hunger += pet[4]
        hunger_x = float(f"0.{pet[4]}") if pet[4] < 10 else 1
        total_feed_price += int(pet[2] / 10) - int(pet[2]/10 * hunger_x)
        print(f"{str(pet[2])} h {pet[4]} total_feed_price {total_feed_price}")
    print(f"total pet price: {total_pets_price} and gunger: {total_pets_hunger}")
    print(str(query.from_user.id) + f" has {len(owned_pets)}")
    if len(owned_pets) == 0:
        bot.send_message(query.from_user.id, "У вас нет питомцев")
        return
    if hasattr(query,'data'):
        cidx = int(extract_numbers(query.data))

        first_pet = owned_pets[cidx]
        pet_info = sql_helper.db_pet_info(first_pet[0])
        animal_id = pet_info[1]
        print('animal id: ' + str(animal_id))

        if int(extract_numbers(query.data,1)) == 1:
            print('feed option')
            feed_price = int(pet_info[8] / 10) - int(pet_info[8]/10 * float(f"0.{pet_info[2]}"))
            coins = sql_helper.db_get_player_info(query.from_user.id)[0]
            if coins < feed_price:
                bot.send_message(query.from_user.id, "❌ не хватает денег!")
                bot.delete_message(query.message.chat.id, query.message.id)
                return
            sql_helper.db_remove_money(query.from_user.id,feed_price)
            sql_helper.db_change_hunger(pet_info[0], True, 10)
            healty = random.randrange(0,9)
            print('healty: ' + str(healty))
            if not healty:
                sql_helper.db_change_health(pet_info[0],False,1)
            bot.send_message(query.from_user.id, pet_emoji(animal_id))
        elif int(extract_numbers(query.data,1)) == 2:
            print('cure option')
            
            antibio = sql_helper.db_check_owned_item(query.from_user.id,5)
            #sql_helper.db_change_health(pet_info[0],cure=True,val=15)
            if sql_helper.tech_done_check(query.from_user.id,3) > 0:
                sql_helper.db_cure_pet(pet_info[0], tech_upgrade=True)
            else:
                sql_helper.db_cure_pet(pet_info[0], tech_upgrade=False)
            sql_helper.db_delete_property(antibio)
            bot.send_message(query.from_user.id, "вылечен")
        elif int(extract_numbers(query.data,1)) == 3:
            print('feed all option')
            #total_feed_price = int(total_pets_price / 10) - int(total_pets_price/10 * float(f"0.{total_pets_hunger}"))
            coins = sql_helper.db_get_player_info(query.from_user.id)[0]
            if coins < total_feed_price:
                bot.send_message(query.from_user.id, "❌ нехватает денег!")
                bot.delete_message(query.message.chat.id, query.message.id)
                echo_all()
            sql_helper.db_remove_money(query.from_user.id,total_feed_price)
            sql_helper.db_feed_all(query.from_user.id)
                
    else:
        cidx = 0
    print('cidx: ' + str(cidx))
    
    #print('owned_pets: ')
    #print(list(owned_pets))
    next_cid = 0 if cidx == len(owned_pets) - 1 else cidx + 1
    first_pet = owned_pets[cidx]
    pet_info = sql_helper.db_pet_info(first_pet[0])
    print('pet_info: ')
    print(list(pet_info))
    mood = define_mood(pet_info)
    feed_price = int(pet_info[8] / 10) - int(pet_info[8]/10 * float(f"0.{pet_info[2]}"))
    print(f"{pet_info[8]} - {pet_info[2]}")
    #total_feed_price = int(total_pets_price / 10) - int(total_pets_price/10 * float(f"0.{total_pets_hunger}"))
    habitat = habitat_emoji(pet_info[6])
    meal_emj = "🍗" if pet_info[7] == 3 else "🥗"
    btn_lbl = pet_emoji(pet_info[1]) + f"\nнастроение: {mood} \nсытость {meal_emj}: " + str(pet_info[2]) + f"\nздоровье ♥: {pet_info[3]} \nобитает: {habitat} \nрейтинг⭐:{pet_info[9]}"     
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_pack = []
    action = '_0'
    # TODO add SHOW (petting) animated emoji button, FEED button, CURE (heal) button
    if len(owned_pets) > 1:
        btn_backward = types.InlineKeyboardButton('◀',callback_data="pet" + str(cidx-1) + action)
        btn_forward = types.InlineKeyboardButton('▶',callback_data="pet" + str(next_cid) + action)
        btn_pack = btn_pack + [btn_backward,btn_forward]
    if pet_info[2] < 10 and pet_info[1] != 0:
        btn_feed = types.InlineKeyboardButton(f"🍽💰{feed_price}",callback_data="pet" + str(cidx) + '_1')
        if len(owned_pets) > 1:
            smart_feed = sql_helper.db_check_owned_item(query.from_user.id, 30)
            if smart_feed > 0:
                btn_feed_all = types.InlineKeyboardButton(f"🍽️🍽️💰{total_feed_price} всех",callback_data="pet" + str(cidx) + '_3')
                btn_pack = btn_pack + [btn_feed_all]
        btn_pack = btn_pack + [btn_feed]
    if pet_info[3] < 10 and pet_info[1] != 0:
        items = sql_helper.db_get_owned_items_group(query.from_user.id)
        have_antibiotic = False
        for i in items:
            print('items:')
            print(i[0])
            if i[0] == 5:
                have_antibiotic = True
                break
        if have_antibiotic:
            btn_cure = types.InlineKeyboardButton('💉',callback_data="pet" + str(cidx) + '_2')
            btn_pack = btn_pack + [btn_cure]

    markup.add(*btn_pack)
    # if len(owned_pets) > 1:
    #     markup.add(*btn_pack)
    # else:
    #     markup.add(btn_feed)

    if hasattr(query,'data'):
        bot.edit_message_text(
            text=btn_lbl,
            chat_id=query.message.chat.id,
            message_id=query.message.id,
            reply_markup=markup
        )
    else:
        bot.send_message(query.from_user.id, btn_lbl, reply_markup=markup)


# - - - - - - SHOP  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@bot.message_handler(regexp=".*Магазин.*")
def shop_select(message):
    print('---------- SELECT SHOP -----------')
    tid = message.from_user.id
    print(f"Buyer {tid}")
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
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Зоомагазин 🐇",)
        btn2 = types.KeyboardButton("Рынок 🏪",)
        btn_back = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn2,btn_back)
    bot.send_message(tid, 'Куда пойдем?:', reply_markup=markup)  
    bot.register_next_step_handler(message, to_shop)

def zoo_management(message):
    tid = message.from_user.id
    #anti_forward(message.from_user.id, message.forward_date)
    if message.forward_date is not None:
        print(f"-- ANTI CHEAT for {str(tid)} - - -- - -- - - - -")
        #print("forward: " + str(message.forward_date))
        penalty = 10
        sql_helper.db_stamina_down(tid,10)
        sql_helper.db_remove_money(tid, penalty)
        bot.send_message(tid, f"⚠ Мошенничество! -{penalty}💰")
        return
    print('- - - ZOO MANAGEMENT - - -')
    #location =  sql_helper.db_check_location(tid)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Питомцы",)
    btn2 = types.KeyboardButton("Безопасность",)
    btn3 = types.KeyboardButton("ℹ️Информация",)
    btn4 = types.KeyboardButton("Пригласить 🙋‍♂️",)
    btn5 = types.KeyboardButton("🌟Возможности",)
    btn_back = types.KeyboardButton("🔙 Назад")
    markup.add(btn1,btn2,btn3,btn4,btn5,btn_back)
    bot.send_message(tid, 'Что вас интересует?:', reply_markup=markup)  
    bot.register_next_step_handler(message, to_zoo_management)

def to_zoo_management(message):
    print('- - to_zoo_management - - ')
    #anti_forward(message.from_user.id, message.forward_date)
    if re.match('Питомцы.*',message.text):           
        show_pets(message)
    elif re.match('Безопасность.*', message.text):
        print('- - - security selected - - - ')
        bot.send_message(message.from_user.id, "Введите только одну цифру! (0-9). Это будет пароль на открытие клетки. При взломе друой игрок попытается её угадать. Если угадает самый дешевый петомец может убежать")
        bot.register_next_step_handler(message, set_cage_password)
    elif re.match('ℹ️.*',message.text):
        print('info_dummy')
    elif re.match('Пригласить.*',message.text):
        bot.send_message(message.from_user.id, "Пригласи друга в игру и попроси его ввести код *" + str(message.from_user.id) + "* и ты получишь 🥫х2 энергетика (+10 💪)!", parse_mode='markdown')
    
    elif re.match('^🌟Возможности.*',message.text):
        stats_up(message)
    else:
        echo_all(message)

def stats_up(message):
    print('-stats')
    tid = message.from_user.id
    bot.send_message(tid, get_statistics(tid))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("⬆️ Улучшения",)
    btn2 = types.KeyboardButton("💻 Исследования",)
    btn_back = types.KeyboardButton("🔙 Назад")
    reserv_energy = sql_helper.db_check_owned_item(message.from_user.id, 14)
    if reserv_energy > 0:
        btn_energy = types.KeyboardButton("Энергетик 💪🥫",)
        markup.add(btn1,btn2,btn_energy,btn_back)
    else:        
        markup.add(btn1,btn2,btn_back)
    map_item = sql_helper.db_check_owned_item(tid,13)
    paleo = sql_helper.tech_done_check(tid,2)
    if map_item and paleo:
        btn_map = types.KeyboardButton("Карта🗺️")
        markup.add(btn_map)
    bot.send_message(tid, 'Что вас интересует?:', reply_markup=markup) 
    bot.register_next_step_handler(message, stats_up_selection)

def stats_up_selection(message):
    print('-stat selection')
    if re.match('.*Исследования.*',message.text):
        do_tech(message)
    elif re.match('.*Улучшения.*', message.text):
        do_ability_up(message)
    elif re.match('Энергетик.*',message.text):
        #increase_stamina(message)
        # TODO maby make inline keyboard in previous method and check there
        e = sql_helper.db_check_owned_item(message.from_user.id, 14)
        if not e:
            bot.send_message(message.from_user.id, "⚠️Мошенничество! Применены штрафы!")
            sql_helper.db_stamina_down(message.from_user.id, 10)
            sql_helper.db_remove_money(message.from_user.id,100)
            return
        stamina_limit = sql_helper.db_get_player_info(message.from_user.id)[8]
        sql_helper.db_stamina_up(message.from_user.id,stamina_limit, stamina_limit)
        sql_helper.db_remove_property(e)
        bot.send_message(message.from_user.id, "💪 Силы восстановлены!")
        echo_all(message)
    elif re.match('Карта.*',message.text):
        m = sql_helper.db_check_owned_item(message.from_user.id, 13)
        paleo = sql_helper.tech_done_check(message.from_user.id,2)
        if not paleo:
            bot.send_message(message.from_user.id, "Требуется навык палеонтологии!")
        if not m:
            bot.send_message(message.from_user.id, "У вас нет карты!")
            return
        sql_helper.db_remove_property(m)
        no_mamont_location = sql_helper.map_no_mamont()
        bot.send_message(message.from_user.id, f"Судя по данных, останков мамонта точно нет в {habitat_emoji(no_mamont_location)}\nВозможно используя данные другой карты 🗺️ можно уточнить местоположение.")
    else:
        echo_all(message)


def set_cage_password(message):
    password = message.text
    if re.match('^\d$',password):
        sql_helper.db_change_zoo_pass(message.from_user.id, password)
        bot.send_message(message.from_user.id, "🔒 Защита 1 уровня включена")
    else:
        bot.send_message(message.from_user.id, "❌ только одну цифру!")
        bot.register_next_step_handler(message, set_cage_password)

@bot.callback_query_handler(lambda query: 'tech' in query.data)
def do_tech(query):
    print('- - TECH - -')
    tid = query.from_user.id 
    available_items = sql_helper.tech_list()
    player_items = sql_helper.db_get_owned_items_group(tid)
    tech_status = ""
    time_left = ""
    state = ""
    already = False
    resourses_required = False
    
    if hasattr(query,'data'):
        #print(query.data)
        cidx = int(extract_numbers(query.data))
        print(f" - {tid} technology research item {cidx} - - - - ")
        action = int(extract_numbers(query.data,1))
        pinfo = sql_helper.db_get_player_info(tid)
        item = available_items[cidx]
        if action == 1: # start learn technology option

            
            required_item = item[6]
            required_coins = item[3]
            bio_ready = sql_helper.tech_done_check(tid,3)
            
            if sql_helper.db_check_owned_item(tid,required_item) and (required_coins <= pinfo[0]):
                # DNA check bones countity
                tech_id = item[0]
                bracheo_bones = 0
                trex_bones = 0
                print(f"TECH try start;{datetime.now()};{tid};owns:{required_item};tech_id:{tech_id}")

                if tech_id in  [4,5]:
                    print(' DNA branch start- - -')
                    if not bio_ready:
                        bot.send_message(tid,"Необходимы знания биологии🦠")
                        bot.delete_message(query.message.chat.id, query.message.id)  
                        return
                        
                    for i in player_items:
                        if i[0] == 40:
                            bracheo_bones = i[2]
                        elif i[0] == 41:
                            trex_bones = i[2]
                    if tech_id == 4:
                        print(f"bracheosaur bones {bracheo_bones}")
                        if bracheo_bones >= 3:
                            sql_helper.tech_player_start(tid,item[0]) 
                            sql_helper.db_remove_money(tid,required_coins) 
                            bone = sql_helper.db_check_owned_item(tid, 40)
                            sql_helper.db_remove_property(bone)
                            bone = sql_helper.db_check_owned_item(tid, 40)
                            sql_helper.db_remove_property(bone)
                        else:
                            tech_status = f"\n⚠️Нужно больше костей 🦕 ({bracheo_bones}/3)🦴"
                            resourses_required = True
                    elif tech_id == 5:
                        print(f"trex bones {trex_bones}")
                        if trex_bones >= 3:
                            sql_helper.tech_player_start(tid,item[0]) 
                            sql_helper.db_remove_money(tid,required_coins) 
                            bone = sql_helper.db_check_owned_item(tid, 41)
                            sql_helper.db_remove_property(bone)
                            bone = sql_helper.db_check_owned_item(tid, 41)
                            sql_helper.db_remove_property(bone)
                        else:
                            tech_status = f"\n⚠️Нужно больше костей 🦖({trex_bones}/3)🦴"
                            resourses_required = True
                elif tech_id == 2: # Paleontology
                    item_map = sql_helper.db_check_owned_item(tid, 13)
                    sql_helper.db_remove_property(item_map)
                elif tech_id in [6,7]:
                    egg_type = 43 if item[0]== 7 else 42
                    owned_egg = sql_helper.db_check_owned_item(tid,egg_type)
                    sql_helper.db_remove_property(owned_egg)
                    sql_helper.tech_player_start(tid,item[0]) 
                    sql_helper.db_remove_money(tid,required_coins)
                else:
                    print('TECH SOMETHING ELSE - - - ')
                     
                    sql_helper.tech_player_start(tid,item[0])  
                    sql_helper.db_remove_money(tid,required_coins)              
            else:
                print(f"{tid} has NO required {required_item}")
                resourses_required = True
                #bot.answer_callback_query(query.id, f"❌ У вас нет {item_emoji(required_item)}") 
                bot.send_message(tid, f"❌ Требуется {item_emoji(required_item)} и {required_coins}💰")
                bot.delete_message(query.message.chat.id, query.message.id)  
                return
        elif action == 2: # Devote stamina for research technology
            stamina = pinfo[2]
            if stamina == 0:
                bot.send_message(tid, f"❌ Нужна сила 💪 чтобы заниматься исследованиями")
                bot.delete_message(query.message.chat.id, query.message.id)  
                return
            else:
                print(f"tech {item[0]} tid {tid} devote stamina")
                sql_helper.db_stamina_down(tid,1)
                sql_helper.tech_player_work(tid, item[0])

    else:
        cidx = 0
    next_cid = 0 if cidx == len(available_items) - 1 else cidx + 1
    item = available_items[cidx]

    in_progress = sql_helper.tech_player_list(tid) #  id, 1 time_start, 2 time_point, 3 stamina_spend, 4 tid, 5 tech_id, 6 lvl (now lvl means complete bcz only 1 lvl exists)
    #print(in_progress)
    for t in in_progress:
        #print(f"{t}")
        if t[5]== item[0]: # If players have start learn tech and its = selected tech
            already = True
            if t[6] > 0:
                tech_status = f"{tech_emoji(t[5]) + item[1]}\n⭐ Исследование завершено \nℹ️Теперь вы способны {item[8]}"
                research_completed = True
            else:
                #time_left = "♾️" if t[3] is None else t[3]
                spend_stamina = t[3]
                required_stamina = item[5]
                this_moment = datetime.now()
                time_rest = str(t[2] - this_moment)
                time_left = "♾️" if t[1] == t[2] or t[2] < this_moment  else time_rest.split('.')[0]
                research_completed = True if t[2] < this_moment and spend_stamina >= required_stamina else False
                if research_completed:
                    # DNA research 
                    if item[0] in [4,5]: 
                        if random.randrange(0,2):   # 50 percent success on revive dinosaur egg
                            print(f"{datetime.now()};{tid};Research COMPLETED;{item[0]}")
                            #sql_helper.tech_done(tid,item[0])
                            trex_egg = 1 if item[0]== 5 else 0
                            if trex_egg:
                                sql_helper.db_get_item(tid,43) # trex
                            else:
                                sql_helper.db_get_item(tid,42) # bracheosaur
                            #stop_type = "⭐ Изучено"
                            sql_helper.tech_reset(tid,item[0])
                            bot.send_message(tid, f"{tech_emoji(t[5]) + item[1]}\n⭐ Исследование завершено \n Вы получили яйцо динозавра!")
                            bot.delete_message(query.message.chat.id, query.message.id) 
                        else:
                            print(f"TECH FAIL obtaining dino egg")
                            sql_helper.tech_reset(tid,item[0])
                            sql_helper.db_exp_up(tid,5)
                    # ALIVE DINO
                    elif item[0] in [6,7]:
                        
                        if random.randrange(0,2):   # 50 percent success on revive dinosaur
                            print(f"{datetime.now()};{tid};Research COMPLETED;{item[0]}")
                            #sql_helper.tech_done(tid,item[0])
                            trex_egg = 1 if item[0]== 7 else 0
                            if trex_egg:
                                sql_helper.db_get_pet(tid,51) # trex
                                dino = "🦖"
                            else:
                                sql_helper.db_get_pet(tid,50) # bracheosaur
                                dino = "🦕"
                            #stop_type = "⭐ Изучено"
                            sql_helper.tech_reset_hard(tid,item[0])
                            bot.send_message(tid, f"{dino}")
                            bot.delete_message(query.message.chat.id, query.message.id) 
                            return
                        else:
                            print(f"TECH FAIL obtaining alive dino")
                            sql_helper.tech_reset_hard(tid,item[0])
                            sql_helper.db_exp_up(tid,3)
                            bot.send_message(tid, f"❌ Неудачная инкубация динозавра")
                            bot.delete_message(query.message.chat.id, query.message.id) 
                            return
                    else:
                        print(f"{datetime.now()};{tid};Research COMPLETED;{item[0]}")
                        sql_helper.tech_done(tid,item[0])
                        #stop_type = "⭐ Изучено"
                        tech_status = f"{tech_emoji(t[5]) + item[1]}\n⭐ Исследование завершено \nℹ️Теперь вы способны {item[8]}"
                else:
                    #stop_type = "🔴 Остановлено"
                    state = "🟢 Активно" if datetime.now() < t[2] else "🔴 Остановлено"
                    tech_status = f"\n⚒️ Вы приступили к исследованию {tech_emoji(t[5])}\n{item[8]}\n💪Сил вложено: {spend_stamina} / {required_stamina} \n⏳ Времени запланировано: {time_left}\nСтатус: {state}"

            

    markup = types.InlineKeyboardMarkup(row_width=2,)

    #TODO add button exit and delete window
    
    if already:
        lbl = tech_status
        if research_completed:
            btn_buy = types.InlineKeyboardButton(f"✖️", callback_data='tech' + str(cidx) + '_0')
        else:
            btn_buy = types.InlineKeyboardButton(f"➖💪", callback_data='tech' + str(cidx) + '_2')
    else:
        lbl = tech_emoji(item[0]) + " " + item[1] + f"\n{item[8]}\n💰{item[3]} ⏳ {item[4]} 💪 {item[5]} \nТребуется:{item_emoji(item[6])} {tech_status}"
        btn_ico = "✖️" if resourses_required else "❇️"
        if resourses_required:
            btn_ico = "✖️"
            act = '_3'
        else:
            btn_ico = "❇️"
            act = '_1'
        btn_buy = types.InlineKeyboardButton(f"{btn_ico}", callback_data='tech' + str(cidx) + act)
    btn_forward = types.InlineKeyboardButton('▶', callback_data='tech' + str(next_cid) + '_0' )
    markup.add(btn_buy,btn_forward)
    if hasattr(query,'data'):
        bot.edit_message_text(
            text=lbl,
            chat_id=query.message.chat.id,
            parse_mode='markdown', # to make some text bold with *this* in messages
            message_id=query.message.id,
            reply_markup=markup
        )
    else:
        bot.send_message(query.from_user.id, lbl,parse_mode='markdown', reply_markup=markup)


@bot.callback_query_handler(lambda query: 'up' in query.data)
def do_ability_up(query):
    
    tid = query.from_user.id 
    #exp_needed = sql_helper.show_lvlup_target(tid)
    available_items = sql_helper.db_upgrade_list(tid)
    points = sql_helper.db_get_player_info(tid)[7]
    print(f"{str(datetime.now())} ABILITY UP {tid} {points}")
    btn_pack = [] 
    if hasattr(query,'data'):
        print(query.data)
        cidx = int(extract_numbers(query.data))
        # -------------------------------------------buy upgrade option -------------------------------------------------------
        if int(extract_numbers(query.data,1)):
            print(f" - {tid} upgrading item {cidx} - - - - ")
            item = available_items[cidx]
            #total_pasports = sql_helper.db_count_item_type(tid,10)
            #extra_price = round(1.0 + (0.6 * total_pasports),2) # ATTENTION THIS FORMULA USED IN TWO PLACES 
            buying_ok = points
            upgrade_ready = True
            if buying_ok:
                if item[0] == 1:
                    sql_helper.db_points_down(tid,item[0])
                    sql_helper.db_stamina_max_up(tid)
                    print(f"stamina_max_up {tid}")
                elif item[0] == 2:
                    sql_helper.db_points_down(tid,item[0])
                    sql_helper.db_change_pet_space(tid,1)
                    print(f"ability up pet_space {tid}")
                elif item[0] == 3:
                    sql_helper.db_points_down(tid,item[0])
                    sql_helper.taming_up(tid,1)
                elif item[0] == 4:
                    sql_helper.db_points_down(tid,item[0])
                    sql_helper.lockpick_up(tid,1)
                elif item[0] == 5:
                    sql_helper.db_points_down(tid,item[0])
                    sql_helper.db_stamina_max_up(tid)
                    print(f"stamina_max_up {tid}")
                elif item[0] == 6:
                    sql_helper.db_points_down(tid,item[0])
                    sql_helper.taming_up(tid,1)
                elif item[0] == 7:
                    sql_helper.db_points_down(tid,item[0])
                    sql_helper.lockpick_up(tid,1)
                else:
                    print('not ready yet')
                    upgrade_ready = False
                if upgrade_ready:
                    bot.answer_callback_query(query.id, f"🌟 Ваши способности улучшены!")  
                    bot.send_message(query.from_user.id, "🌟 Ваши способности улучшены!")
                else:
                    bot.send_message(query.from_user.id, "🌟 Ещё не реализовано, подождите новый патч, или потратьте на другое!")
                bot.delete_message(query.message.chat.id, query.message.id)  
                return
            else:
                bot.answer_callback_query(query.id, f"❌ Нехватает очков талантов!") 
                bot.delete_message(query.message.chat.id, query.message.id)  
                return
                 
    
    else:
        cidx = 0

    next_cid = 0 if cidx == len(available_items) - 1 else cidx + 1
    item = available_items[cidx]
    
    markup = types.InlineKeyboardMarkup(row_width=2,)
    up_lbl_avail =  "" if item[3] else f"\n🟥 требуется {item[1]} уровень"
    lbl = item[2] + up_lbl_avail
    btn_buy = types.InlineKeyboardButton(f"❇️", callback_data='up' + str(cidx) + '_1')
    btn_forward = types.InlineKeyboardButton('▶', callback_data='up' + str(next_cid) + '_0' )
    markup.add(btn_buy,btn_forward)
    if hasattr(query,'data'):
        bot.edit_message_text(
            text=lbl,
            chat_id=query.message.chat.id,
            parse_mode='markdown', # to make some text bold with *this* in messages
            message_id=query.message.id,
            reply_markup=markup
        )
    else:
        bot.send_message(query.from_user.id, lbl,parse_mode='markdown', reply_markup=markup)

def lucky_way(message):
    tid = message.from_user.id
    if slow_down(message.from_user.id):
        return
    #print(message.__dict__)
    # anti_forward(message.from_user.id, message.forward_date)
    if message.forward_date is not None:
        print(f"-- ANTI CHEAT for {str(tid)} - - -- - -- - - - -")
        #print("forward: " + str(message.forward_date))
        penalty = 10
        sql_helper.db_stamina_down(tid,10)
        sql_helper.db_remove_money(tid, penalty)
        bot.send_message(tid, f"⚠ Мошенничество! -{penalty}💰")
        return
    stamina = sql_helper.db_get_player_info(message.from_user.id)[2]
    if stamina == 0:
        bot.send_message(tid,"Недостаточно сил😪")
        return
    print('- - - LUCKY WAY - - -')
    #location =  sql_helper.db_check_location(tid)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🦓Поймать животное",)
    btn2 = types.KeyboardButton("💰Деньги",)
    btn3 = types.KeyboardButton("😈Преступник",)
    btn4 = types.KeyboardButton("⛏️Клад",)
    btn_back = types.KeyboardButton("🔙 Назад")
    markup.add(btn1,btn2,btn3,btn4,btn_back)
    bot.send_message(tid, 'Что вас интересует?:', reply_markup=markup)  
    bot.register_next_step_handler(message, to_lucky_way)

def to_lucky_way(message):
    print('- - to_lucky_way - - ')
    #anti_forward(message.from_user.id, message.forward_date)
    if slow_down(message.from_user.id):
        return
    if message.forward_date is not None:
        print(f"-- ANTI CHEAT for {str(message.from_user.id)} - - -- - -- - - - -")
        #print("forward: " + str(message.forward_date))
        penalty = 10
        sql_helper.db_stamina_down(message.from_user.id,10)
        sql_helper.db_remove_money(message.from_user.id, penalty)
        bot.send_message(message.from_user.id, f"⚠ Мошенничество! -{penalty}💰")
        return
    if re.match('^💰Деньги.*',message.text):   
        print('- - - money selected - - - ')        
        do_work(message)
    elif re.match('^🦓Поймать.*', message.text):
        print('- - - animal lucky selected - - - ')
        pet_shop(message, catch_mode=True)
    elif re.match('^😈Преступник.*', message.text):
        print('- - - animal lucky selected - - - ')
        location =  sql_helper.db_check_location(message.from_user.id)
        if location == 5:
            bot.send_message(message.from_user.id, "❌На этой территории доступ к чужим зоопаркам запрещен")
            echo_all(message)
            return
        stamina = sql_helper.db_get_player_info(message.from_user.id)[2]    
        if stamina < 2:
            bot.send_message(message.from_user.id, "Ты устал 😪")
            echo_all(message)
            return
        search_victims(message)
    elif re.match('^⛏️Клад.*', message.text):
        print('- - - digging treasure lucky selected - - - ')
        bot.send_message(message.from_user.id, "Это поле доступно для всех игроков. Возможно где-то здесь зарыто сокровище. Выбери место где копать, вдруг тебе повезёт! \nГлубина каждой клетки 2. Попытка 💪1. \n⬛️ - Можно копать глубже. \n◾️ - не копали. 🚫 - Копать некуда.")
        lucky_treasure(message)
    else:
        echo_all(message)

@bot.callback_query_handler(lambda query: 'dig' in query.data)
def lucky_treasure(query):
    tid = query.from_user.id
    player = sql_helper.db_get_player_info(tid)
    location = player[5]
    stamina = player[2]

    # TODO add ability to set mine (bomb) in cell 
    # TODO add tool required ⛏️

    msg = '⛏️Раскопки'

    if hasattr(query,'data'):
        print(f"{datetime.now()};{tid};{query.data}")
        
        dig_cell = int(extract_numbers(query.data))
        if dig_cell == 100:
            bot.send_message(query.from_user.id, "выход")
            bot.delete_message(query.message.chat.id, query.message.id)
            return
        stm_left = sql_helper.db_stamina_down(tid,1)
        time.sleep(0.3)
        if stm_left == 0:
            print(f"LOW STAMINA")
            return
        deep = int(extract_numbers(query.data,1))
        dig_result = sql_helper.db_dig_field(location,dig_cell,deep,tid)        
        
        if not dig_result[0]:
            print('it is a botton')
            msg = f"❌ В этом месте уже слишком глубоко, вряд ли стоит копать здесь дальше. 💪{stamina}"
        elif dig_result[0] == dig_result[1] or dig_result[0] == dig_result[2]:            
            money_or_item = random.randrange(1,7)
            #treasure_value = 20 if money_or_item >= 3 else 10
            print(f"DIG_TREASURE_OR_BONES: {money_or_item}")
            if money_or_item >= 3:
                if dig_result[0] == dig_result[1]:
                    bot.send_message(query.from_user.id,'+20💰 Клад!')
                    sql_helper.db_add_money(tid,20)
                else:
                    bot.send_message(query.from_user.id,'+10💰 Клад!')
                    sql_helper.db_add_money(tid,10)          
            else:
                print(f"DIG_BONE;{tid}")
                if sql_helper.tech_done_check(tid,2) > 0:
                    trex = random.randrange(0,2)
                    if trex:
                        sql_helper.db_get_item(tid,41)  
                    else:
                        sql_helper.db_get_item(tid,40)
                else:
                    if random.randrange(0,2):
                        sql_helper.db_get_item(tid,40)
                bot.send_message(query.from_user.id,'🦴Вы нашли кости древнего существа. Без знаний Палеонтологии можно найти меньше костей и некоторые будут непригодны.')  
                bot.delete_message(query.message.chat.id, query.message.id) 
                return           
        elif dig_result[0] == dig_result[3]:
            print('Danger FOUND')
            bot.send_message(query.from_user.id,'🤕 Вы травмировались -4💪')
            sql_helper.db_stamina_down(tid,4)
            sql_helper.db_exp_up(tid,2)
            # bot.send_message(query.from_user.id,'Ты устал, наберись сил')
            # bot.delete_message(query.message.chat.id, query.message.id)
        elif dig_result[0] == dig_result[4]:
            print(f"{tid} Fossil found")
            if sql_helper.tech_done_check(tid,2) > 0:
                mamont_intact = random.randrange(1,11) # whole body. not damaged
                print("MAMONT")
                if mamont_intact > 5:
                    sql_helper.db_buy_pet(tid,31)
                    bot.send_message(query.from_user.id, "🦣 Мамонт! Вы нашли целого мамонта! Он не живой, но выглядит как настоящий!")
                else:
                    bot.send_message(query.from_user.id, "🦴 Вы нашли останки древнего животного. Похоже это мамонт. К сожалению он плохо сохранился.")
            else:
                bot.send_message(query.from_user.id, "🦴 Вы нашли останки древнего животного. Похоже это был 🦣 мамонт. К сожалению вы повредили его при раскопках и не знаете Как выкопать. Возможно изучив Палеонтологию вы смогли бы это сделать правильно.")
                #bot.answer_callback_query(query.id, "", show_alert=True)
                sql_helper.db_exp_up(tid,2)
        else:
            msg = f"⛏️ 💪{stamina - 1}"
            sql_helper.db_exp_up(tid,1)
            bot.answer_callback_query(query.id, "🌟+1", show_alert=False)
            

    cells = sql_helper.db_get_field(location)
    pin_pad_buttons = []
    markup = types.InlineKeyboardMarkup(row_width=4,)
    counter = 1
    for i in cells:
        if i[0] == 0:
            # 
            deep = 2
            cell_emoji = '⬛️' if i[1] != 0 else '🚫'
            btn = types.InlineKeyboardButton(f"{cell_emoji}",callback_data=f"dig_{counter}_{deep}")
        else:
            deep = 1
            cell_emoji = '◾️' if i[1] != 0 else '🚫'
            btn = types.InlineKeyboardButton(f"{cell_emoji}{i}",callback_data=f"dig_{counter}_{deep}")
        counter +=1
        pin_pad_buttons.append(btn)
    btn_exit = types.InlineKeyboardButton(f"🔙",callback_data=f"dig_100")
    pin_pad_buttons.append(btn_exit)
    markup.add(*pin_pad_buttons)

    if stamina < 1:
        bot.send_message(query.from_user.id,'Ты устал, наберись сил')
        bot.delete_message(query.message.chat.id, query.message.id)

    if hasattr(query,'data'):
        bot.edit_message_text(
            text=msg,
            chat_id=query.message.chat.id,
            parse_mode='markdown', # to make some text bold with *this* in messages
            message_id=query.message.id,
            reply_markup=markup
        )
    else:
        bot.send_message(query.from_user.id, msg, reply_markup=markup)
        #bot.send_message(query.from_user.id,'treasure', reply_markup=markup)

@bot.callback_query_handler(lambda query: 'stealing' in query.data)
def stealing(query):
    print('- STEALING (checking input pass):')

    tid = query.from_user.id
    pinfo = sql_helper.db_get_player_info(tid)
    
    victim = extract_numbers(query.data,0)
    input_pass = int(extract_numbers(query.data,1))
    if input_pass == 100:
        bot.send_message(tid, "выход")
        bot.delete_message(query.message.chat.id, query.message.id)
        return
    #print(info)
    secret = sql_helper.db_get_zoo_password(victim)
    

    # decay key
    items = sql_helper.db_get_owned_items(tid)
    tools = 0
    tools_durability = 0
    for i in items:
        if i[5]== 20:
            tools = i[0]
            tools_durability = i[6]

    if tools_durability == 0:
        bot.send_message(query.from_user.id, "⚠Отмычка сломана")
        bot.delete_message(query.message.chat.id, query.message.id)
        sql_helper.db_remove_property(tools)
        #echo_all()
        return

    sql_helper.db_decay_property(tools)

    v_items = sql_helper.db_get_owned_items(victim)
    strong_lock = False
    zoo_alarm = False
    for i in v_items:
        #print('items:')
        #print(i[5])
        if i[5] == 6:
            strong_lock = True
        elif i[5] == 7:
            zoo_alarm = True
            #break
    
    pwr = 8 if strong_lock else 2
    #pwr = 4 if pinfo[9] == 1 else pwr
    pwr = math.ceil(pwr/(pinfo[9]+1))
    lock_info = f"Здесь установлены хорошие🔒\nВаш навык взлома:{pinfo[9]}\n(1 попытка= {pwr} 💪)" if strong_lock else ''
    
    stamina = sql_helper.db_get_player_info(query.from_user.id)[2]    
    if stamina < pwr:
        bot.send_message(tid, lock_info + "Недостаточно сил 😪")
        bot.delete_message(query.message.chat.id, query.message.id)
        #echo_all()
        return
    sql_helper.db_stamina_down(query.from_user.id, pwr)
    sql_helper.db_exp_up(tid,pwr)

    print(f"STEALING; target:{victim} ;input: {input_pass} secret: {secret}; pwr:{pwr}")

    if input_pass == secret:
        print('cage unlocked')
        chapest_pet = sql_helper.db_get_cheapest_pet(victim)
        print(list(chapest_pet))
        #bot.answer_callback_query(query.message.id, f"Успешно! Вероятность 10% что самый дешевый петомец убежит.") 
        bot.delete_message(query.message.chat.id, query.message.id)
        pet_stays = random.randrange(1,100)
        sql_helper.db_stamina_down(tid, 1) # TODO get cheaper or remove whan stealing (lockpicking improved)
        bot.send_message(tid, "🔐")
        escape_percent = 16
        
        if pet_stays < escape_percent:
                print('Successful harm: pet escaped!')
                if chapest_pet[2] == 31: # moomoth
                    sql_helper.db_change_health(chapest_pet[0],val=5)
                    act = 'был повреждён вором!'
                else:
                    sql_helper.db_remove_pet(chapest_pet[0])
                    act = 'убежал!'
                for tidx in [query.from_user.id, victim]:
                    bot.send_message(tidx, f" {pet_emoji(chapest_pet[2])} {act}")
        else:
            bot.send_message(query.from_user.id, f"Успешно! Замок взломан, но {pet_emoji(chapest_pet[2])} не {act} Шанс {escape_percent}%")

            if zoo_alarm:
                print('ZOO_ALARM')
                bot.send_message(victim,"🚨 Тревога! Ваши клетки пытаются открыть!")
    else:
        search_victims(query)
        #bot.send_message(query.from_user.id, "🔒 Неудалось")
        #bot.delete_message(query.message.chat.id, query.message.id)
        # bot.edit_message_text(
        #     text='🔒 Неудалось',
        #     chat_id=query.message.chat.id,
        #     parse_mode='markdown', # to make some text bold with *this* in messages
        #     message_id=query.message.id,
        #     reply_markup=markup
        # )
        #TODO stamina down , degrade skeleton key
    #bot.send_message(query.from_user.id, f"{victim} : {input_pass} ? {secret}", parse_mode='markdown')

    #TO THINK : after stealing prohibit restrict another stealing try for perid of time

@bot.callback_query_handler(lambda query: 'victim' in query.data)
def search_victims(query):

    tid = query.from_user.id
    markup = None
    btn_pack = []
    
    if hasattr(query,'data'):
        print(query.data)

        items = sql_helper.db_get_owned_items(tid)
        tools = 0
        for i in items:
            if i[5]== 20:
                tools = i[0]

        if tools == 0:
            bot.send_message(tid, "Нужна отмычка!")
            bot.delete_message(query.message.chat.id, query.message.id)
            #echo_all()
            return
        
        stamina = sql_helper.db_get_player_info(tid)[2]
        #sql_helper.db_stamina_down(query.from_user.id,1)
        ask = 'Зоопарк жертвы:'
        victim = int(extract_numbers(query.data,0))
        #print('victim: ' + str(victim))
        v_zoo = sql_helper.db_get_owned_pets(victim)
        v_emoji_pack = ''
        #TODO good lock consume more stamina
        for pet in v_zoo:
            v_emoji_pack += pet_emoji(pet[1])
        ask = "Обитатели: " + v_emoji_pack + f"\nВаша 💪{stamina}"
        pin_pad_buttons = []
        markup = types.InlineKeyboardMarkup(row_width=3,)
        for i in range(9,-1,-1):
            btn = types.InlineKeyboardButton(f"{i}",callback_data=f"stealing{victim}_{i}")
            pin_pad_buttons.append(btn)
        btn_exit = types.InlineKeyboardButton(f"✖",callback_data=f"stealing{victim}_100")
        pin_pad_buttons.append(btn_exit)
        markup.add(*pin_pad_buttons)
        #markup = quick_markup({'1': {'callback_data': 'victim'},'2': {'callback_data': 'victim'},'3': {'callback_data': 'victim'}}, row_width=3)

        print(list(v_zoo))
    else:
        print('------ have no data')
        markup = types.InlineKeyboardMarkup(row_width=1,)

        stamina = sql_helper.db_get_player_info(tid)[2]
        sql_helper.db_stamina_down(tid,1)
        sql_helper.db_exp_up(tid,1)

        ask = '-1💪 Ближайшие зоопарки:'
        location =  sql_helper.db_check_location(tid)
        victims = sql_helper.db_get_nearby_players(location)
        i = 1
        #print("total players: " + str(total_players))
        if len(victims) < 2:
            ask = 'Похоже рядом нет других игроков -1💪'
        
        for player in victims:
            if player[0] == tid:
                continue
            pname = player[1] if player[2] =='x' else player[2]
            
            btn_title = f"#{i} {pname}\n"
            btn = types.InlineKeyboardButton(btn_title,callback_data='victim' + str(player[0]))
            i += 1
            btn_pack.append(btn)
        markup.add(*btn_pack)
    if hasattr(query,'data'):
        #print('HAS query data:')
        #print(query.data)
        if re.match('steal.*',query.data ):
            ask = '🔒 Неудалось' + f"\nВаша 💪{stamina}"
            bot.answer_callback_query(query.id, f"🔒 неудачно")
        #     bot.send_message(query.from_user.id, ask, reply_markup=markup)
        # else:
        bot.edit_message_text(
            text=ask,
            chat_id=query.message.chat.id,
            parse_mode='markdown', # to make some text bold with *this* in messages
            message_id=query.message.id,
            reply_markup=markup
        )
    else:
        bot.send_message(query.from_user.id, ask, reply_markup=markup)


def to_shop(message):
    print('- - to shop - - ')
    if re.match('.*Зоо.*',message.text):           
        pet_shop(message, catch_mode=False)
    elif re.match('.*Рынок.*', message.text):
        print('- - - bazar selected - - - ')
        bazar_shop_new(message)
    else:
        echo_all(message)

def bazar_shop(message):
    tid = message.from_user.id  
    # TODO check owned items
    location =  sql_helper.db_check_location(tid)
    available_items = sql_helper.db_get_bazar_shop_items(location)
    btn_pack = []

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)                   
    print(list(available_items))
    for a in available_items:
        btn = types.KeyboardButton(f"#{a[0]}" + " 📦 "  + a[1] + " 💰 " + str(a[2]))
        btn_pack.append(btn)
    #btn_sell = types.KeyboardButton("Продать ") # NOTICE maby later
    btn_back = types.KeyboardButton("🔙 Назад")
    markup.add(*btn_pack,btn_back)
    bot.send_message(tid, 'Выберите покупку:', reply_markup=markup)
    bot.register_next_step_handler(message, buy_item)

@bot.callback_query_handler(lambda message: 'bazar' in message.data )
def bazar_shop_new(message):
    tid = message.from_user.id  
    # TODO check owned items
    location =  sql_helper.db_check_location(tid)
    available_items = sql_helper.db_get_bazar_shop_items(location)
    btn_pack = []

    # for i in available_items:
    #     btn = types.KeyboardButton(f"#{i[0]}" + " 📦 "  + i[1] + " 💰 " + str(i[2]))
    #     btn_pack.append(btn)
    # markup = types.InlineKeyboardMarkup()
    # markup.add(btn_pack)

    #check owned


    if hasattr(message,'data'):
        cidx = int(extract_numbers(message.data))
        # -------------------------------------------buy item option -------------------------------------------------------
        if int(extract_numbers(message.data,1)):
            
            item = available_items[cidx]
            print(f"{datetime.now()}, {tid} buying item {item[0]} in loc: {location}")          
            if item[0] == 10:
                total_pasports = sql_helper.db_count_item_type(tid,10)
                total_pasports = 0 if total_pasports is None else total_pasports
                extra_price = round(1.0 + (0.6 * total_pasports),2) # ATTENTION THIS FORMULA USED IN TWO PLACES 
            else:
                extra_price = 1
            buying_ok = sql_helper.db_buy_item(tid,item[0], extra_price)
            if buying_ok:
                bot.answer_callback_query(message.id, f"📦 Вы купили {item[1]}!")            
                if item[0] == 10:
                    bot.send_message(message.from_user.id, "📔 Введите новое имя для себя в игре! (20 символов)")
                    bot.register_next_step_handler(message.message, set_nickname)
                    # TODO get peni for more than one passport
            else:
                bot.answer_callback_query(message.id, f"❌ Нехватает денег!") 
                return   
    else:
        cidx = 0

    next_cid = 0 if cidx == len(available_items) - 1 else cidx + 1
    item = available_items[cidx]
    price = item[2]

        #check owned
    owned_items = sql_helper.db_get_owned_items_group(message.from_user.id)
    owned_items_id = []
    is_owned = False
    is_owned_info = ''
    for i in owned_items:
        if i[0] == item[0]:
            is_owned = True
            is_owned_info = f"\n✅ У вас уже имеется ({i[2]})"
            if i[0] == 10: # every next pasport is more expensive
                price = int(price * (1.0 + (0.6 * i[2]))) # ATTENTION THIS FORMULA USED IN TWO PLACES 
            break
    print(list(owned_items_id))        

    lbl = f"{item_emoji(item[0])} *{item[1]}* : {item[3]} {is_owned_info}"
    action = '_0'

    markup = types.InlineKeyboardMarkup()
    if item[0] in [1,2,3] and is_owned:
        btn_buy = types.InlineKeyboardButton('✖', callback_data='bazar' + str(next_cid) + action)
    else:
        btn_buy = types.InlineKeyboardButton(f"💰 {price} ", callback_data='bazar' + str(cidx) + '_1')
    btn_forward = types.InlineKeyboardButton('▶', callback_data='bazar' + str(next_cid) + action)
    #btn_sell = types.KeyboardButton("Продать ") # NOTICE maby later
    #btn_back = types.KeyboardButton("🔙 Назад")
    markup.add(btn_buy,btn_forward)
    # bot.send_message(tid, 'Выберите покупку:', reply_markup=markup)
    # bot.register_next_step_handler(message, buy_item)
    if hasattr(message,'data'):
        bot.edit_message_text(
            text=lbl,
            chat_id=message.message.chat.id,
            parse_mode='markdown', # to make some text bold with *this* in messages
            message_id=message.message.id,
            reply_markup=markup
        )
    else:
        bot.send_message(message.from_user.id, lbl,parse_mode='markdown', reply_markup=markup)

def pet_shop(message, catch_mode=False):
    print('---------- PET SHOP -----------')    
    tid = message.from_user.id    
    owned = sql_helper.db_check_owned_pets(message.from_user.id)
    pet_space = sql_helper.db_get_player_info(message.from_user.id)[4]
    # TODO add pet space addition by buying some item (maby just a box) and return to home

    if owned == pet_space: 
            # markup = types.ReplyKeyboardMarkup(resize_keyboard=True) 
            # bot.send_message(message.from_user.id,"Нет места для новых питомцев ☹")
            # btn_sell = types.KeyboardButton("Продать ")
            # btn_back = types.KeyboardButton("🔙 Назад")            
            # markup.add(btn_sell,btn_back)
            # bot.register_next_step_handler(message,sell_pets(message) )
            bot.send_message(message.from_user.id, 'В вашем зоопарке нет свободного места!')
    
        # define location to show animals specific for this location
    location =  sql_helper.db_check_location(tid)
    if catch_mode:
        animals = sql_helper.db_get_animal_for_catch(location)
    else:
        animals = sql_helper.db_get_animal_shop(location, catch_mode)
    btn_pack = []

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)                   
    print(list(animals))
    for a in animals:
        if catch_mode:
            btn = types.KeyboardButton(f"#{a[0]} " + pet_emoji(a[0]) + " 💰" + str(a[3]) + f" 💪{a[4]} 🎲{a[5]}%")
            msg = 'Здесь есть шанс поймать:'
        else:
            btn = types.KeyboardButton(f"#{a[0]} " + pet_emoji(a[0]) + " 💰 " + str(a[2]) + f" ⭐{a[3]}")
            msg = 'Здесь можно купить:'
        btn_pack.append(btn)
    btn_sell = types.KeyboardButton("Продать ")
    btn_back = types.KeyboardButton("🔙 Назад")
    markup.add(*btn_pack,btn_sell,btn_back)
    bot.send_message(tid, msg, reply_markup=markup)
    if catch_mode:
        bot.register_next_step_handler(message,catch_pet)
    else:
        bot.register_next_step_handler(message, buy_pet)
      

def catch_pet(message):
    print('- - - trying catch pet - - -')
    if re.match('.*Назад.*',message.text):
        echo_all(message)
        return
    tid = message.from_user.id

    #anti_forward(tid, message.forward_date)
    if message.forward_date is not None:
        print(f"-- ANTI CHEAT for {str(message.from_user.id)} - - -- - -- - - - -")
        #print("forward: " + str(message.forward_date))
        penalty = 10
        sql_helper.db_stamina_down(message.from_user.id,10)
        sql_helper.db_remove_money(message.from_user.id, penalty)
        bot.send_message(message.from_user.id, f"⚠ Мошенничество! -{penalty}💰")
        return
    
    owned = sql_helper.db_check_owned_pets(message.from_user.id)
    pet_space = sql_helper.db_get_player_info(message.from_user.id)[4]
    # TODO add pet space addition by buying some item (maby just a box) and return to home

    if owned == pet_space: 
            # markup = types.ReplyKeyboardMarkup(resize_keyboard=True) 
            # bot.send_message(message.from_user.id,"Нет места для новых питомцев ☹")
            # btn_sell = types.KeyboardButton("Продать ")
            # btn_back = types.KeyboardButton("🔙 Назад")            
            # markup.add(btn_sell,btn_back)
            # bot.register_next_step_handler(message,sell_pets(message) )
            bot.send_message(message.from_user.id, 'В зоопарке кончилось место!')
            return
    #elif owned < pet_space:
    
    info = sql_helper.db_get_player_info(message.from_user.id)
    coins = info[0]
    stamina = info[2]
    print(stamina)
    last_work = info[3]
    hour_ago = datetime.now() - timedelta(hours=1)
    #d = datetime.now() - delta
    if last_work < hour_ago:
    #if stamina == 0:
        print(f"lastwork {last_work} more than {hour_ago} checking relax...")
        stamina = stamina + check_relax(tid)
    else:
        print(f"lastwork {last_work} less than {hour_ago} - NO checking relax")

    animal_id = int(extract_numbers(message.text))
    catch_price = int(extract_numbers(message.text,1))
    chance = int(extract_numbers(message.text,3))
    pwr = int(extract_numbers(message.text,2)) 
    
    print("-- CATCHING: " + str(tid) + " type: " + message.text + f" animal:{animal_id} chance:{chance} at " + str(datetime.now()))
    #print(message.__dict__)
    
    if stamina < pwr or coins < catch_price:
        bot.send_message(message.from_user.id, f"😪 Нужны деньги и силы, чтобы ловить редких животных!\n Ваши 💪={stamina} 💰={coins}")  
        echo_all
        return    

    if chance == 17:
        print('chance 17%')
        m = bot.send_dice(tid,'🎲')
        sql_helper.db_stamina_down(tid, pwr)
        sql_helper.db_remove_money(tid,catch_price)
    elif chance == 11:
        print('chance 11')
        m = bot.send_dice(tid,'🎰')
        sql_helper.db_stamina_down(tid, pwr)
        sql_helper.db_remove_money(tid,catch_price)
    else:
        print('ERROR CHANCE PERCENT PROBLEM - - - - - - - - - - ')
        
    bot.register_next_step_handler(message, lucky_way)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # m = bot.send_dice(tid,'🎲')
    dig_result = m.dice.value
    if chance == 11:
        print(f"Rare catching {tid}")
        if dig_result in [1,16,22,32,43,48,64] or (dig_result in [1,2,3,4,16,22,32,43,48,64] and info[10] > 0): # 2nd option for upgraded taming ability  TODO check or rewrite 
            # TODO add catching bonus
            time.sleep(2)
            print(f"catching {tid}; upgrade worked; slot {dig_result}")
            sql_helper.db_get_pet(tid, animal_id)
            bot.send_message(tid,f"Ура! Вы поймали {pet_emoji(animal_id)}",  reply_markup=markup)    
            return
        else:
            print(f"failed with slot: {dig_result}")
            time.sleep(2)
            bot.send_message(tid, f"Неповезло, животное убежало! Потрачено {pwr}💪 {catch_price}💰",  reply_markup=markup)
            sql_helper.db_exp_up(tid,pwr)  
    elif chance == 17:
        if dig_result < 6:
            # TODO this and other sleep() stops all other players!
            if dig_result ==5  and info[10] > 0 and random.randrange(0,2):
                time.sleep(3)
                print(f"catching {tid}; upgrade worked")
                sql_helper.db_get_pet(tid, animal_id)
                bot.send_message(tid,f"Ура! Вы поймали {pet_emoji(animal_id)}",  reply_markup=markup)    
                return
            time.sleep(3)
            bot.send_message(tid, f"Неповезло, животное убежало! Потрачено {pwr}💪 {catch_price}💰",  reply_markup=markup)
            sql_helper.db_exp_up(tid,pwr)         
        elif dig_result == 6:
            time.sleep(3)
            sql_helper.db_get_pet(tid, animal_id)
            bot.send_message(tid,f"Ура! Вы поймали {pet_emoji(animal_id)}",  reply_markup=markup)            
        else:
            print('-- unknown catching animal none --')
            echo_all(message) 

def buy_pet(message):

    owned = sql_helper.db_check_owned_pets(message.from_user.id)
    pet_space = sql_helper.db_get_player_info(message.from_user.id)[4]
    # TODO add pet space addition by buying some item (maby just a box) and return to home

    if owned == pet_space: 
            # markup = types.ReplyKeyboardMarkup(resize_keyboard=True) 
            # bot.send_message(message.from_user.id,"Нет места для новых питомцев ☹")
            # btn_sell = types.KeyboardButton("Продать ")
            # btn_back = types.KeyboardButton("🔙 Назад")            
            # markup.add(btn_sell,btn_back)
            # bot.register_next_step_handler(message,sell_pets(message) )
            bot.send_message(message.from_user.id, 'В зоопарке кончилось место!')
    elif owned < pet_space:
        print(' - - - buy pet - - - ')
        if re.match('.*#.*',message.text):
            animal_id = int(extract_numbers(message.text))
            ok = sql_helper.db_buy_pet(message.from_user.id, animal_id)
            if ok:
                bot.send_message(message.from_user.id, "🎉 Петомец куплен!")
                bot.send_message(message.from_user.id, pet_emoji(animal_id))
                #echo_all(message)
            else:
                bot.send_message(message.from_user.id, "❌ Не хватает денег!")
    # selling pet
    if re.match('.*Продать.*',message.text):
        pet_list = sql_helper.db_get_owned_pets(message.from_user.id)
        if len(pet_list) == 0:
            bot.send_message(message.from_user.id, "🚫 У вас нет питомцев!")
            #time.sleep(1)
            echo_all(message)
        else:
            sell_pets(message)  
    else:
        echo_all(message)

def buy_item(message):
    print(' - - - buy item - - - ')
    if re.match('.*#.*',message.text):
        item_id = int(extract_numbers(message.text))
        owned_items = sql_helper.db_get_owned_items(message.from_user.id)
        owned_items_id = []
        for i in owned_items:
            owned_items_id.append(i[5])
        print(list(owned_items_id))
        if item_id in owned_items_id:
            bot.send_message(message.from_user.id, "❌ У вас уже есть такой предмет!")
            return
        ok = sql_helper.db_buy_item(message.from_user.id, item_id)
        # item id 1 and 2 its different types of boxes
        if ok and item_id in [1,2]:
            bot.send_message(message.from_user.id, "🎉 Поздравляем с покупкой! Вернитесь домой, чтобы использовать клетку.\n Эту клетку можно использовать только один раз!")
            bot.send_photo(message.from_user.id,'AgACAgIAAxkBAAIkIWdC48JXnJZFGVULAAFBQefELqAT0AAC8eUxG72lGUq9LWS8E531jQEAAwIAA3MAAzYE')
            echo_all(message)
        elif ok and item_id == 10:
            # passport 
            bot.send_message(message.from_user.id, "📔 Введите новое имя для себя в игре!")
            bot.register_next_step_handler(message, set_nickname)
        else:
            bot.send_message(message.from_user.id, "❌ Не хватает денег!")
    # selling pet
    # elif re.match('.*Продать.*',message.text):
    #     pet_list = sql_helper.db_get_owned_pets(message.from_user.id)
    #     if len(pet_list) == 0:
    #         bot.send_message(message.from_user.id, "🚫 У вас нет вещей!")
    #         #time.sleep(1)
    #         echo_all(message)
    #     else:
    #         sell_pets(message)  
    else:
        echo_all(message)

@bot.callback_query_handler(lambda query: 'sel' in query.data )
def sell_pets(query):
    print('- - - - sell pets function - - - - ')
    owned_pets = sql_helper.db_get_owned_pets(query.from_user.id)
    #print(list(owned_pets))
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(*gen_inline_sell_buttons(owned_pets)) 
    if hasattr(query,'data'):
        
        pet_it = extract_numbers(query.data)
        sold_animal = int(extract_numbers(query.data,1))
        sql_helper.db_sell_pet(pet_it) 
        owned_pets = sql_helper.db_get_owned_pets(query.from_user.id)
        text = "Кого продать?" if len(owned_pets) > 0 else "У вас нет питомцев!" 
        markup = quick_markup({}) # clear buttons from previous query
        markup.add(*gen_inline_sell_buttons(owned_pets)) 
        bot.edit_message_text(
            #text='Продан ' + pet_emoji(sold_animal),
            text,#= 'Кого хотите продать?',
            chat_id=query.message.chat.id,
            message_id=query.message.id,
            reply_markup=markup
        )
        bot.answer_callback_query(query.id, pet_emoji(sold_animal) + " продан!", show_alert=True)
    else:
        bot.send_message(query.from_user.id, "Кого продать?", reply_markup=markup)  
    #bot.register_next_step_handler(message, echo_all)

def gen_inline_sell_buttons(data_list):
    btn_pack = []
    for p in data_list:
        animal_id = str(p[1])
        pet_price = str(int(p[2] / 2)) # sell price its original price / 2
        emj = str(pet_emoji(p[1]) + " 💰+" + pet_price)
        cb_prefix = 'sel'
        btn = types.InlineKeyboardButton(emj,callback_data=cb_prefix + str(p[0]) + '_' + animal_id)
        btn_pack.append(btn)

    return btn_pack

def set_nickname(message):
    print(f"{message.from_user.id} rename")
    raw_nickname = message.text[:20]
    regex_filter = re.compile(r'\w{3,20}',re.I)
    filter_result = regex_filter.search(raw_nickname)
    new_nickname = 'Сонный Пцыц' if not hasattr(filter_result,'group') else filter_result.group()
    sql_helper.db_rename_player(message.from_user.id, new_nickname)
    if new_nickname == 'Сонный Пцыц':
        bot.send_message(message.from_user.id, "Вы использовали некорректное имя. Ваше новое имя: " + new_nickname)
    else:
        bot.send_message(message.from_user.id, "Теперь в топе вы будете отображаться с этим именем")
    print(new_nickname)

#  - - - - - - - - - - - - E A R N I N G  M O N E Y  - - - - - - - - - - - - - - - - - -

# TODO rename all work mentions to getmoney
@bot.message_handler(regexp=".*Работа.*")
def do_work(message):
    print(' - - - play minigames - - -')
    tid = message.from_user.id

    #anti_forward(tid, message.forward_date)
    if message.forward_date is not None:
        print(f"-- ANTI CHEAT for {str(message.from_user.id)} - - -- - -- - - - -")
        #print("forward: " + str(message.forward_date))
        penalty = 10
        sql_helper.db_stamina_down(message.from_user.id,10)
        sql_helper.db_remove_money(message.from_user.id, penalty)
        bot.send_message(message.from_user.id, f"⚠ Мошенничество! -{penalty}💰")
        return

    info = sql_helper.db_get_player_info(message.from_user.id)
    stamina = info[2]
    print(stamina)
    last_work = info[3]
    hour_ago = datetime.now() - timedelta(hours=1)
    #d = datetime.now() - delta
    if last_work < hour_ago:
    #if stamina == 0:
        print(f"lastwork {last_work} more than {hour_ago} checking relax...")
        stamina = stamina + check_relax(tid)
    else:
        print(f"lastwork {last_work} less than {hour_ago} - NO checking relax")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if stamina == 1:
        btn1 = types.KeyboardButton("🎲 удачный кубик 💪x1")
        btn3 = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn3)
        bot.send_message(message.from_user.id, "Твои силы : " + str(stamina), reply_markup=markup) 
        bot.register_next_step_handler(message, search_money, stamina)
    elif stamina == 2:
        btn1 = types.KeyboardButton("🎲 удачный кубик 💪x1")
        btn2 = types.KeyboardButton("🎯 удачный дартс 💪x2")
        btn3 = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn2,btn3)
        bot.send_message(message.from_user.id, "Твои силы : " + str(stamina), reply_markup=markup) 
        bot.register_next_step_handler(message, search_money, stamina)
    elif stamina > 2:
        btn1 = types.KeyboardButton("🎲 удачный кубик 💪x1")
        btn2 = types.KeyboardButton("🎯 удачный дартс 💪x2")
        btn3 = types.KeyboardButton("🎳 удачный боулинг 💪x3")
        btn_back = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn2, btn3, btn_back)
        bot.send_message(message.from_user.id, "Твои силы : " + str(stamina), reply_markup=markup)
        bot.register_next_step_handler(message, search_money, stamina) 
    else:
        # check energy reserve
        
        bot.send_message(message.from_user.id, "😪 Ты устал, наберись сил :", reply_markup=markup)  
        bot.register_next_step_handler(message, echo_all)

def search_money(message, stamina):
    tid = message.from_user.id
    print("-- PLAY: " + str(tid) + " type: " + message.text + " at " + str(datetime.now()) + " stamina: " + str(stamina))
    
    #print(message.__dict__)
    #anti_forward(tid, message.forward_date)
    if message.forward_date is not None:
        print(f"-- ANTI CHEAT for {str(message.from_user.id)} - - -- - -- - - - -")
        #print("forward: " + str(message.forward_date))
        penalty = 10
        sql_helper.db_stamina_down(message.from_user.id,10)
        sql_helper.db_remove_money(message.from_user.id, penalty)
        bot.send_message(message.from_user.id, f"⚠ Мошенничество! -{penalty}💰")
        return

    if re.match('.*удачн.*',message.text):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("Ещё")
        markup.add(btn)        
        if re.match('.*🎲.*',message.text):
            m = bot.send_dice(tid,'🎲')
            pwr = 1
        elif re.match('.*🎯.*',message.text):
            if stamina < 2:
                bot.send_message(tid,"Недостаточно сил")
                return
            m = bot.send_dice(tid,'🎯')
            pwr = 2
        elif re.match('.*🎳.*',message.text):
            if stamina < 3:
                bot.send_message(tid,"Недостаточно сил")
                return
            m = bot.send_dice(tid,'🎳')
            pwr = 3
        else:
            return
        sql_helper.db_stamina_down(tid, pwr)
        bot.register_next_step_handler(message, do_work)
        # m = bot.send_dice(tid,'🎲')
        dig_result = m.dice.value
        coins = pwr
        if dig_result < 5:
            # TODO this and other sleep() stops all other players!
            time.sleep(3)
            bot.send_message(tid,'💩 Неповезло, бывает!',  reply_markup=markup)
        elif dig_result == 5:
            time.sleep(3)
            sql_helper.db_add_money(tid,coins)
            bot.send_message(tid,f"Ура! Приз! 💰 x {coins}",  reply_markup=markup)            
        elif dig_result == 6:
            time.sleep(3)
            coins = coins + 1 if coins < 3 else 5
            sql_helper.db_add_money(tid,coins)
            bot.send_message(tid,f"Ура! Приз! 💰 x {coins}",  reply_markup=markup)            

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
    '''
    returns: stamina point if player rest enough hours
    '''
    info = sql_helper.db_get_player_info(tid)
    last_work = info[3]
    stamina_before = info[2]
    stamina_limit = info[8]
    
    
    #print(f"check+relax func: {str(tid)} last work: " + str(last_work))
    #ts = datetime.fromisoformat(last_work)
    #print(ts)
    this_moment = datetime.now()
    time_diff = this_moment - last_work
    day_left =  this_moment.date().day - last_work.date().day
    #print('time dif:' + str(time_diff))
    single_stamina_priod = 1
    hours_rest = time_diff.days * 24 + time_diff.seconds // 3600 // single_stamina_priod
    #print('hours: ' + str(hours_rest))
    if day_left != 0:
        print('relax day or more')
        profit = sql_helper.db_get_profit_pg(tid, 18) #sql_helper.db_get_profit(tid)  
        if profit == -1:
            bot.send_message(tid,"⚠️ Мошенничество -10💰 " )
            sql_helper.db_remove_money(tid,10)
            return
        bot.send_message(tid,"Доход зоопарка 💰 " + str(profit))
        if stamina_before == stamina_limit:
            sql_helper.db_stamina_up(tid,0,stamina_limit) # set new last_work time to prevent profit loop
            return stamina_before
        relax = hours_rest if (hours_rest + stamina_before) < stamina_limit else stamina_limit - stamina_before
        sql_helper.db_stamina_up(tid,relax,stamina_limit)
    else:
        if hours_rest > 0:
            relax = hours_rest if (hours_rest + stamina_before) < stamina_limit else stamina_limit - stamina_before
            #print('stamina added: ' + str(hours_rest))
            sql_helper.db_stamina_up(tid,relax,stamina_limit)
        else:
            relax = 0
            #print('hours rest ' + str(hours_rest) + 'not enough')
    print(str(datetime.now()) + f" check_relax;tid {str(tid)} last work: {str(last_work)} t_dif: {time_diff}; hours_rest: {hours_rest}; stm_up: {relax}; day_left: {day_left} ")
    return relax

# TODO protect from travel enywhere by text message

@bot.message_handler(regexp=".*Путешествие.*")
def shop_select(message):
    print('---------- SELECT TRAVEL -----------')
    tid = message.from_user.id
    have_passport = sql_helper.db_check_owned_item(tid,10)
    if have_passport == 0:
        bot.send_message(tid, "У вас нет паспорта! 📔")
        return
    # define location to show specific shop
    location =  sql_helper.db_check_location(tid)
    if location == 5:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🌲 Лес 💰 12",)
        btn2 = types.KeyboardButton("🏜 Африка 💰 25",)
        btn_home = types.KeyboardButton("🏠 Домой 💰 5",)
        btn_back = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn2,btn_back)
    elif location == 3: # forest
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🌊 Море 💰 35",)
        btn_home = types.KeyboardButton("🏠 Домой 💰 5",)
        btn_back = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn_home,btn_back)
    elif location == 1: # desert africa
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #btn1 = types.KeyboardButton("🌲 Лес 💰 12",)
        btn1 = types.KeyboardButton("🌊 Море 💰 35",)
        btn2 = types.KeyboardButton("🌎 Америка 💰 20",)
        btn_home = types.KeyboardButton("🏠 Домой 💰 5",)
        btn_back = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn2,btn_home,btn_back)
    elif location == 4: # sea 
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🌲 Лес 💰 12",)
        btn2 = types.KeyboardButton("🏜 Африка 💰 25",)
        btn3 = types.KeyboardButton("🇦🇺 Авст.💰 50",)
        #btn_home = types.KeyboardButton("🏠 Домой 💰 5",)
        btn_back = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn2,btn3,btn_back)
    elif location == 6: # America 
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🏜 Африка 💰 25",)
        btn2 = types.KeyboardButton("🇦🇺 Авст.💰 50",)
        btn_back = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn2,btn_back)
    elif location == 7: # Australia 
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)   
        btn1 = types.KeyboardButton("🌎 Америка 💰 20",)     
        btn_back = types.KeyboardButton("🔙 Назад")
        markup.add(btn1,btn_back)
    else:
        # TODO make home available
        print('- - - - UNKNOWN LOCATION  - - - - -')
    bot.send_message(tid, 'Куда отправимся? 💪-1:', reply_markup=markup)  
    bot.register_next_step_handler(message, travel)



def travel(message):
    print(' - - - TRY TRAVEL - - - ')
    tid = message.from_user.id
    coins = sql_helper.db_get_player_info(message.from_user.id)[0]
    if re.match('.*Лес.*',message.text):
        #ok = sql_helper.db_buy_pet(message.from_user.id, 1)
        if coins >= 12 and sql_helper.db_stamina_drain(tid,1) > -1:
            sql_helper.db_change_location(tid,3,12)
            bot.send_message(message.from_user.id, "✈ Вы отправились в лес 🌲!")
            # new location image
            # any picture have unique id, that we receive when send this pic for the first time to telegram. See picture grabber code block in the end.
            bot.send_photo(tid,'AgACAgIAAxkBAAIOEWcuAuVbHngSU2Woim8h7RyV_RHYAAIt6DEbItVxSW-G6fuv_7JNAQADAgADcwADNgQ')
            sql_helper.db_exp_up(tid,1)
        else:
            bot.send_message(message.from_user.id, "❌ Нужны деньги и сила!")
    if re.match('.*Африка.*',message.text):
        #ok = sql_helper.db_buy_pet(message.from_user.id, 1)
        if coins >= 25 and sql_helper.db_stamina_drain(tid,1) > -1:
            # TODO variable for ticket price
            sql_helper.db_change_location(tid,1,25)
            bot.send_message(message.from_user.id, "✈ Вы улетели в Африку 🏜!")
            # new location image
            bot.send_photo(tid,'AgACAgIAAxkBAAIOEmcuA05mlhg-HQfSqDbYL8ixtHZTAAIv6DEbItVxSfetuCF-nurtAQADAgADcwADNgQ')
            sql_helper.db_exp_up(tid,1)
        else:
            bot.send_message(message.from_user.id, "❌ Нужны деньги и сила!")
    if re.match('.*Море.*',message.text):
        #ok = sql_helper.db_buy_pet(message.from_user.id, 1)
        if coins >= 35 and sql_helper.db_stamina_drain(tid,1) > -1:
            # TODO variable for ticket price
            sql_helper.db_change_location(tid,4,35)
            bot.send_message(message.from_user.id, "✈ Вы улетели на море 🌊!")
            # new location image
            bot.send_photo(tid,'AgACAgIAAxkBAAIOM2cvAAH26uIyVk5WcDod9iBPf-5EkgACweoxGyLVeUmoB8aK8XWdvQEAAwIAA3MAAzYE')
            sql_helper.db_exp_up(tid,1)
        else:
            bot.send_message(message.from_user.id, "❌ Нужны деньги и сила!")
    if re.match('.*Америка.*',message.text):
        #ok = sql_helper.db_buy_pet(message.from_user.id, 1)
        if coins >= 20 and sql_helper.db_stamina_drain(tid,1) > -1:
            # TODO variable for ticket price
            sql_helper.db_change_location(tid,6,20)
            bot.send_message(message.from_user.id, "✈ Вы улетели в Америку 🌎!")
            sql_helper.db_exp_up(tid,1)
            # new location image
            #bot.send_photo(tid,'AgACAgIAAxkBAAIOM2cvAAH26uIyVk5WcDod9iBPf-5EkgACweoxGyLVeUmoB8aK8XWdvQEAAwIAA3MAAzYE')
        else:
            bot.send_message(message.from_user.id, "❌ Нужны деньги и сила!")
    if re.match('.*Авст.*',message.text):
        #ok = sql_helper.db_buy_pet(message.from_user.id, 1)
        if coins >= 50 and sql_helper.db_stamina_drain(tid,1) > -1:
            # TODO variable for ticket price
            sql_helper.db_change_location(tid,7,50)
            bot.send_message(message.from_user.id, "✈ Вы улетели в Австралию 🇦🇺!")
            sql_helper.db_exp_up(tid,1)
            # new location image
            #bot.send_photo(tid,'AgACAgIAAxkBAAIOM2cvAAH26uIyVk5WcDod9iBPf-5EkgACweoxGyLVeUmoB8aK8XWdvQEAAwIAA3MAAzYE')
        else:
            bot.send_message(message.from_user.id, "❌ Нужны деньги и сила!")
    if re.match('.*Дом.*',message.text):
        #ok = sql_helper.db_buy_pet(message.from_user.id, 1)
        if coins >= 5 and sql_helper.db_stamina_drain(tid,1) > -1:
            # TODO variable for ticket price
            sql_helper.db_change_location(tid,5,5)
            bot.send_message(message.from_user.id, "✈ Вы улетели домой 🏠!")
            # new location image
            bot.send_photo(tid,'AgACAgIAAxkBAAIODGcuAhzmF5UMoXJRY21Muwi2veWRAAIq6DEbItVxSb9bfLiZxO8FAQADAgADcwADNgQ')
            # check for delivering new items (cage - for increase owned pets limit)
            owned_items = sql_helper.db_get_owned_items(tid)
            print(f"- List of owned items for {tid}")
            print(list(owned_items))
            #cage_counter = 0
            for i in owned_items:
                if i[5] in [1,2,3] and i[3] == False:
                    sql_helper.db_change_pet_space(tid,1)
                    sql_helper.db_update_property(i[0],switch=True)
                    bot.send_message(tid, "Место для питомцев увеличено!")
                # if i[1] == 'Клетка' and i[3] == False:
                #     sql_helper.db_change_pet_space(tid,1)
                #     sql_helper.db_update_property(i[0],switch=True)    
                #     bot.send_message(tid, "Место для питомцев увеличено!")
                # elif i[1] == 'Железная Клетка' and i[3] == False:
                #     sql_helper.db_change_pet_space(tid,1)
                #     bot.send_message(tid, "Место для питомцев увеличено!")
                #             #cage_counter += 1
                #             #sql_helper.db_remove_property(i[0])                    
                #     sql_helper.db_update_property(i[0],switch=True)            
            # if cage_counter == 1:
            #     sql_helper.db_change_pet_space(tid,1)
            #     bot.send_message(tid, "Место для питомцев увеличено!")
            # elif cage_counter > 1:
            #     bot.send_message(tid, "У вас уже есть такая клетка для животных!")    
            # 
            print('home return done')        
        else:
            bot.send_message(message.from_user.id, "❌ Нужны деньги и сила!")
    echo_all(message)

@bot.callback_query_handler(lambda query: 'cure' in query.data )
def vet(query):
    print('- - - - cure pets function - - - - ')    
    tid = query.from_user.id
    if hasattr(query,'data'):
        print(query.data)
        coins = sql_helper.db_get_player_info(tid)[0]
        cure_price = int(extract_numbers(query.data, 1))   
        print('cure_price from data:' + str(cure_price))     
        if coins < cure_price:
            lbl = '❌ не хватает денег 💰'
            bot.send_message(query.from_user.id, lbl, reply_markup=None)
            
        else:
            healing_pet_id = extract_numbers(query.data)
            print('Healing pet_id: ' + healing_pet_id)     
            animal_id = sql_helper.db_buy_healing(healing_pet_id, cure_price, tid)#sql_helper.db_cure_pet(healing_pet_id)  
            lbl = str(pet_emoji(animal_id)) + 'вылечен 🤗  💰-' + str(cure_price) 
            bot.send_message(tid, '💊')
            # TODO learn how to show notification and show it  
    else:
        print('no pet_id for now')
        lbl = '🏥 кого будем лечить?'
        healing_pet_id = ''
    owned_pets = sql_helper.db_get_owned_pets(tid)
    if len(owned_pets) == 0: 
        bot.send_message(tid, "Все питомцы здоровы 😺 Лечение не требуется!")
        return
    coins = sql_helper.db_get_player_info(tid)[0]
    #print(list(owned_pets))
    #markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_pack = []
    for p in owned_pets:
        print(p)
        health = p[3]
        max_health = p[5]
        if p[1] == 0 or health == max_health: continue # escape corpses
        cure_price = int((p[2] * 0.7) * ((max_health-health) / max_health))  #str(int(p[2] / 2)) # sell price its original price / 2
        if cure_price == 0: cure_price = 1
        emj = str(pet_emoji(p[1]) + f" ♥ {str(health)}/{max_health} 💰x" + str(cure_price))
        cb_prefix = 'cure'
        cb_price_sfx = '_' + str(cure_price)
        btn = types.InlineKeyboardButton(emj,callback_data=cb_prefix + str(p[0]) + cb_price_sfx)
        # TODO fix emoji
        
        btn_pack.append(btn)
        print(type(btn_pack))
    markup.add(*btn_pack)
    #bot.send_message(message.from_user.id, "Кого лечим?", reply_markup=markup)  

    if hasattr(query,'data'):
        bot.edit_message_text(
            text=lbl,
            chat_id=query.message.chat.id,
            message_id=query.message.id,
            reply_markup=markup
        )
    else:
        bot.send_message(query.from_user.id, lbl, reply_markup=markup)

    #bot.register_next_step_handler(message, echo_all)

# @bot.callback_query_handler(lambda query: 'cure' in query.data )
# def pet_cure(query):
#     print(' - - pet cure func -- : ')
#     #pet_it = query.data[-1:]
#     pet_it = extract_numbers(query.data)
#     sql_helper.db_sell_pet(pet_it)    
#     bot.answer_callback_query(query.id,text='You sold pet')
#     bot.send_message(query.from_user.id, "Петомец продан")

#def show_top(message):
 #   print('- - - SHOW TOP - - -')

@bot.callback_query_handler(lambda query: 'tops' in query.data)
def show_top(query):
    print('- -- SHOW TOPS -- -')
    tid = query.from_user.id 
    
    if hasattr(query,'data'):
        cidx = int(extract_numbers(query.data))
        if cidx == 1:
            leaders = sql_helper.db_get_top_players('pets')
            total_players = leaders[0][3]
            info = f"🏆 Лучшие игроки 🐇\n  10 из {total_players} \n----------------------------------\n"
            i = 1
            
            print("total players: " + str(total_players))
            for player in leaders:
                pname = 'без имени' if player[0] is None else player[0]
                pet_group = ''
                show_limit = 0
                for pet in player[2]:
                    if show_limit == 4:
                        break
                    show_limit += 1
                    pet_group += pet_emoji(pet)
                animal = player[2]
                info += f"{i}) *{pname}* и его {pet_group}\n"
                i += 1
            #print(info)
            bot.send_message(tid, info, parse_mode='markdown')
            bot.delete_message(query.message.chat.id, query.message.id)
            return
        elif cidx == 2:
            leaders = sql_helper.db_get_top_players('exp')
            total_players = leaders[0][3]
            info = f"🏆 Лучшие игроки 🌟\n  10 из {total_players} \n----------------------------------\n"
            i = 1
            
            print("total players: " + str(total_players))
            for player in leaders:
                pname = 'без имени' if player[0] is None else player[0]
                exp = f"🌟{player[5]}"
                pet_group = ''
                show_limit = 0
                for pet in player[2]:
                    if show_limit == 3:
                        break
                    show_limit += 1
                    pet_group += pet_emoji(pet)
                animal = player[2]
                info += f"{i}) *{pname}* {exp} и его {pet_group}\n"
                i += 1
            #print(info)
            bot.send_message(tid, info, parse_mode='markdown')
            bot.delete_message(query.message.chat.id, query.message.id)
            return
    else:
        cidx = 0

    #next_cid = 0 if cidx == len(available_items) - 1 else cidx + 1
    #item = available_items[cidx]
    
    markup = types.InlineKeyboardMarkup(row_width=2,)
    lbl = 'рейтинг'
    btn_top_pets = types.InlineKeyboardButton(f"🐇 Животные", callback_data='tops_1')
    btn_exit = types.InlineKeyboardButton('🌟 Опыт', callback_data='tops_2' )
    markup.add(btn_top_pets,btn_exit)
    # if hasattr(query,'data'):
    #     bot.edit_message_text(
    #         text=lbl,
    #         chat_id=query.message.chat.id,
    #         parse_mode='markdown', # to make some text bold with *this* in messages
    #         message_id=query.message.id,
    #         reply_markup=markup
    #     )
    # else:
    bot.send_message(query.from_user.id, lbl,parse_mode='markdown', reply_markup=markup)

# - - - - - - -  U T I L S - - - - - - - 

def extract_numbers(str, v=0):
    '''
    Used for extract variables from callback query data that was concatenated before.

    :param str: string containing some special build-in param values.
    :param v: block of numbers that need to return

    :return number: number saved in query data. First block by default 
    "rtype: string
    '''
    numbers = re.findall(r'\d+',str)
    #print('extracted: ' + numbers[v])
    return numbers[v]

# emoji was here




def anti_forward(tid, forward_date):
    '''
    anti cheat from multiple forwarding messages
    '''
    if forward_date is not None:
        print(f"-- ANTI CHEAT for {str(tid)} - - -- - -- - - - -")
        #print("forward: " + str(message.forward_date))
        penalty = 10
        sql_helper.db_stamina_down(tid,10)
        sql_helper.db_remove_money(tid, penalty)
        bot.send_message(tid, f"⚠ Мошенничество! -{penalty}💰")
        return
    
def slow_down(tid):
    current_time = time.time()

    # Reset the count if the time window has passed
    if current_time - user_message_count[tid]['first_time'] > TIME_WINDOW:
        user_message_count[tid] = {'count': 1, 'first_time': current_time}
    else:
        # Increment the count and check if it exceeds the limit
        user_message_count[tid]['count'] += 1

    if user_message_count[tid]['count'] > MESSAGE_LIMIT:
        print('-----------You are sending messages too quickly! Please wait a moment.')
        #bot.reply_to(message, 'You are sending messages too quickly! Please wait a moment.')
        return True
    else:
        # Process the message as needed
        print('- - - FREQUENCY OK')
        return False
       # bot.reply_to(message, 'Message received!')

# TODO write func that gets array from SQL and search target value in it if it exists

# - - - - - - -  M A I N  M E N U  - - - - - - - 

def next_option(message):
    print('-- -- NEXT option ----')
    #print(message.__dict__)
    if slow_down(message.from_user.id):
        return

    if message.forward_date is not None:
        print(f"-- ANTI CHEAT for {str(tid)} - - -- - -- - - - -")
        return
    if re.match('.*Зоо.*',message.text):
        #bot.register_next_step_handler(message, show_pets)
        zoo_management(message)
    elif re.match('.*Имущество.*',message.text):
        bot.reply_to(message, 'test option')
    elif re.match('.*повезёт.*',message.text):
        print(' - - work select - -')
        #do_work(message)
        lucky_way(message)
    elif re.match('.*Магазин.*',message.text):
        bot.register_next_step_handler(message, shop_select)
    elif re.match('.*Путешествие.*',message.text):
        bot.register_next_step_handler(message, travel)
    elif re.match('.*больница.*',message.text):
        vet(message)
    elif re.match('.*ТОП.*',message.text):
        show_top(message)

def get_statistics(tid):
    pet_cnt = sql_helper.db_check_owned_pets(tid)
    items = sql_helper.db_get_owned_items_group(tid)
    next_lvlexp = sql_helper.show_lvlup_target(tid)
    #box = '📦' if len(items) > 0 else ' '
    item_overview = ''
    for i in items:
        q = '' if i[2] == 1 else f"x{i[2]}"
        item_overview = item_overview + f"{item_emoji(i[0])}{q}"
    check_relax(tid)
    pinfo = sql_helper.db_get_player_info(tid)
    this_moment = datetime.now()
    time_rest = str(this_moment - pinfo[3])
    time_rest = time_rest.split('.')[0]
    lvl = pinfo[1]
    coins = pinfo[0]
    stamina = pinfo[2]   
    stamina_max = pinfo[8] 
    pet_space = pinfo[4]
    exp = pinfo[6]
    loc = habitat_emoji(pinfo[5]) 
    lvl_points = f"\n❇️Очки талантов: {pinfo[7]}" if pinfo[7] != 0 else ""; 
    lvl_taming = f"\n🔑Навык взлома: {pinfo[9]}" if pinfo[9] != 0 else ""
    lvl_lockpicking = f"\n🕸️Навык ловли: {pinfo[10]}" if pinfo[10] != 0 else ""
    player_stats = loc +' Уровень: ' + str(lvl) + '\nСила 💪: ' + str(stamina) + f" / {stamina_max} ⏳{time_rest} " +  '\nПитомцы 😺: ' + str(pet_cnt) + ' / ' + str(pet_space) + '\nДеньги 💰: ' + str(coins) + f"\nОпыт 🌟: {str(exp)} / {str(next_lvlexp)}" + lvl_points
    player_stats = player_stats + f"{lvl_taming}{lvl_lockpicking}\nВещи: {item_overview}"
    # next line must be commented before run game in production
    # player_stats = player_stats + '\n⚠ Сервер в режиме обслуживания, все действия сделанные вами в этот период не будут сохранены!'

    return player_stats



# picture grabber
@bot.message_handler(func=lambda message: True, content_types=['photo'])
def echo_allimage(message):
    print('it is image ')
    file_id = message.photo[0].file_id
    print('file id : ' + str(file_id))

#anything other messages
@bot.message_handler(func=lambda m:True)
def echo_all(message):
    #print('---------- ANYTHING -----------')
    tid = message.from_user.id
    if message.forward_date is not None:
        print(f"-- ANTI CHEAT for {str(message.from_user.id)} - - -- - -- - - - -")
        #print("forward: " + str(message.forward_date))
        #penalty = 10
        #sql_helper.db_stamina_down(message.from_user.id,10)
        #sql_helper.db_remove_money(message.from_user.id, penalty)
        #bot.send_message(message.from_user.id, f"⚠ Мошенничество! -{penalty}💰")
        return
 
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🐇 Зоопарк")
    btn2 = types.KeyboardButton("🏫 Имущество")
    btn_hospital = types.KeyboardButton("🏥 Вет.больница")
    btn3 = types.KeyboardButton("🍀 Мне повезёт")
    btn4 = types.KeyboardButton("🛒 Магазин")
    btn5 = types.KeyboardButton("✈ Путешествие")
    btn_top = types.KeyboardButton("🏆 ТОП")
    markup.add(btn1,btn_hospital,btn3,btn4,btn5,btn_top)
    bot.send_message(tid, get_statistics(tid),reply_markup=markup)
    #bot.register_next_step_handler(message, next_option)
    next_option(message)

bot.infinity_polling()


