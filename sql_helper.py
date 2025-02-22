# test postgres for AMZOO telegram bot

import psycopg
from datetime import datetime, timedelta
import random

con = psycopg.connect('dbname=amzoo user=pet_master host=localhost password=dashakuromi application_name=amzoo')

# ==================================== CHECK BLOCK

def db_check_player_exists(tid):
    print('SQL check exist player')
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
    print('SQL check players location - - -')
    q = '''SELECT h.id from players p join habitat h on h.id = p.game_location where telegram_id = %s'''
    cur = con.cursor()
    cur.execute(q,(tid,))
    b = cur.fetchone()
    if b is None:
        result = 0
    else:
        result = b[0]

    return result

def db_check_owned_pets(tid):
    print('SQL check owned pets')
    q = '''SELECT count(*) from pets where owner = %s'''
    cur = con.cursor()
    cur.execute(q,(tid,))
    b = cur.fetchone()
    if b is None:
        result = 0
    else:
        print(f"pets: {b[0]}")
        result = b[0]
    con.commit()
    cur.close()


    return result

def db_check_owned_coins(tid):
    print('SQL check owned coins')
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
    coins, level, stamina, last_work, pet_space, game_location, exp, 7 lvl_points, 8 stamina_max, 9 lockpicking, 10 taming
    '''
    print(f"SQL get player info {tid}")
    q = '''SELECT coins, level, stamina, last_work, pet_space, game_location, exp, lvl_points, stamina_max, lockpicking, taming from players where telegram_id = %s'''
    cur = con.cursor()
    cur.execute(q,(tid,))
    b = cur.fetchone()
    con.commit()
    if b is None:
        result = 0
    else:
        #print(b)
        result = b
    
    cur.close()

    return result

def db_pet_info(id):
    """
        :param id: pet id from pets table.

        :return list: [0 id, 1 animal_id, 2 hunger, 3 health, 4 mood, 5 a.species, 6 habitat, 7 food_type,  8 price, 9 rating] of pets 
    """
    print('SQL pet_info')
    q = '''SELECT p.id, animal_id, hunger, health, mood, a.species, habitat, food_type, price, rating from pets p join animal_list a on a.id = p.animal_id where p.id = %s'''
    cur = con.cursor()
    cur.execute(q,(id,))
    con.commit()
    b = cur.fetchone()
    result = b
    return b

def db_get_owned_pets(tid):
     """
        :param tid: telegram id of current player.

        :return list: [id, animal_id, price, health, 4 hunger] from pets table
    """
     print('SQL get all players pets --')
     q = '''select pets.id, animal_id, price, health, hunger from pets join animal_list a on a.id = pets.animal_id where owner = %s;'''
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
    print('SQL get all players items')
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
        return property group by item
        :param tid: telegram id of current player.

        :return list: [item_id, ttl_price, quantity] from property and items tables
    """
    print('SQL items group')
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

def db_check_owned_item(tid, id):
    """
    Check if player owns exact item

    :return property id or 0 if have not item
    """
    #q = "SELECT count(*) FROM property WHERE owner = %s AND item_id = %s"
    q = "SELECT id FROM property WHERE owner = %s AND item_id = %s LIMIT 1;"
    cur = con.cursor()
    cur.execute(q,(tid,id))
    b = cur.fetchone()
    pid = 0 if b is None else b[0]
    return pid

def db_count_item_type(tid, id):
    """
    :param id: item id
    :return  quantity of instances
    """
    q = "SELECT count(*) FROM property WHERE owner = %s AND item_id = %s;"
    cur = con.cursor()
    cur.execute(q,(tid,id))
    b = cur.fetchone()
    return b[0]

def db_get_profit(tid):
    """
        :param tid: telegram id of current player.

        :return sum of coins for owned pets
    """
    profit_percent = 18
    print(f"Profit {tid} at " + str(datetime.now()))
    q = '''select sum(price) * %s / 100 as profit from pets p join animal_list a on a.id = p.animal_id where "owner" = %s'''
    cur = con.cursor()
    cur.execute(q,(profit_percent,tid,))
    b = cur.fetchone()
    profit = 0 if b is None else b[0]
    db_add_money(tid, profit)
    cur.close()
    con.commit()
    return profit

def db_get_profit_pg(tid, percent):
    """
    calculate and add profit with PGSQL function. Also check if player try to repeat it (cheating).
    In PG get_profit fucntion we use SELECT ... FOR UPDATE to prevent players from spam multiple message to repeat profit.
    """
    q = 'SELECT  get_profit(%s,%s) ;'
    cur = con.cursor()
    cur.execute(q,(tid,percent))
    b = cur.fetchone()[0]
    cur.close()
    con.commit()
    return b


def db_get_animal_shop(location_id, catch_mode=False):
     """
        :param location_id: location of shop. [5 - any, 4 water, 3 forest, 2 field, 1 desert]

        :return list: [animal_id, species, price, rating 3] from pets table
    """
     
     if catch_mode:
         print('-- SQL get all animals for location to catch--')
         q = '''select id, species, price, rating from animal_list al where habitat = %s and price > 0 and catch_price > 0;'''
     else:
         print('-- SQL get all animals for location to buy--')
         q = '''select id, species, price, rating from animal_list al where habitat = %s and price > 0 and catch_price is null;'''
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

def db_get_top_players(top_order):
    """
    :return list: [username, sum_points, best_animal, total_players]
    #(select animal_id from pets p2 join animal_list aa on aa.id = p2.animal_id where p2.owner = p.telegram_id order by rating desc limit 1) best_animal,
    """
    if top_order == 'pets':
        q = '''select case when nick_name = 'x' then p.username else nick_name end nick ,
        sum(rating) *  (1.0 + count(distinct animal_id)/10::numeric) best_pets,
        --array_agg(distinct animal_id order by animal_id desc) ,
        (select array_agg(animal_id order by rating desc) from pets p2 join animal_list aa on aa.id = p2.animal_id where p2.owner = p.telegram_id) best_animal,
            count(*) over () ttl , telegram_id
                from pets RIGHT JOIN players p on p.telegram_id = pets.owner 
                JOIN animal_list al on al.id = pets.animal_id
                where p.last_work > current_date - interval '14 days'
                group by username, nick_name, telegram_id order by 2 desc, 1 NULLS LAST LIMIT 10;'''
    elif top_order == 'exp':
        q = '''select case when nick_name = 'x' then p.username else nick_name end nick ,
        sum(rating) *  (1.0 + count(distinct animal_id)/10::numeric) best_pets,
        --array_agg(distinct animal_id order by animal_id desc) ,
        (select array_agg(animal_id order by rating desc) from pets p2 join animal_list aa on aa.id = p2.animal_id where p2.owner = p.telegram_id) best_animal,
            count(*) over () ttl , telegram_id, p.exp
                from pets RIGHT JOIN players p on p.telegram_id = pets.owner 
                JOIN animal_list al on al.id = pets.animal_id
                where p.last_work > current_date - interval '14 days'
                group by username, nick_name, telegram_id order by 6 desc NULLS LAST LIMIT 10;'''
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
    :return all tids for 14 days
    """
    print(" - - get all tids - - ")
    q = '''SELECT telegram_id FROM players where last_work > current_date - interval '14 days';'''
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
    print("SQL get nearby players")
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

def db_get_field(location):
    '''
    Returns array of arrays of numbers that is cells to dig
    '''
    print(f"SQL treasure fild loc:{location}")
    q = '''SELECT field FROM treasure_field WHERE location = %s'''
    cur = con.cursor()
    cur.execute(q,(location,))
    f = cur.fetchone()
    #print(f) # show all feild array 
    cur.close()
    return f[0]

def db_dig_field(location, cell, deep_cell, tid):
    '''
    Change element of subarray to 0 to mark it as digged
    tid for log only
    returns: update cell, treasure and [2]danger cells id
    '''
    q0 = 'SELECT field[%(cell)s][%(deep_cell)s], treasure, danger FROM treasure_field WHERE location = %(location)s;'

    q = '''UPDATE treasure_field SET field[%(cell)s][%(deep_cell)s] = 0 WHERE location = %(location)s;'''
    cur = con.cursor()
    cur.execute(q0,{'cell':cell, 'deep_cell':deep_cell, 'location':location})
    b = cur.fetchone()
    cur.execute(q,{'cell':cell, 'deep_cell':deep_cell, 'location':location})
    #cur.execute(q,(cell, deep_cell, location))
    con.commit()
    
    print(f"SQL digging {tid} target;treasure;danger {b}")
    cur.close()
    return b

def db_refil_pits():
    '''
    delete all old treasure feilds and create new for every location
    '''
    q = "delete from treasure_field;"
    cur = con.cursor()
    cur.execute(q,)
    cur.close()
    con.commit()
    for i in range(7):
        cel_win = random.randrange(1,40)
        cel_fail = random.randrange(1,40)
        cel_fail = random.randrange(1,40) if cel_fail == cel_win else cel_fail
        print(f"win: {cel_win} fail:{cel_fail}")
        loc = i+1
        hint = 0
        if cel_win < 9:
            hint = 1
        elif 8 < cel_win < 17: 
            hint = 2
        elif 16 < cel_win < 25:
            hint = 3
        elif 24 < cel_win < 33:
            hint = 4
        else:
            hint = 5
        print(hint)
        q = '''insert into treasure_field(create_date, field, location , hint_row, treasure , danger ) values (current_date, '{{1,2},{3,4},{5,6},{7,8},{9,10},{11,12},{13,14},{15,16},{17,18},{19,20},{21,22},{23,24},{25,26},{27,28},{29,30},{31,32}, {33,34},{35,36},{37,38},{39,40}}', %s, %s, %s, %s );'''
        cur = con.cursor()
        cur.execute(q,(loc,hint,cel_win,cel_fail))
        cur.close()
        con.commit()


def lockpick_up(tid,value):
    """
    Improve skill for stealing, and burgluring, unlocking any locks
    """
    print(' SQL lockpick up')
    q = "UPDATE players SET lockpicking = lockpicking + %s WHERE telegram_id = %s"
    cur = con.cursor()
    cur.execute(q,(value,tid))
    con.commit()
    cur.close()
    return

def taming_up(tid,value):
    """
    Improve skill for catching animals
    """
    print(' SQL lockpick up')
    q = "UPDATE players SET taming = taming + %s WHERE telegram_id = %s"
    cur = con.cursor()
    cur.execute(q,(value,tid))
    con.commit()
    cur.close()
    return

def event_exe(event):
    print(' SQL update event')
    #q = "UPDATE events SET last_executed =%s, is_active = %s WHERE name = %s"
    q = "UPDATE events SET last_executed = current_date WHERE name = %s"
    cur = con.cursor()
    cur.execute(q,(event,))
    con.commit()
    cur.close()
    return

def event_get(event):
    print('SQL get event')
    q = '''SELECT is_active, date_part('day',last_executed) FROM events WHERE name = %s'''
    cur = con.cursor()
    cur.execute(q,(event,))
    p = cur.fetchone()
    cur.close()
    return p

# ==================================== DML BLOCK

def db_new_player(tid,username,nickname):
    print('SQL write new user to DB - -')
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
    print('SQL blocker player')
    q = "UPDATE players SET invite_date = NULL, pet_space = 0 WHERE telegram_id = %s"
    cur = con.cursor()
    cur.execute(q,(tid,))
    con.commit()
    cur.close()


def db_add_money(tid, value):
    print('SQL write money to DB')
    q = '''UPDATE players set coins = coins + %s where telegram_id = %s;'''
    cur = con.cursor()
    cur.execute(q,(value,tid))
    con.commit()
    cur.close()

def db_remove_money(tid, value):
    print('SQL remove money')
    q = '''UPDATE players set coins = (CASE WHEN coins - %(value)s < 0 THEN 0 ELSE coins - %(value)s END) where telegram_id = %(tid)s;'''
    cur = con.cursor()
    cur.execute(q,{'value':value,'tid':tid})
    con.commit()
    cur.close()

def db_change_location(tid, value, coins):
    print('SQL db_change_location')
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

def db_stamina_drain(tid, value):
    """SQL function returns -1 if not enough stamina, number as result after succesful subtraction.
    """
    print('SQL stamina drain')
    q = '''SELECT get_tired(%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(tid,value))
    stamina = cur.fetchone()[0]
    print('-SQL stamina drain:' + str(stamina))
    con.commit()
    cur.close()
    return(stamina)

