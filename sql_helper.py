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



def db_new_player(tid,username,nickname):
    print(' - - write new user to DB - -')
    q = '''INSERT INTO players(telegram_id, invite_date, username, nick_name, coins) VALUES (%s, current_date, %s,%s, 0);'''
    cur = con.cursor()
    cur.execute(q,(tid,username,nickname))
    con.commit()

def db_add_money(tid, value):
    print('- - - write money to DB - - - ')
    q = '''UPDATE players set coins = %s where telegram_id = %s;'''

def db_buy_pet(tid,animal_id):
    print(' - - write new user to DB - -')
    q = '''insert into pets( animal_id,  owner /*petname*/) values(%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(animal_id,tid))
    con.commit()

