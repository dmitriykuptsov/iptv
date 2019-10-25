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
import json
import time
from config import config
from scrypto import AESCipher

cipher = AESCipher(config["MASTER_SECRET"]);
nonce = config["SERVER_NONCE"];

class Token:
	@staticmethod
	def is_valid(token):
		try:
			if not token:
				return False
			if token["server_nonce"] != nonce:
				return False
			now = int(time.mktime(time.gmtime()))
			return now <= token["valid_until"];
		except:
			return False

	@staticmethod
	def get_token_hash(token):
		if Token.is_valid():
			return token["token"];
		else:
			return None

	@staticmethod
	def get_user_id(token):
		if not token:
			return None
		if Token.is_valid(token):
			return token["user_id"];
		return None

	@staticmethod
	def decode(token):
		try:
			token = cipher.decrypt(token);
			return json.loads(token);
		except:
			return None

	@staticmethod
	def encode(user_id, hased_token, server_nonce, expires_in):
		now = int(time.mktime(time.gmtime()))
		valid_until = now + expires_in;
		token = json.dumps({
			"token": hased_token,
			"valid_until": valid_until,
			"user_id": user_id,
			"server_nonce": server_nonce
			});
		return cipher.encrypt(token);