def db_stamina_up(tid, value, limit):
    """  sql trigger updates last_work table field
        :param tid: telegram id of current player.
        :param value: points up.

        :return None:
    """
    print('- - - update up stamina lvl to DB - - - ')
    q = '''UPDATE players set stamina = (CASE WHEN stamina + %(value)s > %(limit)s THEN %(limit)s ELSE stamina + %(value)s END) where telegram_id = %(tid)s;'''
    q2 = '''SELECT stamina FROM players WHERE telegram_id = %s;'''
    cur = con.cursor()
    cur.execute(q,{'value':value,'tid':tid,'limit':limit})
    cur.execute(q2,(tid,))
    b = cur.fetchone()
    #print('db stamina up result: ' + str(b))
    con.commit()
    cur.close()
    return

def db_exp_up(tid, value=1):
    """
    Increase experience for player
    :return record (1 if levelup 0 if no; exp to next lvl)
    """
    q = "select * FROM exp_up(%s,%s) AS (lvlup int, next_exp_up int);"
    cur = con.cursor()
    cur.execute(q,(tid,value))
    record = cur.fetchone()
    con.commit()
    cur.close()
    return record

def show_lvlup_target(tid):
    """
    exp needed to levelup
    """
    q = "select l.exp from levels l join players p on p.level + 1 = l.lvl where p.telegram_id = %s;"
    cur = con.cursor()
    cur.execute(q,(tid,))
    b = cur.fetchone()[0]
    con.commit()
    cur.close()
    return b

