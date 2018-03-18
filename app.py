from flask import Flask,abort,request,Response
import urllib.parse
import json
from flask import jsonify
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from ics import Calendar
import calendar
import datetime
from os import environ

app = Flask(__name__)

import sys
import zot_n_ride as ZNR
import bcrypt

DEBUG_FLAG = environ.get('DEBUG_FLAG')

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

TEN_MINUTES = 10*60 # used to create a ten minute buffer before and after a class

@app.route('/')
@app.route('/home')
@app.route('/welcome')
def welcome():
    return 'Welcome to Zot n\' Ride!'

# Endpoint for Creating a User
@app.route('/api/register',methods=['POST'])
def register_user():
    if not request.json:
        abort(400)
    body = request.json
    hashedPW = bcrypt.hashpw(body['password'].encode('utf-8'),bcrypt.gensalt(12))
    query = ZNR.create_user_into_db(body['netID'],hashedPW,body['firstname'],body['lastname'],body['major'],body['address'],body['isDriver'],body['arrivals'],body['departures'])
    if query == None:
        abort(400)
    return get_user_json(query)

# Endpoint for Validating a Login
@app.route('/api/login',methods=['POST'])
def login_user():
    if not request.json:
        abort(400)
    body = request.json
    query = ZNR.validate_login(body['netID'],body['password'])
    if not query:
        abort(400)
    return get_user_json(query)

# Endpoint for User Profile
@app.route('/api/user/<netID>')
def display_user(netID):
    query = ZNR.get_user(netID)
    return get_user_json(query)

# Endpoint for Importing .ICS File Data
@app.route('/api/import',methods=['POST'])
def import_calendar_file():
    if not request.json:
        abort(400)
    body = request.json
    arrivals = dict()
    departures = dict()
    classes = []
    cal = Calendar(urllib.parse.unquote(body['ics_plaintext']))
    for event in cal.events:
        event.name = event.name.replace('+',' ')
        if 'Final Exam' not in event.name:
            course_name = ' '.join(event.name.split())
            classes.append(course_name)
            days = calendar.day_name[event.begin.weekday()][:3]
            begin_time, end_time = format_time(event.begin - datetime.timedelta(seconds=TEN_MINUTES)), format_time(event.end + datetime.timedelta(seconds=TEN_MINUTES))
            hours, minutes = str(event.duration).split(':')[:2]
            if 'LEC' in event.name:
                    days = handle_class_time(days,hours,minutes)
            begin_time_integer = time_to_int(begin_time)
            end_time_integer = time_to_int(end_time)
            for day in days.split():
                if day not in arrivals or begin_time_integer < arrivals[day]:
                    arrivals[day] = begin_time_integer
                if day not in departures or end_time_integer > departures[day]:
                    departures[day] = end_time_integer
    user_object = ZNR.update_user_times(body['netID'],arrivals,departures)
    ZNR.update_classes(body['netID'],classes)
    return get_user_json(user_object)

def format_time(date_object):
    return str(date_object.time())[:-3]

def time_to_int(time_string):
    return int(time_string[:2] + time_string[3:])

def handle_class_time(days,hours,minutes):
    if (hours,minutes) == ('1','20'):
        if days == 'Mon':
            days += ' Wed'
        if days == 'Tue':
            days += ' Thu'
    elif (hours,minutes) == ('0','50'):
        days += ' Wed Fri'
    return days

def get_user_json(query):
    return_value = query.copy()
    del return_value['_id']
    del return_value['password']
    return json.dumps(return_value)

# Endpoint to Add User to Request Pool
@app.route('/api/addRequest',methods=['POST'])
def add_request():
    if not request.json:
        abort(400)
    body = request.json
    query = ZNR.add_user_request(body['netID'],body['direction'],body['time'])
    if not query:
        abort(400)
    return get_user_json(query)

# Endpoint to Remove User from Request Pool
@app.route('/api/removeRequest',methods=['POST'])
def remove_request():
    if not request.json:
        abort(400)
    body = request.json
    query = ZNR.remove_user_request(body['netID'],body['direction'])
    # abort 400 if nothing was removed, meaning the request never existed
    if query == 0:
        abort(400)
    # need the call to ZNR.get_user because delete_one returns the count
    # of items deleted instead of the json of object deleted
    return get_user_json(ZNR.get_user(body['netID']))

# Endpoint to Display Rider Requests to Driver
@app.route('/api/getRequests/<netID>/<direction>')
def get_requests(netID,direction):
    if not ZNR.is_driver(netID):
        abort(400)
    direction_number = int(direction)
    if direction_number >= 2:
        abort(400)
    fetch_search = ZNR.find_previous_search(netID,direction_number)
    if fetch_search != None:
        return json.dumps(fetch_search[netID])
    lists = ZNR.load_all_requests()
    if direction_number == 0:
        return json.dumps(ZNR.match_users_to_uci(lists[0],lists[1])[netID])
    elif direction_number == 1:
        return json.dumps(ZNR.match_users_to_home(lists[2],lists[3])[netID])

# Endpoint to Confirm Match
@app.route('/api/confirmRequest',methods=['POST'])
def confirm_request():
    if not request.json:
        abort(400)
    body = request.json
    query = ZNR.add_match(body['driverID'],body['riderID'],body['direction'])
    if not query:
        abort(400)
    ZNR.remove_users_from_request_pool(body['driverID'],body['riderID'],body['direction'])
    if body['direction'] == 0:
        return 'Successfully matched {} with {} when going to UCI.'.format(body['driverID'],body['riderID'])
    elif body['direction'] == 1:
        return 'Successfully matched {} with {} when going home.'.format(body['driverID'],body['riderID'])

# Endpoint to Display User's Ride Status
@app.route('/api/getRideStatus')
def get_ride_status(netID):
    pass

# Endpoint to Remove Match
@app.route('/api/endRide',methods=['POST'])
def end_ride():
    if not request.json:
        abort(400)
    body = request.json
    query = ZNR.remove_match(body['driverID'],body['riderID'],body['direction'])
    if not query:
        abort(400)
    return 'Ride has ended between {} and {}.'.format(body['driverID'],body['riderID'])
    
if __name__ == '__main__':
    if DEBUG_FLAG == 'true':
        app.debug = True
