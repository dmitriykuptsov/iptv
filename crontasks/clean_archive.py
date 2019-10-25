#!/bin/bash
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
import os
import sys
import re
import time
import shutil

base_path = sys.argv[1];
max_interval = int(sys.argv[2]);
folders = None;
try:
	folders = os.listdir(base_path);
except:
	exit(-1);
for folder in folders:
	current_time = int(time.time());
	if re.match(r"[0-9]{10}", folder):
		print "Checking whether we should delete the folder or not %s" % (folder);
		folder_timestamp = int(folder);
		if (current_time - folder_timestamp) > max_interval:
			print "Deleting the folder %s with old content... " % (folder);
			shutil.rmtree("".join([base_path, "/", folder]))
	else:
		print "Skipping folder %s" % (folder)
