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
config = {
	"DEMUX": "/dev/dvb/adapter0/demux0",
	"FRONTEND": "/dev/dvb/adapter0/frontend0",
	"DVR": "/dev/dvb/adapter0/dvr0",
	"SEQUENCE_LENGTH_IN_BYTES": (4*1024*1024 + 164), #Slightly larger than 2MB, we need a multiple of 188 
	"TS_OUTPUT_FOLDER": "/var/streaming/",
	"EXEC_DIR": "/opt/iptv/capturing/",
	"EXTRACT_DURATION_SCRIPT": "compute_duration.sh",
	"CONVERT_RAW_TS": "convert_ts.sh",
	"NUMBER_OF_SEQUENCIES_PER_FOLDER": 2,
	"CENTER_FREQUENCY_HZ": 410000000,
	"MODULATION": 0x6,
	"INVERSION": 0x2,
	"SYMBOL_RATE": 6900000,
	"FEC": 0x9,
	"BANDWIDTH": 0x0,
	"WEB_PATH": "/streaming/segments/",
	"M3U8_VERSION": 0x3,
	"ENABLE_STREAM_ENCRYPTION": True,
	"CRON": {
		"CRONTASKS_FOLDER": "/opt/iptv/crontasks/",
		"POLL_INTERVAL": 10,
		# This is rather silly to run cron tasks periodically
		# For example TV schedule parser should be executed one at midnight or so...
		# For now lets leave this code as it is
		"TASKS": [
			{
				"NAME": "CLEAN_ARCHIVE",
				"SCRIPT": "/opt/iptv/crontasks/clean_archive.py",
				"PARAMS": "/var/streaming/2001/ 600",
				"INTERVAL_IN_SECONDS": 60
			},
			{
				"NAME": "CLEAN_ARCHIVE",
				"SCRIPT": "/opt/iptv/crontasks/clean_archive.py",
				"PARAMS": "/var/streaming/2002/ 600",
				"INTERVAL_IN_SECONDS": 60
			},
			{
				"NAME": "CLEAN_ARCHIVE",
				"SCRIPT": "/opt/iptv/crontasks/clean_archive.py",
				"PARAMS": "/var/streaming/2003/ 600",
				"INTERVAL_IN_SECONDS": 60
			},
			{
				"NAME": "CLEAN_ARCHIVE",
				"SCRIPT": "/opt/iptv/crontasks/clean_archive.py",
				"PARAMS": "/var/streaming/2005/ 600",
				"INTERVAL_IN_SECONDS": 60
			}#,
			#{
			#	"NAME": "CLEAN_ARCHIVE",
			#	"SCRIPT": "/home/pi/iptv/crontasks/clean_archive.py",
			#	"PARAMS": "/var/streaming/2006/ 600",
			#	"INTERVAL_IN_SECONDS": 60
			#}#,
			#{
			#	"NAME": "CLEAN_ARCHIVE",
			#	"SCRIPT": "/home/pi/iptv/crontasks/clean_archive.py",
			#	"PARAMS": "/var/streaming/2014/ 600",
			#	"INTERVAL_IN_SECONDS": 60
			#},
			#{
			#	"NAME": "CLEAN_ARCHIVE",
			#	"SCRIPT": "/home/pi/iptv/crontasks/clean_archive.py",
			#	"PARAMS": "/var/streaming/2016/ 600",
			#	"INTERVAL_IN_SECONDS": 60
			#},
			#{
			#	"NAME": "CLEAN_ARCHIVE",
			#	"SCRIPT": "/home/pi/iptv/crontasks/clean_archive.py",
			#	"PARAMS": "/var/streaming/2015/ 600",
			#	"INTERVAL_IN_SECONDS": 60
			#}#,
			# This task should be called somewhere else...
			#{
			#	"NAME": "PARSE_TV_SCHEDULE",
			#	"SCRIPT": "/home/pi/iptv/crontasks/crawl_and_parse_schedule.py",
			#	"PARAMS": "localhost root root streamtv",
			#	"INTERVAL_IN_SECONDS": 3600
			#}
		]
	}, "VALID_CHANNELS": {
		2001: u"Первый канал",
		2002: u"Россия 1",
		2003: u"Россия 24",
		2005: u"НТВ"#,
		#2006: u"EuroNews"#,
		#2014: u"Детский мир",
		#2016: u"Карусель",
		#2015: u"Disney Channel"
	}
}
