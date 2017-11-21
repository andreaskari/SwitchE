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

COST_PER_HOUR = {
	0:  0.202,
	8:  0.230,
	12: 0.253,
	14: 0.853,
	18: 0.230,
	21: 0.202,
}

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

def get_last_number_stream_items(collection_name, limit):
	db = get_database()
	collection = get_collection(db, collection_name)
	result = collection.find().sort('timestamp', pymongo.DESCENDING).limit(limit)
	return result

def calculate_energy_last_hour(): 
	result = get_last_number_stream_items(CURRENT_COLLECTION, 10)
	utc_timestamp_seconds = int(datetime.datetime.now().strftime('%s'))
	energy = 0.0
	for r in result:
		date_obj = datetime.datetime.fromtimestamp(r['timestamp'])
		seconds = (utc_timestamp_seconds - date_obj).total_seconds()
		if seconds < 3600:
			power = 120.0 * float(r['value'])
			# Energy from power: times 1 sec (then convert to kWh)
			energy += power / 3600.0 
	desired_data = {
		'timestamp': utc_timestamp_seconds,
		'energy': energy
	}
	return desired_data

def calculate_cost_last_hour(): 
	data_list = calculateEnergyLastHour()
	hour = (r['timestamp'] % 3600) / 60
	last_slot = COST_PER_HOUR.keys()[0]
	for time_slot in COST_PER_HOUR.keys():
		if hour < time_slot:
			break
		last_slot = time_slot
	rate = COST_PER_HOUR[last_slot]
	desired_data = {
		'timestamp': r['timestamp'],
		'cost': rate * r['energy']
	}
	return desired_data

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
		'current': float(result['value'])
	}
	return jsonify(desired_data)

@app.route('/getLastPower', methods=['GET']) 
def getLastPower(): 
	result = get_last_stream_item(CURRENT_COLLECTION)
	desired_data = {
		'timestamp': result['timestamp'],
		'power': 120.0 * float(result['value'])
	}
	return jsonify(desired_data)

@app.route('/getPowerHistory', methods=['GET']) 
def getPowerHistory(): 
	result = get_last_number_stream_items(CURRENT_COLLECTION, 10)
	desired_data_list = []
	for r in result:
		desired_data_list.append({
			'timestamp': r['timestamp'],
			'power': 120.0 * float(r['value'])
		})
	return jsonify(desired_data_list)

@app.route('/getEnergyLastHour', methods=['GET']) 
def getEnergyLastHour(): 
	desired_data = calculate_energy_last_hour()
	return jsonify(desired_data)

@app.route('/getCostLastHour', methods=['GET']) 
def getCostLastHour(): 
	desired_data = calculate_cost_last_hour()
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

