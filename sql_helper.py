# test postgres for AMZOO telegram bot

import psycopg
from datetime import datetime, timedelta

con = psycopg.connect('dbname=amzoo user=pet_master host=localhost password=dashakuromi')

def db_check_player_exists(tid):
    print('- - - check exist player - - -')
    q = '''SELECT telegram_id from players where telegram_id = %s'''
    cur = con.cursor()
    cur.execute(q,(tid,))
    b = cur.fetchone()
    if b is None:
        result = None
    else:
        print(b[0])
        result = b[0]

    return result

def db_check_owned_pets(tid):
    print('- - - check exist player - - -')
    q = '''SELECT count(*) from pets where owner = %s'''
    cur = con.cursor()
    cur.execute(q,(tid,))
    b = cur.fetchone()
    if b is None:
        result = 0
    else:
        print(b[0])
        result = b[0]

    return result

def db_check_owned_coins(tid):
    print('- - - check exist player - - -')
    q = '''SELECT coins from players where telegram_id = %s'''
    cur = con.cursor()
    cur.execute(q,(tid,))
    b = cur.fetchone()
    if b is None:
        result = 0
    else:
        print(b[0])
        result = b[0]

    return result

def db_get_player_info(tid):
    print('- - - get player info- - -')
    q = '''SELECT coins, level from players where telegram_id = %s'''
    cur = con.cursor()
    cur.execute(q,(tid,))
    b = cur.fetchone()
    if b is None:
        result = 0
    else:
        print(b[0])
        print(b[1])
        result = b

    return result

def db_check_location(tid):
    print('- - - check players location - - -')
    q = '''SELECT h.id from players p join habitat h on h.id = p.game_location where telegram_id = %s'''
    cur = con.cursor()
    cur.execute(q,(tid,))
    b = cur.fetchone()
    if b is None:
        result = 0
    else:
        print(b[0])
        result = b[0]

    return result


def db_new_player(tid,username,nickname):
    print(' - - write new user to DB - -')
    q = '''INSERT INTO players(telegram_id, invite_date, username, nick_name, coins) VALUES (%s, current_date, %s,%s, 0);'''
    cur = con.cursor()
    cur.execute(q,(tid,username,nickname))
    con.commit()

def db_add_money(tid, value):
    print('- - - write money to DB - - - ')
    q = '''UPDATE players set coins = %s where telegram_id = %s;'''

def db_buy_pet(animal_id,tid):
    print(' - - write new user to DB - -')
    q = '''SELECT buy_pet(%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(animal_id,tid))
    con.commit()

# ==================================== SHOW BLOCK

def db_get_owned_pets(tid):
     print('-- get all players pets --')
     q = 'select id, animal_id from pets where owner = %s;'
     tid_list = []

     with con.cursor() as cur:
          cur.execute(q)
          b = cur.fetchall()
          print(type(b))
          print(list(b))
          for record in b:
               tid_list.append(record[0])
               
     return tid_list