def db_upgrade_list(tid):
    """
    returns: id, lvl_required, info, is_available
    """
    #q = "select id, lvl_required, info FROM zoo_upgrades;"
    q = '''select u.id, lvl_required, info, p."level" = u.lvl_required avail
    FROM zoo_upgrades u join players p on p."level"+1  >= u.lvl_required and p.telegram_id = %(tid)s 
    where u.id not in (select up_id from player_knows pk where tid = %(tid)s);'''
    cur = con.cursor()
    cur.execute(q,{'tid':tid,})
    b = cur.fetchall()
    con.commit()
    cur.close()
    return b

def db_points_down(tid, up_id):
    q = "update players set lvl_points = lvl_points - 1 where telegram_id = %s"
    cur = con.cursor()
    cur.execute(q,(tid,))
    con.commit()
    q = "insert into player_knows(ldate, tid, up_id) values (now(),%s,%s)"
    cur.execute(q,(tid,up_id))
    con.commit()
    cur.close()
    return 

def db_stamina_max_up(tid):
    q = "update players set stamina_max = stamina_max + 1 where telegram_id = %s"
    cur = con.cursor()
    cur.execute(q,(tid,))
    con.commit()
    cur.close()
    return 

def db_buy_pet(tid, animal_id):
    print(' - - write to DB buy pet - -')
    q = '''SELECT buy_pet(%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(tid,animal_id))
    b = cur.fetchone()[0]
    con.commit()
    cur.close()
    return b

def db_get_pet(tid, animal_id):
    """  assign new pet to player

        :return 1 if OK 0 for :
    """
    print('SQL write to DB catch pet - -')
    q = '''INSERT INTO pets(owner, animal_id ) values (%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(tid,animal_id))
    #result = cur.fetchone()
    con.commit()
    cur.close()
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

