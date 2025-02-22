create role pet_master with login createdb;

create database amzoo;

grant pg_read_server_files to pet_master;

create table players(telegram_id int8 primary key, invite_date date, username text, first_name text, nick_name text,
coins smallint default 0, level int default 1,
game_location int default 5 references habitat(id),
stamina int default 5 check (stamina > -1 and stamina < 11)
);

alter table players alter column coins set not null;

alter table players add column level int default 1;

alter table players add column stamina int default 5 check (stamina > -1 and stamina < 11)

alter table players drop column stamina;

alter table players drop column levle;

alter table players add column last_work timestamp default now();

alter table players add constraint pkey_tid primary key (telegram_id)

alter table players add column pet_space int default 4;

alter table players add column zoo_pass int default 0 check (zoo_pass > -1 )

alter table players add column plant_food int default 10 check (plant_food > -1)

alter table players add column meat_food int default 10 check (plant_food > -1)

alter table players add column exp int default 0;

alter table players add column lvl_points int default 0;

alter table players  drop constraint players_stamina_check 

alter table players add constraint players_stamina_check check (stamina > -1)

alter table players add column stamina_max int default 10;

update players set stamina_max = stamina_max + 1 where telegram_id = 

update players set stamina_max = 10;

alter table players add column lockpicking smallint default 0;

alter table players add column taming smallint default 0;

comment on column players.pet_space is 'how maby pets can obtain. 0 if player blocks bot'

drop  table players cascade;

select * from pets p 

select * from players p ;

select

delete from players where telegram_id = 775803031

select buy_pet(6472394157,3)

create table zoo_system(owner int8 unique references players(telegram_id),
name text, -- system name (guard, electric, fire etc.)
zoo_pass int default 0,
pass_update timestamp,
beaking_tryes int default 0,
beaking_success int default 0,
last_stealing timestamp)

insert into zoo_system(owner)  select telegram_id from players ;

select * from zoo_system

drop table zoo_system

select * from players p 


create table animal_list(
id int8 primary key,
species text,
habitat int references habitat(id),
food_type int references food_type(id), 
price int)

alter table animal_list add column catch_price int;

alter table animal_list add column catch_difficulty int; -- how much stamina you loss on try

alter table animal_list add column catch_chance int; -- percents % 17 for dice and other 1-6 games

alter table animal_list add column rating int;

select species, rating from animal_list al order by rating desc;

insert into animal_list values(0,'bones',5,0,0)

0;Кости;5;0;0

truncate  animal_list ;

create table tpets(id int references animal_list, species text);

create table pets(
id int8 generated always as identity,
animal_id int8 references animal_list(id),
owner int8 references players(telegram_id),
petname text,  hunger int default 6 check (hunger < 11 and hunger >= 0),
health int default 10 check( health > -1), 
mood int default 3);

alter table pets add column shit smallint default 0;


drop table pets;

select * from pets;

select * from pets;

select * from players p 

create or replace function fill_pet() returns trigger 
as $$
begin 
	new.species = (select species from animal_list where id = new.id);
	new.habitat = (select habitat from animal_list where id = new.id);
	new.food_type = (select name from animal_list where id = new.id);
	return new;
end;
$$ language plpgsql;

create trigger t_before_row before insert on tpets for each row execute function fill_pet();

insert into tpets(id) values (1)

select * from tpets;


create temp table anlist(
id int8 primary key,
species text,
habitat int ,
food_type int, 
price int,
catch_price int,
catch_difficulty int ,
catch_chance int,
rating int
)

copy animal_list(id,species,habitat,food_type,price,catch_price,catch_difficulty,catch_chance) from 'C:\Python\Python310\Scripts\amzzoo\a.csv' delimiter ';' csv header encoding 'WIN1251'

create temp table anlist(id int, name text)

copy anlist from 'C:\Program Files\PostgreSQL\17\animals_b.csv' delimiter ';' csv header -- encoding 'WIN1251'

insert into animal_list (
select n.* from anlist n left join animal_list i on i.id = n.id where i.id is null
)

