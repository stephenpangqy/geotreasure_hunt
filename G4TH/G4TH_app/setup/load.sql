drop database if exists user;
create database user;
use user;

create table users (
  id int AUTO_INCREMENT primary key,
	username varchar(300) not null,
  is_member char(1) not null, # Y for Yes, # N forNo
  membership_date date,
  current_points int,
  total_points int,
  boxes_open int,
  last_login date,
  daily_boxes int,

  UNIQUE(username)
);

# ADDING SAMPLE user data
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Sarah Baumert', 'Y', '2021-04-11', 235, 500, 2, null, 5);
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Michelle', 'N', null, 5555, 5555, 5, null, 3);
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Meghan', 'N', null, 234, 556, 1, null, 3);
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Christine', 'N', null, 22, 55, 0, null, 3);
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Mieka', 'N', null, 3, 3, 0, null, 3);
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Lunatone', 'N', null, 112, 112, 5, null, 3);
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Torrence', 'N', null, 2414, 5323, 12, null, 3);
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Monique', 'N', null, 44, 52, 3, null, 3);
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Yuri', 'N', null, 1253, 1530, 8, null, 3);
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Alison', 'N', null, 502, 502, 4, null, 3);
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Chrissa', 'N', null, 0, 2, 0, null, 3);
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Meese', 'N', null, 500, 500, 1, null, 3);
INSERT into users (username,is_member,membership_date,current_points,total_points,boxes_open,last_login,daily_boxes)VALUES ('Gina Poskitt', 'Y', '2021-03-21', 4352, 4400, 15, null, 3);


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
INSERT INTO in_game_shop_items VALUES ('$20 Gongcha Voucher', 550, 'Redeem this to get a $20 Gongcha Voucher.');
INSERT INTO in_game_shop_items VALUES ('$5 Capitaland Voucher', 220, 'Redeem this to get a $5 Capitaland Voucher.');
INSERT INTO in_game_shop_items VALUES ('$3 Li-Ho Voucher', 130, 'Redeem to get a $3 Li_Ho Voucher.');
INSERT INTO in_game_shop_items VALUES ('$1 Popular Voucher', 80, 'Redeem to get a $1 Popular Voucher.');
INSERT INTO in_game_shop_items VALUES ('$10 GrabVoucher', 350, 'Redeem this to get a $10 Voucher that you can use on Grab.');


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
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES ('$30 GrabVoucher',54,1.2949,103.6305,'Michelle','N');
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES (null,203,1.3525,103.9447,'Michelle','N');
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES ('$3 Li-Ho Voucher',100,1.3868,103.8914,'Mieka','N');
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES (null,123,1.2939,103.8533,'Meghan','N');
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES ('$10 GrabVoucher',100,1.29838869,103.856419,'Michelle','N');
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES (null,25,1.4214,103.7475,'Lunatone','N');
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES ('$10 GrabVoucher',43,1.4305,103.7173,'Meese','N');
INSERT INTO box (box_contents,no_of_points,box_latitude,box_longitude,planted_by_username,is_opened) VALUES (null,90,1.3008,103.9122,'Torrence','N');

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