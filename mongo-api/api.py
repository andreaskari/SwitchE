## Created by Andre Askarinam, 2017

# -- Imports -- #

import socket 
import datetime
import pprint
import pymongo
from pymongo import MongoClient
from flask import Flask, request, jsonify


# -- Constants -- #

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

FLASK_HOST = '0.0.0.0'
FLASK_PORT = 80

DATABASE = 'switche'

CURRENT_COLLECTION = 'current'
GEOLOCATION_COLLECTION = 'geolocation'
IO_COLLECTION = 'io'
SETTINGS_COLLECTION = 'settings'

MANUAL_SETTINGS_MODE = 'manual'
TIMER_SETTINGS_MODE = 'timer'
GEOLOCATION_SETTINGS_MODE = 'geolocation'


# -- Classes & Methods -- #

def get_database():
	client = MongoClient(MONGODB_HOST, MONGODB_PORT)
	return client[DATABASE]

def get_collection(db, collection_name):
	return db[collection_name]

def insert_to_stream_collection(collection_name, value):
	db = get_database()
	collection = get_collection(db, collection_name)
	utc_timestamp_seconds = int(datetime.datetime.now().strftime('%s'))
	post = {
		'timestamp': utc_timestamp_seconds,
		'value': value
	}
	post_id = collection.insert_one(post).inserted_id
	return post_id

def get_last_stream_item(collection_name):
	db = get_database()
	collection = get_collection(db, collection_name)
	result = collection.find().sort('timestamp', pymongo.DESCENDING).limit(1)
	return result[0]

# def update_settings_collection(settings):
# 	db = get_database()
# 	collection = get_collection(db, SETTINGS_COLLECTION)
# 	utc_timestamp_seconds = int(datetime.datetime.now().strftime('%s'))
# 	settings = {
# 		'timestamp': utc_timestamp_seconds,
# 		'mode': ,
# 		'manual_IO': ,
# 		'timer_start_time': ,
# 		'timer_end_time': ,
# 		'geolocation_lat_long',
# 		'geolocation_radius',
# 	}

# -- API Endpoints -- #

app = Flask(__name__)

@app.route('/')
def root():
  return "This is our sexy API sitting on MongoDB"


@app.route('/getLastCurrent', methods=['GET']) 
def getLastCurrent(): 
	result = get_last_stream_item(CURRENT_COLLECTION)
	desired_data = {
		'timestamp': result['timestamp'],
		'value': result['value']
	}
	return jsonify(desired_data)

@app.route('/getLastLocation', methods=['GET']) 
def getLastLocation(): 
	result = get_last_stream_item(GEOLOCATION_COLLECTION)
	desired_data = {
		'timestamp': result['timestamp'],
		'value': result['value']
	}
	return jsonify(desired_data)

@app.route('/getLastIO', methods=['GET']) 
def getLastIO(): 
	result = get_last_stream_item(IO_COLLECTION)
	desired_data = {
		'timestamp': result['timestamp'],
		'value': result['value']
	}
	return jsonify(desired_data)

@app.route('/getLastSettings', methods=['GET'])
def getLastSettings(): 
	result = get_last_stream_item(SETTINGS_COLLECTION)
	desired_data = {
		'timestamp': result['timestamp'],
		'value': result['value']
	}
	return jsonify(desired_data)


@app.route('/postCurrent/<value>', methods=['POST']) 
def postCurrent(value): 
	insert_to_stream_collection(CURRENT_COLLECTION, value)
	return jsonify({"code": 200})

@app.route('/postLocation/<value>', methods=['POST']) 
def postLocation(value): 
	insert_to_stream_collection(GEOLOCATION_COLLECTION, value)
	return jsonify({"code": 200})

@app.route('/postIO/<value>', methods=['POST']) 
def postIO(value): 
	insert_to_stream_collection(IO_COLLECTION, value)
	return jsonify({"code": 200})

@app.route('/postSettings/<value>', methods=['POST'])
def postSettings(value): 
	insert_to_stream_collection(SETTINGS_COLLECTION, value)
	return jsonify({"code": 200})


# -- Execution -- #

if __name__ == '__main__': 
	app.run(host=FLASK_HOST, port=FLASK_PORT)