select * from anlist

drop table  anlist 

delete from property where owner = 775803031

select * from players p 

select * from property p 

select * from pets p  where "owner" = 775803031

select * from animal_list al --where catch_price > 0 ;

update animal_list o set
price = a.price, catch_price = a.catch_price, catch_difficulty = a.catch_difficulty , catch_chance = a.catch_chance
from (select * from anlist ) a  where o.id = a.id;

--29.01.2025 update all columnse from file but id
update animal_list o set 
price = a.price, catch_price = a.catch_price, catch_difficulty = a.catch_difficulty , catch_chance = a.catch_chance, species = a.species, habitat = a.habitat, 
food_type = a.food_type, rating = a.rating
from (select * from anlist ) a  where o.id = a.id;


merge into animal_list a using anlist b on a.id = b.id

insert into animal_list values(5,'Черепаха',5,2,15)

insert into animal_list values(6,'Индюк',5,2,20)

create table moods(id int primary key, value text);

insert into moods values(1, 'ill'),(2,'sad'),(3,'ok'),(4,'scary'),(5,'happy'),(6,'love'),(7,'cold'),(8,'hot'),(9,'sleep'),(10,'angry'),(0,'dead'),(100,'ghost');

create table habitat(id int primary key, value text)

alter table habitat add column travel_price int;

insert into habitat values(1,'desert'),(2,'field'),(3,'forest'),(4,'water'),(5,'any')

create table food_type(id int primary key , name text)

insert into food_type values (0,'nothing'),(1,'omnivore'),(2,'herbivore'),(3,'carnivore')

create table property(id int primary key , name text);

select * from habitat h 

insert into habitat values(6,'america',20) # TODO

update habitat set travel_price = 12 where id = 3;

select species, rating from animal_list al order by rating 

union select * from  food_type ft 

truncate food_type cascade;

create table items(id int primary key, 
	name text,
	price int, 
	location int references habitat(id),
	description text
	)
	
	alter table items owner to pet_master;

alter table items add column description text;
	
create table property(
	id int primary key generated always as identity, 
	item_id int references items(id),
	durability int default 10 check (durability < 11 and durability >= -1),	
	charged boolean default false, -- if it contain something, charged, enabled ect.
	owner int8 references players(telegram_id)
	);

create table feedbacks(
	id int primary key generated always as identity, 
	msg text,
	type int, -- 0 negative 1 posttive 2 question
	rdate timestamp,
	tid int8
)

select username, nick_name, tid, rdate, msg from feedbacks f join players p on p.telegram_id  = f.tid order by rdate desc;

select * from pets p 

-- db_get_owned_items_group

select  i.id, sum(price) ttl_price, count(*) as quantity from  property p join items i on i.id = p.item_id where owner = 775803031 group by 1 --where owner = %s	
	


copy items from 'C:\Program Files\PostgreSQL\17\items.csv' delimiter ';' csv header -- encoding 'WIN1251'

copy animal_list(id,species,habitat,food_type,price) from 'C:\Python\Python310\Scripts\amzzoo\a.csv' delimiter ';' csv header encoding 'WIN1251'

create temp table new_items4(id int, name text, price int, location int, description text );

drop table new_items4

copy new_items4 from 'C:\Program Files\PostgreSQL\17\items.csv' delimiter ';' csv header -- encoding 'WIN1251'

insert into items select * from new_items n where (select id from items  ) <> n.id

insert into items (
select n.* from new_items4 n left join items i on i.id = n.id where i.id is null
)

update items i set price = n.price, "location" = n.location, description = n.description from new_items4 n where n.id = i.id 

insert into items values(10,'Пасспорт',5,5)

select * from items i ;

UPDATE players set stamina = (case when stamina - 1 < 0 then 0 else stamina-1 end)  where telegram_id = 1969292042
returning stamina 

SELECT telegram_id, username, nick_name FROM players

select * from habitat h ;

truncate items cascade;

drop database amzoo


create role pet_master with password 'dashakuromi'

