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
from flask import Flask
from flask import request, jsonify
from flask import json,Response,send_file
from flask import g
from logging.config import dictConfig
import decimal
import MySQLdb
import hashlib
import random
import datetime
import os
import re
from flask import Response
from math import sqrt
from math import pow
import sys
import json
from math import log
import base64
import atexit
import traceback
from config import config
from tokens import Token
from utils import Utils

app = Flask(__name__);

random.seed(os.urandom(64));

def connect_to_database():
	return MySQLdb.connect(host=config["DB_HOST"],
		user=config["DB_USER"],
		passwd=config["DB_PASSWORD"],
		db=config["DB"],
		charset="utf8");

@app.before_request
def db_connect():
	g.db = connect_to_database();
	g.cur = g.db.cursor(MySQLdb.cursors.DictCursor);

@app.teardown_request
def db_disconnect(exception=None):
	g.db.close();

def exit_handler():
	db = connect_to_database();
	cur = db.cursor(MySQLdb.cursors.DictCursor);
	db.close();

atexit.register(exit_handler);

@app.route("/api/authenticate/", methods=["POST"])
def authenticate():
	try:
		data = json.loads(request.stream.read());
	except:
		return Utils.make_response({
			"status": "failure",
			"reason": "Unable to decode the JSON payload"
		}, 400);
	username = data.get("username") or "";
	password = data.get("password") or "";
	if not re.match("^[a-z0-9]{5,100}$", username):
		return Utils.make_response({
			"status": "failure",
			"reason": "Invalid username"
		}, 403);
	if not re.match("^(?=.*[A-Z]+)(?=.*[a-z]+)(?=.*[0-9]+)", password) or not re.match("^[a-zA-Z0-9]{10,100}$", password):
		return Utils.make_response({
			"status": "failure",
			"reason": "Invalid password"
		}, 403);
	random_token = Utils.token_hex();
	query = "SELECT u.id AS user_id FROM users u WHERE u.username = %s AND u.password = SHA2((%s), 256);";
	g.cur.execute(query, [username, password + config["PASSWORD_SALT"]]);
	row = g.cur.fetchone();
	if not row:
		return Utils.make_response({
			"status": "failure",
			"reason": "Invalid username or password"
		}, 403);
	user_id = row["user_id"];
	expire_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=config["MAX_SESSION_DURATION_IN_SECONDS"])
	response = Utils.make_response({
			"status": "success"
		}, 200);
	response.set_cookie(
			"token", 
			Token.encode(
				user_id, 
				random_token,
				config["SERVER_NONCE"],
				config["MAX_SESSION_DURATION_IN_SECONDS"]), 
			secure=False,
			httponly=True,
			expires=expire_date,
			samesite="Strict");
	return response

@app.route("/api/logout/")
def logout():
	response = Utils.make_response({
		"status": "success"
	}, 200);
	response.set_cookie("token", "", expires=0);
	return response

@app.route("/api/check_token/")
def check_token():
	cookie = request.cookies.get("token", None);
	token = Utils.get_token(cookie);
	if not token:
		return Utils.make_response({
			'status': 'failure',
			'reason': 'unauthorized'
			}, 403);
	else:
		return Utils.make_response({
			'status': 'success'
			}, 200);

@app.route("/api/request_password_reset/", methods=["POST"])
def request_password_reset():
	try:
		data = json.loads(request.stream.read());
	except:
		return Utils.make_response({
			"status": "failure",
			"reason": "Unable to decode the JSON payload"
		}, 400);
	username = data.get("username") or "";
	email = data.get("email") or "";
	response = Utils.make_response({
			"status": "success"
		}, 200);

@app.route("/api/confirm_password_reset/<token>/", methods=["GET"])
def confirm_password_reset(token):
	try:
		data = json.loads(request.stream.read());
	except:
		return Utils.make_response({
			"status": "failure",
			"reason": "Unable to decode the JSON payload"
		}, 400);
	response = Utils.make_response({
			"status": "success"
		}, 200);

@app.route("/api/reset_password/", methods=["POST"])
def reset_password():
	response = Utils.make_response({
			"status": "success"
		}, 200);

