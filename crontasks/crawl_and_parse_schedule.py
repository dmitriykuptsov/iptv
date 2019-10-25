# -*- coding: utf-8 -*-
#!/usr/bin/python

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

# General libraries
import os
import sys
import re
import datetime

# HTTP stuff
import urllib2

# String input/output
from io import StringIO, BytesIO

# Parse the input parameters.

db_host     = sys.argv[1];
db_user     = sys.argv[2];
db_password = sys.argv[3];
db          = sys.argv[4];

# XML stuff
import lxml
from lxml import etree
from lxml import sax

# SAX handler
from xml.sax.handler import ContentHandler

# Mysql stuff
import MySQLdb

connection = MySQLdb.connect(host=db_host, user=db_user, passwd=db_password, db=db, charset="utf8");

def parse_time(s):
	year   = int(s[0:4]);
	month  = int(s[4:6]);
	day    = int(s[6:8]);
	hour   = int(s[8:10]);
	minute = int(s[10:12]);
	second = int(s[12:14]);
	return datetime.datetime(year, month, day, hour, minute, second) - datetime.timedelta(hours=5);

class Program():
	def __init__(self, channel_name, program_name, start, end):
		self.channel_name = channel_name;
		self.program_name = program_name;
		self.start   = start;
		self.end     = end;

	def save(self, connection, cursor):
		sql = "INSERT INTO programs(channel_id, program_name, start_time, end_time) VALUES((SELECT id FROM channels WHERE channel_name LIKE %s), %s, %s, %s)";
		cursor.execute(sql, [self.channel_name, self.program_name, self.start, self.end]);
		connection.commit();

class Channel():
	def __init__(self, name):
		self.name = name;

	def save(self, connection, cursor):
		#sql = "INSERT INTO channels(channel_name) VALUES(%s)";
		#cursor.execute(sql, [self.name]);
		#connection.commit();
		pass

class MyContentHandler(ContentHandler):
	def __init__(self):
		self.in_prog    = False;
		self.in_title   = False;
		self.in_chan    = False;
		self.channel    = None;
		self.start_time = None;
		self.end_time   = None;
		self.program    = None;
		self.channel_id = None;
		self.programs   = {}
		self.channels   = [];
		self.channel_id_name_mapping = {}
		self.valid_channels = {
			"1": u"Первый канал",
			"2": u"Россия 1",
			"676": u"Россия 24",
			"4": u"НТВ"#,
			#"208": u"EuroNews",
			#"216": u"Детский мир",
			#"1464": u"Карусель",
			#"100055": u"Disney Channel"
		}

	def startElementNS(self, name, qname, attributes):
		if name[1] == "programme":
			self.channel_id = attributes.getValueByQName("channel");
			self.start_time = attributes.getValueByQName("start");
			self.end_time = attributes.getValueByQName("stop");
			self.in_prog = True;
		if name[1] == "title" and self.in_prog:
			self.in_title = True;


	def endElementNS(self, name, qname):
		if name[1] == "display-name":
			self.in_chan = False;
		if name[1] == "programme":
			self.in_prog = False;
		if name[1] == "title" and self.in_prog:
			self.in_title = False;

	def characters(self, data):
		#if self.in_chan:
		#	self.channel_name = data;
		#	self.channel_id_name_mapping[self.channel_id] = self.channel_name
		#	self.channels.append(Channel(self.channel_name));
		#	return;
		if self.in_title:
			self.program_name = data;
			#
			if self.channel_id not in self.programs.keys():
				self.programs[self.channel_id] = [];
			if self.channel_id in self.valid_channels.keys():
				self.channel_name = self.valid_channels[self.channel_id];
				program = Program(self.channel_name.strip(), self.program_name, parse_time(self.start_time), parse_time(self.end_time));
				self.programs[self.channel_id].append(program);

	def getChannels(self):
		return self.channels;

	def getPrograms(self):
		return self.programs;

# This code takes extremely long time to execute
# Needs to be revised anyway
# One idea is to mark with a special bit channels and programs,
# as an indication that they will be deleted in the future.
f = urllib2.urlopen("https://tvcom.uz/files/xmltv.xml");
tree = etree.parse(f);
f.close();
h = MyContentHandler();
sax.saxify(tree, h);
cursor = connection.cursor(MySQLdb.cursors.DictCursor);
# Lock the tables so that no inconsistencies will occur
# When querying for channels and programs one should perform the following query:
# SELECT * FROM channels WHERE scheduled_for_insertion = FALSE;
# SELECT * FROM program WHERE scheduled_for_insertion = FALSE;
#cursor.execute("LOCK tables channels WRITE, programs WRITE;");
cursor.execute("LOCK tables programs WRITE;");
# Delete tombstones if any...
#cursor.execute("DELETE FROM channels WHERE scheduled_for_insertion = TRUE");
cursor.execute("DELETE FROM programs WHERE scheduled_for_insertion = TRUE");
# Move old ones...
#cursor.execute("UPDATE channels SET scheduled_for_deletion = TRUE");
cursor.execute("UPDATE programs SET scheduled_for_deletion = TRUE");
cursor.execute("UNLOCK tables;");
connection.commit();
#for channel in h.getChannels():
#	channel.save(connection, cursor);
programs = h.getPrograms();
for channel in programs.keys():
	for program in programs[channel]:
		program.save(connection, cursor);
connection.commit();
# This should be much faster...
#cursor.execute("LOCK tables channels WRITE, programs WRITE;");
cursor.execute("LOCK tables programs WRITE;");
#cursor.execute("DELETE FROM channels WHERE scheduled_for_deletion = TRUE;");
cursor.execute("DELETE FROM programs WHERE scheduled_for_deletion = TRUE;");
#cursor.execute("UPDATE channels SET scheduled_for_insertion = FALSE;");
cursor.execute("UPDATE programs SET scheduled_for_insertion = FALSE;");
cursor.execute("UNLOCK tables;");
connection.close();