select p.id, i."name", price, location from  property p join items i on i.id = p.item_id ;

select * from property p 

select id from property p where item_id = 30 and "owner" = 775803031 limit 1;

select * from players p ;

select * from items i ;

drop table property ;

alter table property add column location int default 5 not null;

alter table items drop column 

alter table property add column charged boolean default false;

	
create or replace function buy_item(tid int8, item int8)
returns int 
language plpgsql
as $$
declare item_price int;
player_coins int;
begin
	select coins into player_coins from players where telegram_id = tid;
	select price into item_price from items where id = item; 
	if item_price > player_coins then 
		return 0;
	end if;
	insert into property(item_id, owner) values(item,tid);
	update players set coins = (coins - item_price) where telegram_id = tid;
	return 1;
end;
$$;
end

-- ver 2 08.02.25 price multiplier
create or replace function buy_item(tid int8, item int8, extra_price double precision)
returns int 
language plpgsql
as $$
declare item_price int;
player_coins int;
begin
	select coins into player_coins from players where telegram_id = tid;
	select price into item_price from items where id = item; 
	item_price = (item_price * extra_price)::int;
	if item_price > player_coins then 
		return 0;
	end if;
	insert into property(item_id, owner) values(item,tid);
	update players set coins = (coins - item_price) where telegram_id = tid;
	return 1;
end;
$$;
end

select (10 * 1.1)::int

delete from property where item_id = 10

select buy_item(6472394157, 6)

select username, p2.* from players p join property p2  on p2."owner" = p.telegram_id ;

delete from property p where id = (select id from property p where item_id = 5 limit 1);

select id from property p where item_id = 5

delete from pets where animal_id = 0;

UPDATE players set pet_space = pet_space + 1 where telegram_id =775803031

update players set exp = 50 where invite_date < now() - interval '2 months' returning players.username , nick_name 

create or replace function buy_pet(tid int8, animal int8)
returns int 
language plpgsql
as $$
declare pet_price int;
player_coins int;
begin
	select coins into player_coins from players where telegram_id = tid;
	select price into pet_price from animal_list where id = animal; 
	if pet_price > player_coins then 
		return 0;
	end if;
	insert into pets(animal_id, owner) values(animal,tid);
	update players set coins = (coins - pet_price) where telegram_id = tid;
	return 1;
end;
$$;
end

-- SELL PET
create or replace function sell_pet(pet_id int8)
returns int 
language plpgsql
as $$
declare 
sell_price int;
tid int8;
begin
	select price/2, p.owner  into sell_price, tid  from animal_list a join pets p on p.animal_id = a .id where p.id = pet_id; 
	raise notice 'sell price: %', sell_price;
	delete from pets where id = pet_id;
	update  players set coins = (coins + sell_price) where telegram_id = tid;
	return 1;
end;
$$;
end

select p.*, p2.coins from pets p join players p2 on p."owner"  = p2.telegram_id 

select 1 into a 

select sell_pet(37) 

select  buy_pet(6472394157,3)

select * from pets p --where "owner" = 6472394157;

select * from players p ;

update players set coins  = coins + 1 where telegram_id = 775803031

-- last work reset BUGGY version DONT USE!
create or replace function work_reset() returns trigger 
as $$
begin 
	new.last_work =  now() ;
	return new;
end;
$$ language plpgsql;

-- 22.02.25 it works
create or replace function work_reset() returns trigger 
as $$
begin 
	if new.stamina < old.stamina then
		new.last_work = now();
	else
		new.last_work = date_trunc('hour',now()) + interval '1 minute' * date_part('minute', old.last_work)  ;
	end if;
	return new;
end;
$$ language plpgsql;

create trigger t_work_res before update of stamina on players for each row execute function work_reset();

drop trigger t_work_res on  players; 

select * from players p 

insert into players(telegram_id) values(1452544471)

-- change hunger level

