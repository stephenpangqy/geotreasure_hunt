drop database if exists user;
create database user;
use user;

create table users (
  id int AUTO_INCREMENT primary key,
	username varchar(300) not null,
  password varchar(80) not null,
  is_member char(1) not null, # Y for Yes, # N forNo
  membership_date date,
  current_points int,
  total_points int,
  boxes_open int,

  UNIQUE(username)
);

# ADDING SAMPLE user data
INSERT into users (username,password,is_member,membership_date,current_points,total_points,boxes_open) VALUES ('Sarah Baumert','5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8', 'N', null, 235, 500, 2);
INSERT into users (username,password,is_member,membership_date,current_points,total_points,boxes_open)VALUES ('Michelle','5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8', 'N', null, 5555, 5555, 5);
INSERT into users (username,password,is_member,membership_date,current_points,total_points,boxes_open)VALUES ('Meghan','5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8', 'N', null, 234, 556, 1);
INSERT into users (username,password,is_member,membership_date,current_points,total_points,boxes_open)VALUES ('Christine','5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8', 'N', null, 22, 55, 0);
INSERT into users (username,password,is_member,membership_date,current_points,total_points,boxes_open)VALUES ('Mieka','5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8', 'N', null, 3, 3, 0);
INSERT into users (username,password,is_member,membership_date,current_points,total_points,boxes_open)VALUES ('Lunatone','5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8', 'N', null, 112, 112, 5);
INSERT into users (username,password,is_member,membership_date,current_points,total_points,boxes_open)VALUES ('Torrence','5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8', 'N', null, 2414, 5323, 12);
INSERT into users (username,password,is_member,membership_date,current_points,total_points,boxes_open)VALUES ('Monique','5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8', 'N', null, 44, 52, 3);
INSERT into users (username,password,is_member,membership_date,current_points,total_points,boxes_open)VALUES ('Yuri','5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8', 'N', null, 1253, 1530, 8);
INSERT into users (username,password,is_member,membership_date,current_points,total_points,boxes_open)VALUES ('Alison','5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8', 'N', null, 502, 502, 4);
INSERT into users (username,password,is_member,membership_date,current_points,total_points,boxes_open)VALUES ('Chrissa','5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8','N', null, 0, 2, 0);

create table user_inventory (
	  username varchar(300) not null,
    itemname varchar(100) not null,
    quantity int not null,
    
    constraint primary key (username,itemname)
);

drop database if exists ingame_shop;
create database ingame_shop;
use ingame_shop;

create table in_game_shop_items (
    itemname varchar(100) not null primary key,
    itemprice int not null,
    itemdesc varchar(300) not null
);

# ADDING SAMPLE SHOP ITEM DATA
INSERT INTO in_game_shop_items VALUES ('$20 Gongcha Voucher', 250, 'Redeem this to get a $20 Gongcha Voucher.');
INSERT INTO in_game_shop_items VALUES ('Straw', 3, 'A simple straw.');
INSERT INTO in_game_shop_items VALUES ('$10 GrabVoucher', 100, 'Redeem this to get a $10 Voucher that you can use on Grab.');


drop database if exists box;
create database box;
use box;

create table box (
	boxid int not null auto_increment primary key,
    box_contents varchar(400), # each item separated by comma, can be empty
    no_of_points int not null,
    box_latitude varchar(100) not null,
    box_longitude varchar(100) not null,
    planted_by_username varchar(300) not null,
    is_opened char(1) # Y for Opened, N for not opened
);

# SAMPLE BOX DATA
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES ('$30 GrabVoucher',54,1.2345,1.5345,'Michelle','N');
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES (null,203,1.4567,1.8924,'Michelle','N');
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES ('1-for-1 GongCha Voucher',100,0.9343,0.82354,'Michelle','N');
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES (null,123,1.456,1.4555,'Meghan','N');
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES ('1-for-1 GongCha Voucher',100,1.29838869,103.856419,'Michelle','N');

drop database if exists ActivityLog;
create database ActivityLog;
use ActivityLog;

CREATE TABLE activitylog (
  activityID int not null auto_increment primary key,
  activityType varchar(300) NOT NULL,
  activityDatetime datetime NOT NULL,
  activityDesc varchar(400),
  user_Involved varchar(300),
  ItemsReceived varchar(400),
  currencyGained int,
  currencyUsed int
);

drop database if exists ErrorLog;
create database ErrorLog;
use ErrorLog;

CREATE TABLE if not exists errorlog (
  errorID int not null auto_increment primary key,
  user_Involved varchar(300) NOT NULL,
  errorType varchar(300) NOT NULL,
  errorDescription varchar(400) NOT NULL,
  errorDatetime datetime NOT NULL
);