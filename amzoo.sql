create role pet_master with login createdb;

create database amzoo;

grant pg_read_server_files to pet_master;

create table players(telegram_id int8 primary key, invite_date date, username text, first_name text, nick_name text,
coins smallint default 0, level int default 1,
game_location int default 5 references habitat(id),
stamina int default 5 check (stamina > -1 and stamina < 11)
);

alter table players add column level int default 1;

alter table players add column stamina int default 5 check (stamina > -1 and stamina < 11)

alter table players drop column stamina;

alter table players drop column levle;

alter table players add column last_work timestamp default now();

alter table players add constraint pkey_tid primary key (telegram_id)

drop  table players cascade;

select * from players p ;

select buy_pet(775803031,1)


create table animal_list(
id int8 primary key,
species text,
habitat int references habitat(id),
food_type int references food_type(id), 
price int)

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




copy animal_list(id,species,habitat,food_type,price) from 'C:\Python\Python310\Scripts\amzzoo\animals.csv' delimiter ';' csv header encoding 'WIN1251'

create table moods(id int primary key, value text);

insert into moods values(1, 'ill'),(2,'sad'),(3,'ok'),(4,'scary'),(5,'happy'),(6,'love'),(7,'cold'),(8,'hot'),(9,'sleep'),(10,'angry'),(0,'dead'),(100,'ghost');

create table habitat(id int primary key, value text)

insert into habitat values(1,'desert'),(2,'field'),(3,'forest'),(4,'water'),(5,'any')

create table food_type(id int primary key , name text)

insert into food_type values (0,'nothing'),(1,'omnivore'),(2,'herbivore'),(3,'carnivore')

truncate food_type cascade;

select * from players p ;

create or replace function buy_pet(tid int8, animal int8)
returns int 
language plpgsql
as $$
declare pet_price int;
begin
	select price into pet_price from animal_list where id = animal; 
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

select sell_pet(8) 

select  buy_pet(775803031,4)

update players set coins  = coins + 1 where telegram_id = 775803031

-- last work reset
create or replace function work_reset() returns trigger 
as $$
begin 
	new.last_work =  now() ;
	return new;
end;
$$ language plpgsql;

create trigger t_work_res before update of stamina on players for each row execute function work_reset();

drop trigger t_work_res on  players; 

select * from players p 

insert into players(telegram_id) values(1)

-- change hunger level

create or replace function change_hunger(pet_id int8, feeding boolean, value int) 
returns int
language plpgsql
as $$
declare 
hung_before int;
health_before int;
begin
	if feeding then
		update pets set hunger = hunger + value where id = pet_id;
	else
		select hunger into hung_before from pets where id = pet_id;
		if hung_before = 0 then
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

select change_hunger(2, false , 1)

select change_hunger(id, false , 1) from pets p where health > 0;

select * from pets;

create temp table t(b boolean)

insert into t values('True')



update pets set hunger = hunger - 1 where hunger > 0;
