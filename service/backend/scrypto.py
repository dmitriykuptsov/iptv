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
from hashlib import sha256
from base64 import b64decode
from base64 import b64encode
from Crypto import Random
from Crypto.Cipher import AES
from os import urandom
from base64 import b64encode

# 256 bit key
KEY_SIZE = AES.block_size * 2
BLOCK_SIZE = AES.block_size
IV_SIZE = BLOCK_SIZE

# PKCS7 padding as described in
# https://tools.ietf.org/html/rfc5652
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
                chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

class AESCipher:
	def __init__(self, key):
		self.key = key;

	def encrypt(self, plaintext):
		padded_plaintext = pad(plaintext);
		iv = Random.new().read(BLOCK_SIZE);
		cipher = AES.new(self.key, AES.MODE_CBC, iv);
		return b64encode(iv + cipher.encrypt(padded_plaintext));

	def decrypt(self, ciphertext):
		ciphertext = b64decode(ciphertext);
		iv = ciphertext[:IV_SIZE];
		cipher = AES.new(self.key, AES.MODE_CBC, iv);
		return unpad(cipher.decrypt(ciphertext[IV_SIZE:])).decode('utf8');
