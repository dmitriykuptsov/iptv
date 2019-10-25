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
import binascii

# The key size is a 16 octet binary string as described in 
# https://tools.ietf.org/html/draft-pantos-http-live-streaming-08#section-5
KEY_SIZE = AES.block_size
BLOCK_SIZE = AES.block_size
IV_SIZE = BLOCK_SIZE

# PKCS7 padding as described in
# https://tools.ietf.org/html/rfc5652
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
                chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

class HLSCipher:

	# Encrypts the segment
	@staticmethod
	def encrypt(plaintext, key, iv):
		padded_plaintext = pad(plaintext);
		cipher = AES.new(key, AES.MODE_CBC, iv);
		return cipher.encrypt(padded_plaintext);

	# Decrypts the segment
	@staticmethod
	def decrypt(ciphertext, key, iv):
		cipher = AES.new(key, AES.MODE_CBC, iv);
		return unpad(cipher.decrypt(ciphertext));

	# The key is nothing else but a binary string of length 16 octets
	@staticmethod
	def encodeKey(key):
		return key;

	@staticmethod
	def generateKey():
		return Random.new().read(KEY_SIZE);

	@staticmethod
	def generateIV():
		return Random.new().read(IV_SIZE);

	# Encodes the key as a 16 octet hexidecimal string prefixed with 0x
	@staticmethod
	def encodeIV(iv):
		return ("0x%s" % (binascii.hexlify(iv)));