def db_buy_item(tid, item_id, extra = 0.0):
    print(' - -  write to DB buy item - -')
    q = '''SELECT buy_item(%s,%s,%s);'''
    cur = con.cursor()
    cur.execute(q,(tid,item_id,extra))
    result = cur.fetchone()
    con.commit()
    print('result ' + str(result))
    return result[0]

def db_get_item(tid, item_id):
    print('- - - get item for free SQL INSERT- - -')
    q = '''insert into property(item_id, durability, charged, "owner") values(%s,10,true,%s) RETURNING id;'''
    cur = con.cursor()
    cur.execute(q,(item_id, tid))
    
    b = cur.fetchone()
    con.commit()
    if b is None:
        result = 0
    else:
        result = b[0]
    con.commit()
    print('GET PROPERTY: ' + str(result))
    return result

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

def db_feed_all(tid):
    """feed all animals of player to max"""
    q = "update pets SET hunger = 10 where owner = %s;"
    cur = con.cursor()
    cur.execute(q,(tid,))
    cur.close()
    con.commit()
    return

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
    return

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

def db_save_feedback(tid, rtype, text):
    '''
    save message from player to developer
    '''
    q = '''INSERT INTO feedbacks(msg, type, rdate, tid) VALUES (%s,%s, now(), %s);'''
    cur = con.cursor()
    cur.execute(q,(text,rtype,tid))
    con.commit()
    cur.close()
    return

# ==================================== SHOW BLOCK


