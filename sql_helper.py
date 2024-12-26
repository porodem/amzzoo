# test postgres for AMZOO telegram bot

import psycopg
from datetime import datetime, timedelta

con = psycopg.connect('dbname=amzoo user=pet_master host=localhost password=dashakuromi application_name=amzoo')

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
#TODO add commit transaction to all DB functions

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
    coins, level, stamina, last_work, pet_space, game_location
    '''
    print('- - - get player info- - -')
    q = '''SELECT coins, level, stamina, last_work, pet_space, game_location from players where telegram_id = %s'''
    cur = con.cursor()
    cur.execute(q,(tid,))
    b = cur.fetchone()
    con.commit()
    if b is None:
        result = 0
    else:
        #print(b)
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
    con.commit()
    b = cur.fetchone()
    result = b
    print (b)
    return b

def db_get_owned_pets(tid):
     """
        :param tid: telegram id of current player.

        :return list: [id, animal_id, price, health] from pets table
    """
     print('-- get all players pets --')
     q = '''select pets.id, animal_id, price, health from pets join animal_list a on a.id = pets.animal_id where owner = %s;'''
     pet_list = []

     with con.cursor() as cur:
          cur.execute(q,(tid,))
          b = cur.fetchall()
          #print(list(b))
          for record in b:
               pet_list.append(record)
          con.commit()
               
     return pet_list

def db_get_owned_items(tid):
    """
        :param tid: telegram id of current player.

        :return list: [property_id, item_name, price, (3) charged, location, item_id, 6 durability] from property and items tables
    """
    print('SQL get all players items --')
    q = '''select  p.id, i."name", price, charged, location, i.id, durability from  property p join items i on i.id = p.item_id  where owner = %s;'''
    item_list = []

    with con.cursor() as cur:
        cur.execute(q,(tid,))
        b = cur.fetchall()
        #print(list(b))
        for record in b:
            item_list.append(record)
        con.commit()
            
    return item_list

def db_get_owned_items_group(tid):
    """
        :param tid: telegram id of current player.

        :return list: [item_id, ttl_price, quantity] from property and items tables
    """
    print('-- get all players items --')
    q = '''select  i.id, sum(price) ttl_price, count(*) as quantity from  property p join items i on i.id = p.item_id where owner = %s group by 1;'''
    item_list = []

    with con.cursor() as cur:
        cur.execute(q,(tid,))
        b = cur.fetchall()
        #print(list(b))
        for record in b:
            item_list.append(record)
        con.commit()
            
    return item_list

def db_get_profit(tid):
    """
        :param tid: telegram id of current player.

        :return sum of coins for owned pets
    """
    print(f"Profit {tid} at " + str(datetime.now()))
    q = '''select sum(price)/7 as profit from pets p join animal_list a on a.id = p.animal_id where "owner" = %s'''
    cur = con.cursor()
    cur.execute(q,(tid,))
    b = cur.fetchone()
    profit = 0 if b[0] is None else b[0]
    db_add_money(tid, profit)
    return profit

def db_get_animal_shop(location_id, catch_mode=False):
     """
        :param location_id: location of shop. [5 - any, 4 water, 3 forest, 2 field, 1 desert]

        :return list: [animal_id, species, price] from pets table
    """
     
     if catch_mode:
         print('-- SQL get all animals for location to catch--')
         q = '''select id, species, price from animal_list al where habitat = %s and price > 0 and catch_price > 0;'''
     else:
         print('-- SQL get all animals for location to buy--')
         q = '''select id, species, price from animal_list al where habitat = %s and price > 0 and catch_price is null;'''
     pet_list = []

     with con.cursor() as cur:
          cur.execute(q,(location_id,))
          b = cur.fetchall()
          #print(list(b))
          for record in b:
               pet_list.append(record)
          con.commit()
               
     return pet_list

def db_get_animal_for_catch(location_id):
    """
        :param location_id: location of shop. [5 - any, 4 water, 3 forest, 2 field, 1 desert]

        :return list: [animal_id, species, price, catch_price, catch_difficulty, catch_chance] from pets table
    """     

    q = '''select id, species, price, catch_price, catch_difficulty, catch_chance  from animal_list al where habitat = %s and price > 0 and catch_price > 0;'''
    pet_list = []

    with con.cursor() as cur:
        cur.execute(q,(location_id,))
        b = cur.fetchall()
        #print(list(b))
        for record in b:
            pet_list.append(record)
        con.commit()
               
    return pet_list

def db_get_bazar_shop_items(location_id):
    """
    :param location_id: location of shop. [5 - any, 4 water, 3 forest, 2 field, 1 desert]
    :return list: [item_id, name, price, description] from pets items
    """
    q = 'SELECT id, name, price, description FROM items WHERE location = %s;'
    items_available = []

    with con.cursor() as cur:
        cur.execute(q,(location_id,))
        b = cur.fetchall()
        for record in b:
            items_available.append(record)
        con.commit()

    return items_available;

def db_get_top_players():
    """
    :return list: [username, sum_points, best_animal, total_players]
    """
    q = '''select case when nick_name = 'x' then p.username else nick_name end nick ,
      sum(animal_id) *  (1.0 + count(distinct animal_id)/10::numeric) ,
      max(animal_id) ,
        count(*) over () ttl , telegram_id
            from pets RIGHT JOIN players p on p.telegram_id = pets.owner 
            group by username, nick_name, telegram_id order by 2 desc NULLS LAST LIMIT 10;'''
    leaders = []
    with con.cursor() as cur:
          cur.execute(q)
          b = cur.fetchall()
          #print(list(b))
          for record in b:
               leaders.append(record)
    #print(list(leaders))
    con.commit()
    return leaders

def db_get_all_tids():
    """
    :return all tids
    """
    print(" - - get all tids - - ")
    q = '''SELECT telegram_id FROM players where invite_date is not null;'''
    all_players = []
    with con.cursor() as cur:
        cur.execute(q) 
        b = cur.fetchall()
        for line in b:
            all_players.append(line[0])
    con.commit()
    print(str(len(all_players)) + " " + str(list(all_players)))
    return(all_players)

def db_get_nearby_players(location = None):
    """
    :return players in same locaton [0 tid 1 username 2 nick]
    """
    print(" - - get all nearby players - - ")
    q = '''SELECT telegram_id, username, nick_name FROM players where game_location = %s and invite_date is not null;'''
    all_players = []
    with con.cursor() as cur:
        cur.execute(q,(location,))
        b = cur.fetchall()
        for line in b:
            all_players.append(line)
        con.commit()
    print(str(len(all_players)) + " " + str(list(all_players)))
    return(all_players)

def db_get_zoo_password(tid):
    print('SQL get zoo_pass')
    q = '''SELECT zoo_pass FROM players WHERE telegram_id = %s'''
    cur = con.cursor()
    cur.execute(q,(tid,))
    p = cur.fetchone()
    cur.close()
    return p[0]

def db_get_cheapest_pet(tid):
    '''
    Returns: list: [pet ID, PRICE, animal_id]
    '''
    print('SQL get cheapest pet')
    q = '''select p.id, al.price, p.animal_id from pets p join animal_list al on al.id = p.animal_id where "owner" = %s order by price limit 1;'''
    cur = con.cursor()
    cur.execute(q,(tid,))
    pet = cur.fetchone()
    cur.close()
    return pet

# ==================================== DML BLOCK

def db_new_player(tid,username,nickname):
    print(' - - write new user to DB - -')
    q = '''INSERT INTO players(telegram_id, invite_date, username, nick_name, coins) VALUES (%s, current_date, %s,%s, 0);'''
    cur = con.cursor()
    cur.execute(q,(tid,username,nickname))
    con.commit()
    cur.close()

def db_rename_player(tid,nickname):
    print(' SQL rename player')
    q = "UPDATE players SET nick_name = %s WHERE telegram_id = %s"
    cur = con.cursor()
    cur.execute(q,(nickname,tid))
    con.commit()
    cur.close()

def db_blocker_player(tid):
    '''
    bot was blocked by this user 
    '''
    print(' SQL blocker player')
    q = "UPDATE players SET invite_date = NULL, pet_space = 0 WHERE telegram_id = %s"
    cur = con.cursor()
    cur.execute(q,(tid,))
    con.commit()
    cur.close()


def db_add_money(tid, value):
    print('- - - write money to DB - - - ')
    q = '''UPDATE players set coins = coins + %s where telegram_id = %s;'''
    cur = con.cursor()
    cur.execute(q,(value,tid))
    con.commit()
    cur.close()

def db_remove_money(tid, value):
    print('- - - SQL remove money  - - - ')
    q = '''UPDATE players set coins = (CASE WHEN coins - %(value)s < 0 THEN 0 ELSE coins - %(value)s END) where telegram_id = %(tid)s;'''
    cur = con.cursor()
    cur.execute(q,{'value':value,'tid':tid})
    con.commit()
    cur.close()

def db_change_location(tid, value, coins):
    print('- - - write money to DB - - - ')
    q = '''UPDATE players set game_location = %s, coins = coins - %s where telegram_id = %s;'''
    cur = con.cursor()
    cur.execute(q,(value,coins,tid))
    con.commit()
    cur.close()

def db_stamina_down(tid, value):
    print(f"SQL stamina down {value}")
    q = '''UPDATE players set stamina = (CASE WHEN stamina - %(value)s < 0 THEN 0 ELSE stamina - %(value)s END) where telegram_id = %(tid)s;'''
    q2 = '''SELECT stamina FROM players WHERE telegram_id = %s;'''
    cur = con.cursor()
    cur.execute(q,{'value':value,'tid':tid})
    cur.execute(q2,(tid,))
    b = cur.fetchone()
    #print('db stamina down result: ' + str(b))
    con.commit()
    cur.close()

def db_stamina_up(tid, value):
    """  sql trigger updates last_work table field
        :param tid: telegram id of current player.
        :param value: points up.

        :return None:
    """
    print('- - - update up stamina lvl to DB - - - ')
    q = '''UPDATE players set stamina = (CASE WHEN stamina + %(value)s > 10 THEN 10 ELSE stamina + %(value)s END) where telegram_id = %(tid)s;'''
    q2 = '''SELECT stamina FROM players WHERE telegram_id = %s;'''
    cur = con.cursor()
    cur.execute(q,{'value':value,'tid':tid})
    cur.execute(q2,(tid,))
    b = cur.fetchone()
    #print('db stamina up result: ' + str(b))
    con.commit()
    cur.close()


def db_buy_pet(tid, animal_id):
    print(' - - write to DB buy pet - -')
    q = '''SELECT buy_pet(%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(tid,animal_id))
    result = cur.fetchone()
    con.commit()
    print('result ' + str(result))
    return result[0]

