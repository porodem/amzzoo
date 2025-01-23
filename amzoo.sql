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

drop  table players cascade;


select * from players p ;

delete from players where telegram_id = 775803031

select buy_pet(775803031,1)


create table animal_list(
id int8 primary key,
species text,
habitat int references habitat(id),
food_type int references food_type(id), 
price int)

alter table animal_list add column catch_price int;

alter table animal_list add column catch_difficulty int; -- how much stamina you loss on try

alter table animal_list add column catch_chance int; -- percents % 17 for dice and other 1-6 games

select * from animal_list al ;

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

drop table pets;

select * from pets;

insert into pets(animal_id, owner /*petname*/) values(2,775803031)

select * from pets;

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
catch_chance int
)

copy animal_list(id,species,habitat,food_type,price,catch_price,catch_difficulty,catch_chance) from 'C:\Python\Python310\Scripts\amzzoo\a.csv' delimiter ';' csv header encoding 'WIN1251'

create temp table anlist(id int, name text)

copy anlist from 'C:\Python\Python310\Scripts\amzzoo\animals.csv' delimiter ';' csv header -- encoding 'WIN1251'

insert into animal_list (
select n.* from anlist n left join animal_list i on i.id = n.id where i.id is null
)

drop table  anlist 

select * from players p 

select * from pets p 

select * from animal_list al where catch_price > 0 ;

update animal_list o set
price = a.price, catch_price = a.catch_price, catch_difficulty = a.catch_difficulty , catch_chance = a.catch_chance
from (select * from anlist ) a  where o.id = a.id;

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

update habitat set travel_price = 12 where id = 3;

select id, species, price from animal_list al where habitat = 5

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


-- db_get_owned_items_group

select  i.id, sum(price) ttl_price, count(*) as quantity from  property p join items i on i.id = p.item_id where owner = 775803031 group by 1 --where owner = %s	
	


copy items from 'C:\Python\Python310\Scripts\amzzoo\items.csv' delimiter ';' csv header -- encoding 'WIN1251'

copy animal_list(id,species,habitat,food_type,price) from 'C:\Python\Python310\Scripts\amzzoo\a.csv' delimiter ';' csv header encoding 'WIN1251'

create temp table new_items4(id int, name text, price int, location int, description text )

copy new_items4 from 'C:\Python\Python310\Scripts\amzzoo\items.csv' delimiter ';' csv header -- encoding 'WIN1251'

insert into items select * from new_items n where (select id from items  ) <> n.id

insert into items (
select n.* from new_items3 n left join items i on i.id = n.id where i.id is null
)

update items i set price = n.price, "location" = n.location, description = n.description from new_items4 n where n.id = i.id 

insert into items values(10,'Пасспорт',5,5)

select * from players p ;

UPDATE players set stamina = (case when stamina - 1 < 0 then 0 else stamina-1 end)  where telegram_id = 1969292042
returning stamina 



select * from habitat h ;

truncate items cascade;




select p.id, i."name", price, location from  property p join items i on i.id = p.item_id ;

select * from property p 

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

select buy_item(775803031, 1)

select username, p2.* from players p join property p2  on p2."owner" = p.telegram_id ;

delete from property p where id = (select id from property p where item_id = 5 limit 1);

select id from property p where item_id = 5

select * from players p ;

UPDATE players set pet_space = pet_space + 1 where telegram_id =775803031

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

select  buy_pet(775803031,4)

select * from pets p ;

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

-- last work reset v2 (have side effect - player after more than one hour rest begin receive stamina up inlimited, every time after check_relax executed on info message)
create or replace function work_reset() returns trigger 
as $$
begin 
	if new.stamina < old.stamina then
		new.last_work =  now() ;
	end if;
	return new;
end;
$$ language plpgsql;

create trigger t_work_res before update of stamina on players for each row execute function work_reset();

drop trigger t_work_res on  players; 

select * from players p 

insert into players(telegram_id) values(3)

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

select * from pets;

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

select * from players p --where nick_name = 'kozel'

select "owner", count(distinct animal_id) from pets p group by "owner" 


-- EPIDEMIC

select * from pets --where animal_id <> 0

select invite_date, username, nick_name, species, pt.id from players p join pets pt on p.telegram_id = pt."owner" 
join animal_list al on al.id = pt.animal_id 
where pt.id % (random() *10 + 1)::int = 0

select (random() *10 + 1)::int

update pets set health = health - 1 where animal_id <> 0 and  id % (random() *10 + 1)::int = 0 returning  *



create or replace function change_health(pet_id int8, healing boolean, value int) 
returns int
language plpgsql
as $$
declare 
health_before int;
begin
	select health into health_before from pets where id = pet_id;
	if healing then
		if health_before + value > 10 then
			update pets set health = 10 where id = pet_id;
		else
			update pets set health = health + value where id = pet_id;
		end if;
	else			
--		if health_before - value < 1 then
--			update pets set animal_id = 0, mood = '3' where id = pet_id;
--		else
		update pets set health = health - value where id = pet_id;
--		end if;
	end if;
    return 1;
end;
$$;
end

select * from pets

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


create table feedbacks(
	id int primary key generated always as identity, 
	msg text,
	type int, -- 0 negative 1 posttive 2 question
	rdate timestamp,
	tid int8
)

select username, tid, rdate, msg from feedbacks f join players p on p.telegram_id  = f.tid ;