create or replace function change_hunger(pet_id int8, feeding boolean, value int) 
returns int
language plpgsql
as $$
declare 
hunger_before int;
health_before int;
begin
	select hunger into hunger_before from pets where id = pet_id;
	if feeding then
		if hunger_before + value > 10 then
			update pets set hunger = 10 where id = pet_id;
		else
			update pets set hunger = hunger + value where id = pet_id;
		end if;
	else		
		if hunger_before = 0 then
			select health into health_before from pets where id = pet_id;
			if health_before = 1 then
				update pets set animal_id = 0, mood = '3' where id = pet_id;
			else
				update pets set health = health - 1 where id = pet_id;
			end if;
	    else
	    	update pets set hunger = hunger - 1 where id = pet_id;
	    end if;
	end if;
    return 1;
end;
$$;
end

select change_hunger(7, true , 12)

select change_hunger(id, false , 1) from pets p where health > 0;

select * from pets where id = 1111;

select * from animal_list al ;

select * from players;

create temp table t(b boolean)

insert into t values('True')

select animal_id, "owner" from pets p where hunger < 2;



update pets set hunger = hunger - 1 where hunger > 0;

select sum(price)/4 as profit from pets p join animal_list a on a.id = p.animal_id where "owner" = 775803031

-- full healing for money

create or replace function buy_healing(pet_id int8, heal_cost int, t_id int8)
returns int
language plpgsql
as $$
declare
a_id int;
player_coins int;
begin
	select coins into player_coins from players where telegram_id = t_id;
	if heal_cost > player_coins then
		return -1;
	end if;
	UPDATE pets SET health = 10 where id = pet_id;
	update players set coins = coins - heal_cost where telegram_id = t_id;
	select animal_id into a_id from pets where id = pet_id;
	return a_id; 
end;
$$;
end

player_coins int;
begin
	select coins into player_coins from players where telegram_id = tid;
	select price into pet_price from animal_list where id = animal; 
	if pet_price > player_coins then 
		return 0;
		
-- top 5 players
	
select p.username , sum(animal_id), max(animal_id) , count(*) over () ttl
from pets right join players p on p.telegram_id = pets.owner 
group by username order by 2  desc nulls last limit 5;


select case when nick_name = 'x' then p.username
      else nick_name end nick ,
      sum(rating) *  (1.0 + count(distinct animal_id)/10::numeric) ,
      --max(al.id) best_animal,
      (select animal_id from pets p2 join animal_list aa on aa.id = p2.animal_id where p2.owner = p.telegram_id order by rating desc limit 1) best_animal,
      array_agg(distinct animal_id order by animal_id desc) ,
        count(*) over () ttl , telegram_id,
        p."exp" 
            from pets RIGHT JOIN players p on p.telegram_id = pets.owner 
            join animal_list al on al.id = pets.animal_id
            where p.last_work > current_date - interval '14 days'
            group by username, nick_name, telegram_id
		order by 2 desc NULLS LAST LIMIT 100;

select case when nick_name = 'x' then p.username
      else nick_name end nick ,
      sum(rating) *  (1.0 + count(distinct animal_id)/10::numeric) ,
      --max(al.id) best_animal,
      (select animal_id from pets p2 join animal_list aa on aa.id = p2.animal_id where p2.owner = p.telegram_id order by rating desc limit 1) best_animal,
      array_agg(distinct animal_id order by animal_id desc) ,
        count(*) over () ttl , telegram_id, p."exp" 
            from pets RIGHT JOIN players p on p.telegram_id = pets.owner 
            join animal_list al on al.id = pets.animal_id
            where p.last_work > current_date - interval '14 days'
            group by username, nick_name, telegram_id
		order by 7 desc NULLS LAST LIMIT 100;

select * from players p --where nick_name = 'kozel'

select animal_id, rating
--(select animal_id from animal_list al2 where rating = (select max(rating) from animal_list al join pets pp on pp.animal_id = al.id where owner = p.telegram_id)) 
--(select max(rating), max(owner)  from animal_list al join pets pp on pp.animal_id = al.id where pp."owner" = pets.owner)
from pets right join players p on p.telegram_id = pets."owner" 
join animal_list al on al.id = pets.animal_id 
where owner = 775803031

