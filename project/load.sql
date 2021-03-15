drop database if exists user;
create database user;
use user;

create table users (
	username varchar(300) not null primary key,
    is_member char(1) not null, # Y for Yes, # N for No
    membership_date date,
    current_points int,
    total_points int,
    boxes_open int
);

# ADDING SAMPLE user data
INSERT into users VALUES ('Sarah Baumert', 'N', null, 235, 500, 2);
INSERT into users VALUES ('Michelle', 'N', null, 5555, 5555, 5);
INSERT into users VALUES ('Meghan', 'N', null, 234, 556, 1);
INSERT into users VALUES ('Christine', 'N', null, 22, 55, 0);
INSERT into users VALUES ('Mieka', 'N', null, 3, 3, 0);
INSERT into users VALUES ('Lunatone', 'N', null, 112, 112, 5);
INSERT into users VALUES ('Torrence', 'N', null, 2414, 5323, 12);
INSERT into users VALUES ('Monique', 'N', null, 44, 52, 3);
INSERT into users VALUES ('Yuri', 'N', null, 1253, 1530, 8);
INSERT into users VALUES ('Alison', 'N', null, 502, 502, 4);
INSERT into users VALUES ('Chrissa','N', null, 0, 2, 0);

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

drop database if exists ActivityLog;
create database ActivityLog;
use ActivityLog;

CREATE TABLE activitylog (
  activityID int not null auto_increment primary key,
  activityType varchar(300) NOT NULL,
  activityDatetime datetime NOT NULL,
  userID_Involved int,
  boxID_Involved int,
  incentivePurchased varchar(300),
  currencyGained int,
  currencyUsed int,
  errorID int
);

drop database if exists ErrorLog;
create database ErrorLog;
use ErrorLog;

CREATE TABLE if not exists errorlog (
  errorID int not null auto_increment primary key,
  errorType varchar(300) NOT NULL,
  errorDescription varchar(300) NOT NULL,
  errorDatetime datetime NOT NULL,
  userID_Involved int NOT NULL
);