def db_get_pet(tid, animal_id):
    """  assign new pet to player

        :return 1 if OK 0 for :
    """
    print(' - - write to DB catch pet - -')
    q = '''INSERT INTO pets(owner, animal_id ) values (%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(tid,animal_id))
    #result = cur.fetchone()
    con.commit()
    #print('result ' + str(result))
    return #result[0]

def db_sell_pet(pet_id):
    print(' - - sell pet DB func - -')
    q = '''SELECT sell_pet(%s);'''
    cur = con.cursor()
    cur.execute(q,(pet_id,))
    result = cur.fetchone()
    print('sql sel result: ' + str(result))
    con.commit()
    cur.close()

def db_remove_pet(pid):
    print('- - - SQL remove pet  - - -')
    q = '''DELETE FROM pets where id = %s;'''
    cur = con.cursor()
    cur.execute(q,(pid,))
    con.commit()
    return

def db_buy_item(tid, item_id):
    print(' - -  write to DB buy item - -')
    q = '''SELECT buy_item(%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(tid,item_id))
    result = cur.fetchone()
    con.commit()
    print('result ' + str(result))
    return result[0]

def db_remove_property(pid):
    print('- - - SQL remove property  - - -')
    q = '''DELETE FROM property where id = %s'''
    cur = con.cursor()
    cur.execute(q,(pid,))
    con.commit()
    return

