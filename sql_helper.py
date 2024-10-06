# test postgres for AMZOO telegram bot

import psycopg
from datetime import datetime, timedelta

con = psycopg.connect('dbname=amzoo user=pet_master host=localhost password=dashakuromi')

# ==================================== CHECK BLOCK

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

def db_check_location(tid):
    '''
    1	desert    2	field    3	forest    4	water    5	any
    '''
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



# ==================================== GET BLOCK

# maybe use this function for any type of player's info instead of many of singled 
def db_get_player_info(tid):
    '''
    coins, level, stamina, last_work
    '''
    print('- - - get player info- - -')
    q = '''SELECT coins, level, stamina, last_work from players where telegram_id = %s'''
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

def db_pet_info(id):
    """
        :param id: pet id from pets table.

        :return list: [0 id, 1 animal_id, 2 hunger, 3 health, 4 mood, 5 a.species, 6 habitat, 7 food_type,  8 price] of pets 
    """
    print('--- DB pet_info ---')
    q = '''SELECT p.id, animal_id, hunger, health, mood, a.species, habitat, food_type, price from pets p join animal_list a on a.id = p.animal_id where p.id = %s'''
    cur = con.cursor()
    cur.execute(q,(id,))
    b = cur.fetchone()
    result = b
    print (b)
    return b

def db_get_owned_pets(tid):
     """
        :param tid: telegram id of current player.

        :return list: [id, animal_id, price] from pets table
    """
     print('-- get all players pets --')
     q = '''select pets.id, animal_id, price from pets join animal_list a on a.id = pets.animal_id where owner = %s;'''
     pet_list = []

     with con.cursor() as cur:
          cur.execute(q,(tid,))
          b = cur.fetchall()
          #print(list(b))
          for record in b:
               pet_list.append(record)
               
     return pet_list

# ==================================== DML BLOCK

def db_new_player(tid,username,nickname):
    print(' - - write new user to DB - -')
    q = '''INSERT INTO players(telegram_id, invite_date, username, nick_name, coins) VALUES (%s, current_date, %s,%s, 0);'''
    cur = con.cursor()
    cur.execute(q,(tid,username,nickname))
    con.commit()

def db_add_money(tid, value):
    print('- - - write money to DB - - - ')
    q = '''UPDATE players set coins = coins + %s where telegram_id = %s;'''
    cur = con.cursor()
    cur.execute(q,(value,tid))
    con.commit()

def db_stamina_down(tid, value):
    print('- - - update down stamina lvl to DB - - - ')
    q = '''UPDATE players set stamina = stamina - %s where telegram_id = %s;'''
    q2 = '''SELECT stamina FROM players WHERE telegram_id = %s;'''
    cur = con.cursor()
    cur.execute(q,(value,tid))
    cur.execute(q2,(tid,))
    b = cur.fetchone()
    print('db stamina down result: ' + str(b))
    con.commit()

def db_stamina_up(tid, value):
    """  sql trigger updates last_work table field
        :param tid: telegram id of current player.
        :param value: points up.

        :return None:
    """
    print('- - - update up stamina lvl to DB - - - ')
    q = '''UPDATE players set stamina = stamina + %s where telegram_id = %s;'''
    q2 = '''SELECT stamina FROM players WHERE telegram_id = %s;'''
    cur = con.cursor()
    cur.execute(q,(value,tid))
    cur.execute(q2,(tid,))
    b = cur.fetchone()
    print('db stamina up result: ' + str(b))
    con.commit()


def db_buy_pet(animal_id,tid):
    print(' - - write new user to DB - -')
    q = '''SELECT buy_pet(%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(animal_id,tid))
    result = cur.fetchone()
    con.commit()
    print('result ' + str(result))
    return result[0]

def db_sell_pet(pet_id):
    print(' - - sell pet DB func - -')
    q = '''SELECT sell_pet(%s);'''
    cur = con.cursor()
    cur.execute(q,(pet_id,))
    result = cur.fetchone()
    print('sql sel result: ' + str(result))
    con.commit()

def db_change_hunger(pet_id: int, feed: bool, val: int=1):
    """  
        :param pet_id: telegram id of current player.
        :param feed:bool is feeding or not
        :param val: points

        :return None:
    """
    print(' - - change hunger pet DB func - -')
    q = '''SELECT change_hunger(%s,%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(pet_id,feed,val))
    result = cur.fetchone()
    print('sql sel result: ' + str(result))
    con.commit()

def db_change_hunger_all():
    """  
        lowers all pets hunger level on 1 (one)
    """
    print(' - - change hunger all pet DB func - -')
    q = '''select change_hunger(id, false , 1) from pets p where health > 0;;'''
    cur = con.cursor()
    cur.execute(q)
    result = cur.fetchone()
    print('sql sel result: ' + str(result))
    con.commit()


# ==================================== SHOW BLOCK


