create role pet_master with login createdb;

create database amzoo;

create table players(telegram_id int8 primary key, invite_date date, username text, first_name text, nick_name text, coins smallint default 0);

alter table players add constraint pkey_tid primary key (telegram_id)

select * from players p ;

create table animal_list(
id int8 primary key,
species text,
habitat int references habitat(id),
food_type int references food_type(id), 
price int)

create table tpets(id int references animal_list, species text);

create table pets(
id int8 generated always as identity,
animal_id int8 references animal_list(id),
owner int8 references players(telegram_id),
petname text,  hunger int default 6 check (hunger < 11 and hunger > 0),
health int default 10, 
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

insert into food_type values (1,'omnivore'),(2,'herbivore'),(3,'carnivore')

select * from players p ;