def db_decay_property(pid,value=1):
    '''
    damage on item during usage
    '''
    print('SQL decay property')
    q = 'UPDATE property SET durability = (CASE WHEN durability - %(value)s < 0 THEN 0 ELSE durability - %(value)s END) where id = %(pid)s'
    cur = con.cursor()
    cur.execute(q,{'value':value,'pid':pid})
    cur.close()
    con.commit()
    return


def db_delete_property(item_id):
    print('- - - SQL remove property  - - -')
    q = '''delete from property p where id = (select id from property p where item_id = %s limit 1);'''
    cur = con.cursor()
    cur.execute(q,(item_id,))
    con.commit()
    return

def db_update_property(pid, switch: bool=None, value: int=0):
    """  sql trigger updates last_work table field
        :param pid: property ID.
        :param switch: Change state of item.
        :param value: durability changes on than value

        :return item:
    """
    print('- - - SQL update property  - - -')
    if switch is not None:
        print('-- SQL change charged')
        q = 'UPDATE property SET charged = %s where id = %s'
        cur = con.cursor()
        cur.execute(q,(switch,pid))

    if value != 0:
        print('-- SQL change durability')
        q = '''UPDATE property SET durability = durability + %s where id = %s'''
        cur = con.cursor()
        cur.execute(q,(value,pid))

    q2 ='SELECT * from property WHERE id = %s'
    cur = con.cursor()
    cur.execute(q2,(pid,))
    result = cur.fetchone()
    con.commit()
    print(list(result))
    return result