@app.route("/api/change_password/")
def change_password():
	cookie = request.cookies.get("token", None);
	token = Utils.get_token(cookie);
	if not token:
		return Utils.make_response({
			'status': 'failure',
			'reason': 'unauthorized'
			}, 403);
	try:
		data = json.loads(request.stream.read());
	except:
		return Utils.make_response({
			"status": "failure",
			"reason": "Unable to decode the JSON payload"
		}, 400);
	username = data.get("username") or "";
	old_password = data.get("old_password") or "";
	if not re.match("^(?=.*[A-Z]+)(?=.*[a-z]+)(?=.*[0-9]+)", old_password) or not re.match("^[a-zA-Z0-9]{10,100}$", old_password):
		return Utils.make_response({
			"status": "failure",
			"reason": "Invalid old password"
		}, 403);
	new_password = data.get("new_password") or "";
	if not re.match("^(?=.*[A-Z]+)(?=.*[a-z]+)(?=.*[0-9]+)", new_password) or not re.match("^[a-zA-Z0-9]{10,100}$", new_password):
		return Utils.make_response({
			"status": "failure",
			"reason": "Invalid new password"
		}, 403);
	query = "SELECT u.id AS user_id FROM users u WHERE u.username = %s AND u.password = SHA2((%s), 256);";
	g.cur.execute(query, [username, old_password + config["PASSWORD_SALT"]]);
	row = g.cur.fetchone();
	if not row:
		return Utils.make_response({
			"status": "failure",
			"reason": "Invalid old password"
		}, 403);
	user_id = Token.get_user_id(token);
	if user_id != row["user_id"]:
		return Utils.make_response({
			"status": "failure",
			"reason": "Invalid username"
			}, 403);
	query = "UPDATE users SET password = SHA2((%s), 256) WHERE id = %s;";
	g.cur.execute(query, [new_password + config["PASSWORD_SALT"], user_id]);
	g.db.commit();
	random_token = Utils.token_hex();
	expire_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=config["MAX_SESSION_DURATION_IN_SECONDS"])
	response = Utils.make_response({
			"status": "success"
		}, 200);
	response.set_cookie(
			"token", 
			Token.encode(
				user_id, 
				random_token,
				config["SERVER_NONCE"],
				config["MAX_SESSION_DURATION_IN_SECONDS"]), 
			secure=False,
			httponly=True,
			expires=expire_date,
			samesite="Strict");
	return response

@app.route("/api/channels/")
def get_channels():
	cookie = request.cookies.get("token", None);
	token = Utils.get_token(cookie);
	if not token:
		return Utils.make_response({
			'status': 'failure',
			'reason': 'unauthorized'
			}, 403);
	query = "SELECT id, channel_name, stream_id, icon_path FROM channels";
	g.cur.execute(query);
	rows = g.cur.fetchall();
	results = [];
	for row in rows:
		results.append({
			"id": row["id"],
			"channel_name": row["channel_name"],
			"stream_id": row["stream_id"],
			"icon_path": row["icon_path"]
			});
	return Utils.make_response({
		"status": "success",
		"result": results
	}, 200);

@app.route("/api/program/<int:channel_id>/")
def get_program(channel_id):
	cookie = request.cookies.get("token", None);
	token = Utils.get_token(cookie);
	if not token:
		return Utils.make_response({
			'status': 'failure',
			'reason': 'unauthorized'
			}, 403);
	query = "SELECT program_name, start_time, end_time FROM programs WHERE scheduled_for_insertion = FALSE AND channel_id = %s AND DAY(start_time) = DAY(NOW())";
	g.cur.execute(query, [channel_id]);
	rows = g.cur.fetchall();
	results = [];
	for row in rows:
		results.append({
			"program_name": row["program_name"],
			"start_time": row["start_time"],
			"end_time": row["end_time"]
			});
	return Utils.make_response({
		"status": "success",
		"result": results
	}, 200);

@app.route("/streaming/segments/<int:stream_id>/<int:timestamp>/<file>")
def get_stream_segment(stream_id, timestamp, file):
	cookie = request.cookies.get("token", None);
	token = Utils.get_token(cookie);
	if not token:
		return Utils.make_response({
			'status': 'failure',
			'reason': 'unauthorized'
			}, 403);
	web_root = config["WEB_ROOT"];
	filename = "".join([web_root, "/", str(stream_id), "/", str(timestamp), "/", file]);
	if not os.path.isfile(filename):
		return Utils.make_response({
			'status': 'failure',
			'reason': 'File not found'
			}, 404);
	return send_file(filename, mimetype='video/mp2t');

@app.route("/streaming/playlist/<int:stream_id>/stream.m3u8")
def get_playlist(stream_id):
	cookie = request.cookies.get("token", None);
	token = Utils.get_token(cookie);
	if not token:
		return Utils.make_response({
			'status': 'failure',
			'reason': 'unauthorized'
			}, 403);
	web_root = config["WEB_ROOT"];
	filename = "".join([web_root, "/", str(stream_id), "/stream.m3u8"]);
	if not os.path.isfile(filename):
		return Utils.make_response({
			'status': 'failure',
			'reason': 'File not found'
			}, 404);
	return send_file(filename, mimetype='application/vnd.apple.mpegurl', cache_timeout=-1);

@app.route("/streaming/keyfile/<int:stream_id>/<int:timestamp>/enc.key")
def get_keyfile(stream_id, timestamp):
	cookie = request.cookies.get("token", None);
	token = Utils.get_token(cookie);
	if not token:
		return Utils.make_response({
			'status': 'failure',
			'reason': 'unauthorized'
			}, 403);
	web_root = config["WEB_ROOT"];
	filename = "".join([web_root, "/", str(stream_id), "/", str(timestamp), "/enc.key"]);
	if not os.path.isfile(filename):
		return Utils.make_response({
			'status': 'failure',
			'reason': 'File not found'
			}, 404);
	return send_file(filename, mimetype='application/octet-stream');

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000);
