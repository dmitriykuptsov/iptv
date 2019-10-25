# Copyright (C) 2019 strangebit

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

DROP DATABASE IF EXISTS streamtv;
CREATE DATABASE streamtv
	DEFAULT CHARACTER SET utf8
	DEFAULT COLLATE utf8_bin;

USE streamtv;

CREATE TABLE IF NOT EXISTS streamtv.channels (
	id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	stream_id INT NOT NULL,
	channel_name VARCHAR(100) NOT NULL,
	icon_path VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS streamtv.programs (
	channel_id INT NOT NULL,
	program_name VARCHAR(1000) NOT NULL,
	start_time DATETIME NOT NULL,
	end_time DATETIME NOT NULL,
	scheduled_for_deletion BOOLEAN DEFAULT FALSE,
	scheduled_for_insertion BOOLEAN DEFAULT TRUE,
	FOREIGN KEY (channel_id)
		REFERENCES streamtv.channels(id)
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS streamtv.users (
	id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	username VARCHAR(100) NOT NULL,
	password VARCHAR(64) NOT NULL,
	email VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS streamtv.accounting (
	id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	user_id INT NOT NULL,
	start_period DATETIME NOT NULL,
	end_period DATETIME NOT NULL,
	FOREIGN KEY (user_id)
		REFERENCES users(id)
		ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS streamtv.channel_icons (
	id INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
	channel_id INT NOT NULL,
	icon_name VARCHAR(20) NOT NULL,
	FOREIGN KEY (channel_id)
		REFERENCES streamtv.channels(id)
		ON DELETE CASCADE
);

INSERT INTO streamtv.users(username, password, email) VALUES('admin', SHA2(CONCAT('deftipZerId7', 'gligoofDapt6'), 256), 'dmitriy.kuptsov@gmail.com');

INSERT INTO streamtv.channels(stream_id, channel_name, icon_path) VALUES(2001, 'Первый канал', '/images/perviy.png');
INSERT INTO streamtv.channels(stream_id, channel_name, icon_path) VALUES(2002, 'Россия 1', '/images/rossiya1.png');
INSERT INTO streamtv.channels(stream_id, channel_name, icon_path) VALUES(2003, 'Россия 24', '/images/rossiya24.png');
INSERT INTO streamtv.channels(stream_id, channel_name, icon_path) VALUES(2005, 'НТВ', '/images/ntv.png');
#INSERT INTO streamtv.channels(stream_id, channel_name, icon_path) VALUES(2006, 'EuroNews', '/images/euronews.png');
#INSERT INTO streamtv.channels(stream_id, channel_name, icon_path) VALUES(2014, 'Детский мир', '/images/detskiy.png');
#INSERT INTO streamtv.channels(stream_id, channel_name, icon_path) VALUES(2016, 'Карусель', '/images/karusel.png');
#INSERT INTO streamtv.channels(stream_id, channel_name, icon_path) VALUES(2015, 'Disney Channel', '/images/disney.png');