select id from animal_list al join pets p2 on p2.animal_id = al.id  where rating = (

select max(rating),
max(p."owner")  from animal_list al join pets p on p.animal_id = al.id where p."owner" = 775803031

)

select array_agg(animal_id order by rating) from pets p2 join animal_list aa on aa.id = p2.animal_id where p2.owner = 775803031 


select "owner", count(distinct animal_id) from pets p group by "owner" 

795547420

select * from property p -- where "owner" = 795547420

update players set coins = coins + 13 where telegram_id = 795547420 775803031 --my



delete from property where owner = 775803031

select * from items i 


-- EPIDEMIC

select * from pets --where animal_id <> 0

select invite_date, username, nick_name, species, pt.id from players p join pets pt on p.telegram_id = pt."owner" 
join animal_list al on al.id = pt.animal_id 
where pt.id % (random() *10 + 1)::int = 0

select (random() *10 + 1)::int

update pets set health = health - 1 where animal_id <> 0 and  id % (random() *10 + 1)::int = 0 returning  *

select * from pets p where "owner" = 775803031

select * from  players --p join pets s on s."owner" = p.telegram_id where p.telegram_id = 823087014


update players set invite_date = null where telegram_id = 775803031

delete  from property 

select * from players p2 order by "exp" desc


select change_health(54,false,1)


create or replace function health_down() returns trigger 
as $$
begin 
	if new.health < 1 then
		new.animal_id =  0 ;
		new.health = 5;
	end if;
	return new;
end;
$$ language plpgsql;

create trigger t_health_down before update of health on pets for each row execute function health_down();


select id, row_number() over() n from pets p where "owner" = 6472394157

select p.id, al.price from pets p join animal_list al on al.id = p.animal_id where "owner" = 6472394157 order by price limit 1;

-- TODO 30.12
create or replace function update_shit(pet_id int8, cleaning bool, value int)
returns int
language plpgsql
as $$
declare
prev_shit int;
player_coins int;
begin
	select shit into prev_shit from pets where id  = pet_id;
	if heal_cost > player_coins then
		return -1;
	end if;
	UPDATE pets SET health = 10 where id = pet_id;
	update players set coins = coins - heal_cost where telegram_id = t_id;
	select animal_id into a_id from pets where id = pet_id;
	return a_id; 
end;
$$;
end

--
create or replace function get_tired(tid int8, value int) 
returns int
language plpgsql
as $$
declare 
stamina_before int;
l_work timestamp;
begin
	select stamina, last_work into stamina_before, l_work from players where telegram_id = tid;
	if stamina_before < value then
		return -1;
	else		
		UPDATE players set stamina = (CASE WHEN stamina - value < 0 THEN 0 ELSE stamina - (value) END) where telegram_id = tid;
	end if;
    return (SELECT stamina FROM players WHERE telegram_id = tid);
end;
$$;
end

select get_tired(775803031,1)

select * from players p 

select * from players p where telegram_id = 775803031

select now() , current_timestamp  at time zone 'MSK',  last_work 
from players p where p.username ~ 'deto'

select * from pg_timezone_abbrevs

create or replace function get_profit(tid int8, percent int) 
returns int
language plpgsql
as $$
declare 
stamina_before int;
l_work timestamp;
profit int;
begin
	select stamina, last_work into stamina_before, l_work from players where telegram_id = tid for update;
	update players set stamina = stamina where telegram_id = tid;
	if l_work > now() - interval '10 minutes' then
		return -1;
	else	
		select coalesce(sum(price) * percent / 100,0) into profit from pets p join animal_list a on a.id = p.animal_id where "owner" = tid;	
		UPDATE players set coins = coins + profit where telegram_id = tid;
	end if;
    return profit;
end;
$$;
end

select change_health(775803031, false, 1)

select get_profit(823087014, 18)

select count(*) from property p where "owner" = 77580303

select * from players --p where telegram_id = 775803031

update players set stamina = 3 where telegram_id = 775803031

select coalesce (null,0)