def db_change_pet_space(tid, value):
    print('- - - SQL update pet space - - - ')
    q = '''UPDATE players set pet_space = pet_space + %s where telegram_id = %s;'''
    #TODO maby add exhaustion for stamina
    cur = con.cursor()
    cur.execute(q,(value,tid))
    con.commit()
    cur.close()
    return

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
    cur.close()

def db_change_hunger_all():
    """  
        lowers all pets hunger level on 1 (one)

        :return list: [owner, animal_id, health]
    """
    print(' - - change hunger all pet DB func - -')
    q = '''select change_hunger(id, false , 1) from pets p where health > 0;;'''
    q2 = '''select "owner", animal_id, health FROM pets p join players u on u.telegram_id = p.owner where hunger < 3 and pet_space <> 0;'''
    cur = con.cursor()
    cur.execute(q)
    cur.execute(q2)
    hungry_pets = cur.fetchall()
    print('sql hunger all result: ' + str(hungry_pets))
    cur.close()
    con.commit()
    cur.close()
    return hungry_pets

def db_cure_pet(pet_id: int):
    """  
        DEPRICATED
        :param pet_id: id of cured pet.

        :return None:
    """
    print(' - - SQL pet curing - -')
    q = '''UPDATE pets SET health = 10 where id = %s;'''
    q2 = '''SELECT animal_id from pets WHERE id = %s'''
    cur = con.cursor()
    cur.execute(q,(pet_id,))
    cur.execute(q2,(pet_id,))
    result = cur.fetchone()[0]
    con.commit()
    cur.close()
    return result

def db_buy_healing(pet_id: int, cost: int, tid: int):
    """
    """
    q = '''SELECT buy_healing(%s,%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(pet_id,cost,tid))
    result = cur.fetchone()[0] # animal id from emoji; -1 if not enough money
    con.commit()
    cur.close()
    return result

def db_infect_pets():
    '''
    epidemic
    '''
    q = '''update pets set health = health - 4 where animal_id <> 0 and id % (random() *10 + 1)::int = 0 returning owner;'''
    infected_pet_list = []

    with con.cursor() as cur:
        cur.execute(q)
        b = cur.fetchall()
        #print(list(b))
        for record in b:
            infected_pet_list.append(record)
        con.commit()
            
    return infected_pet_list

def db_change_health(pet_id: int, cure: bool=False, val: int=1):
    """  
        :param pet_id: telegram id of current player.
        :param cure:bool is healing or not
        :param val: points

        :return None:
    """
    print(' - - change Health pet DB func - -')
    q = '''SELECT change_health(%s,%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(pet_id,cure,val))
    result = cur.fetchone()
    print('sql sel result: ' + str(result))
    con.commit()
    cur.close()

def db_change_zoo_pass(tid, password):
    '''
    set password to protect zoo from theifs
    '''
    print(' - - SQL set zoo pass - -')
    q = '''UPDATE players SET zoo_pass = %s WHERE telegram_id = %s;'''
    cur = con.cursor()
    cur.execute(q,(password, tid))
    con.commit()
    cur.close()
    return 
# ==================================== SHOW BLOCK


