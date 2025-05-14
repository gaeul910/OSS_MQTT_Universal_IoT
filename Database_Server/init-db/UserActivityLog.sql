﻿CREATE TABLE `eventlog` (
	`id`	INT(11)	NOT NULL,
	`locationid`	INT(11)	NOT NULL,
	`time`	DATETIME	NULL,
	`eventid`	INT(11)	NULL
);

CREATE TABLE `userfavroute` (
	`id`	INT(11)	NOT NULL,
	`startlocation_id`	INT(11)	NOT NULL,
	`endlocation_id`	INT(11)	NOT NULL,
	`route`	LINESTRING	NULL,
	`status`	INT(11)	NULL
);

CREATE TABLE `users` (
	`uid`	INT(11)	NOT NULL,
	`id2`	INT(11)	NOT NULL,
	`permission`	INT(11)	NULL
);

CREATE TABLE `userfavlocation` (
	`id`	INT(11)	NOT NULL,
	`uid`	INT(11)	NOT NULL,
	`alias`	TEXT	NULL,
	`coordinate`	POINT	NULL,
	`status`	INT(11)	NULL
);

CREATE TABLE `locationlog` (
	`id`	INT(11)	NOT NULL,
	`uid`	INT(11)	NOT NULL,
	`coordinate`	POINT	NULL,
	`time`	DATETIME	NULL
);

CREATE TABLE `usernotifications` (
	`id`	INT(11)	NOT NULL,
	`uid`	INT(11)	NOT NULL,
	`content`	TEXT	NULL,
	`time`	DATETIME	NULL,
	`stat`	BOOLEAN	NULL,
	`about`	INT(11)	NULL
);

CREATE TABLE `clients` (
	`id`	INT(11) NOT NULL	NOT NULL,
	`token`	VARCHAR(256)	NULL,
	`type`	INT(11)	NULL,
	`perms`	VARCHAR(255)	NULL,
	`valid`	DATETIME	NULL
);

ALTER TABLE `eventlog` ADD CONSTRAINT `PK_EVENTLOG` PRIMARY KEY (
	`id`,
	`locationid`
);

ALTER TABLE `userfavroute` ADD CONSTRAINT `PK_USERFAVROUTE` PRIMARY KEY (
	`id`
);

ALTER TABLE `users` ADD CONSTRAINT `PK_USERS` PRIMARY KEY (
	`uid`
);

ALTER TABLE `userfavlocation` ADD CONSTRAINT `PK_USERFAVLOCATION` PRIMARY KEY (
	`id`
);

ALTER TABLE `locationlog` ADD CONSTRAINT `PK_LOCATIONLOG` PRIMARY KEY (
	`id`
);

ALTER TABLE `usernotifications` ADD CONSTRAINT `PK_USERNOTIFICATIONS` PRIMARY KEY (
	`id`
);

ALTER TABLE `clients` ADD CONSTRAINT `PK_CLIENTS` PRIMARY KEY (
	`id`
);

ALTER TABLE `eventlog` ADD CONSTRAINT `FK_userfavlocation_TO_eventlog_1` FOREIGN KEY (
	`locationid`
)
REFERENCES `userfavlocation` (
	`id`
);