-- show random infect pets
select p2.first_name, p2.username, p2.nick_name, p.animal_id from pets p join players p2 on p2.telegram_id = p."owner" where p.id % (random() *10 + 1)::int = 0

select (random()*15 +1);

update pets set hunger = 10;

SELECT telegram_id, username FROM players where last_work > current_date - interval '14 days'

select * from animal_list al 

-- 02.02.25 Treasure

create table treasure_field(id int8 generated always as identity, create_date date, location int, field int[][], hint_row int, treasure int, danger int);

truncate table treasure_field;

select * from habitat h ;

select unnest(field) from treasure_field;

select * from treasure_field

update treasure_field set field[1][1] = 1
where id = 1 returning treasure = field[1][1], danger;

delete  from treasure_field where id = 1

insert into treasure_field(create_date, field, location , hint_row, treasure , danger ) values (current_date, '{{1,2},{3,4},{5,6},{7,8},{9,10},{11,12},{13,14},{15,16},{17,18},{19,}', 5, 1, 4, 9 )


create table levels(lvl smallint, exp int);

insert into levels values (2, 100),(3,250),(4,400),(5,600),(6,900),(7,1250);

select * from players p 

	select l.exp from levels l join players p on p.level + 1 = l.lvl where p.telegram_id = 775803031;

create or replace function exp_up(tid int8, value int) 
returns record
language plpgsql
as $$
declare 
next_level_exp int;
new_exp int;
levelup int;
begin
	
	select l.exp into next_level_exp from levels l join players p on p.level + 1 = l.lvl where p.telegram_id = tid;
	
	update players set exp = exp + value where telegram_id = tid
	returning exp into new_exp;
	
	if new_exp >= next_level_exp then
		levelup = 1;
		update players set lvl_points = lvl_points + 1 , level = level + 1 where telegram_id = tid;
	else
		levelup = 0;
	end if;

	 return (select (levelup, next_level_exp)::record) ;
end;
$$;
end

drop exp_up

select * from exp_up(775803031,1) as inf(a int, bb int)

select 1

create table zoo_upgrades(id int primary key, lvl_required int default 2, info text);

select * from zoo_upgrades

alter table zoo_upgrades add column way varchar(15);

alter table zoo_upgrades add column value int;

select * from players p 

insert into zoo_upgrades values(1, 2, 'Лимит силы + 1'),(2,2,'Вместимость зоопарка + 1'),(3,2,'Шанс побега животных -5%'),(4,2,'Шанс поймать животное + 5%'),(5,2,'Взлом хороших замков потребует у вас меньше силы 8 -> 4')




create temp table zup(id int primary key, lvl_required int default 2, info text, way varchar(15), value int);

copy zup from 'C:\Program Files\PostgreSQL\17\abilities.csv' delimiter ';' csv header -- encoding 'WIN1251'

insert into zoo_upgrades (
select n.* from zup n left join zoo_upgrades i on i.id = n.id where i.id is null
)

--29.01.2025 update all columnse from file but id
update zoo_upgrades o set 
lvl_required = a.lvl_required, info = a.info , way = a.way, value = a.value
from (select * from zup ) a  where o.id = a.id;




insert into property(item_id, durability, charged, "owner") values(20,10,false,775803031) returning id

insert into pets(animal_id, owner /*petname*/) values(2,6472394157)

select * from pets

select u.id, lvl_required, info, p."level" = u.lvl_required avail, p.nick_name 
FROM zoo_upgrades u join players p on p."level"+1  >= u.lvl_required and p.telegram_id = 775803031 
where u.id not in (select up_id from player_knows pk where tid = 775803031);




create table player_knows(id int generated always as identity, ldate timestamp, tid int8 references players(telegram_id) not null, up_id int references zoo_upgrades(id) not null)

insert into player_knows(ldate, tid, up_id) values (now(),775803031,1)

select * from player_knows

create table events(name varchar(20), last_executed date, is_active bool);

insert into events values('refill', '2025-02-20', false), ('fire', '2025-02-20', false),  ('epidemic', '2025-02-20', false)