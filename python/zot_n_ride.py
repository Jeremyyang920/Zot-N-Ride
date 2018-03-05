from app import app
from collections import defaultdict
import json
import urllib.parse
import urllib.request
import sendgrid
import os
from sendgrid.helpers.mail import *
from authy.api import AuthyApiClient
import confidential
import logger
from pymongo import MongoClient
from user import User
from rider import Rider
from driver import Driver

### CONSTANTS
UCI_PLACE_ID = 'ChIJkb-SJQ7e3IAR7LfattDF-3k'
GOOGLE_API_KEY = confidential.GOOGLE_API_KEY
SENDGRID_API_KEY = confidential.SENDGRID_API_KEY
TWILIO_API_KEY = confidential.TWILIO_API_KEY
BASE_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&'
BUFFER_PICKUP_TIME = 5*60
DAY_ABBREVIATIONS = ['MON','TUE','WED','THU','FRI','SAT','SUN']
DEFAULT_ARRIVAL_TIME = '8:00'
DEFAULT_DEPARTURE_TIME = '18:00'
log = logger.configure_logger()
client = MongoClient(confidential.MONGO_CLIENT_URI)
db = client['test']
users = db.users

def calc_driving_time(source: str, destination: str) -> int:
    query_parameters = [('origins',source), ('destinations',destination), ('key',GOOGLE_API_KEY)]
    url = BASE_URL + urllib.parse.urlencode(query_parameters)
    json_to_read = get_json(url)
    return json_to_read['rows'][0]['elements'][0]['duration']['value']

def get_json(url: str) -> dict:
    response = None
    try:
        response = urllib.request.urlopen(url)
        return json.loads(response.read().decode(encoding='utf-8'))
    finally:
        if response != None:
            response.close()

def match_users(riders: [Rider], drivers: [Driver]) -> dict:
    result = defaultdict(dict)
    for rider in riders:
        for driver in drivers:
            delta_time = (calc_driving_time(driver.address,rider.address) + rider.time_to_uci + BUFFER_PICKUP_TIME) - driver.time_to_uci
            result[rider][driver] = delta_time
    return extract_matches(result)

def match_users_with_db(riders, drivers) -> dict:
    result = defaultdict(dict)
    for rider in riders:
        for driver in drivers:
            delta_time = (calc_driving_time(driver['address'],rider['address']) + rider['time_to_uci'] + BUFFER_PICKUP_TIME) - driver['time_to_uci']
            rider_name = rider['name']['first'] + ' ' + rider['name']['last']
            driver_name = driver['name']['first'] + ' ' + driver['name']['last']
            result[rider_name][driver_name] = delta_time
    return extract_matches(result)


def extract_matches(input_dict: dict) -> dict:
    result = dict()
    for k in input_dict:
        result[k] = min(input_dict[k].items(),key = lambda x: x[1])[0]
    return result

def confirm_email(u: User):
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
    from_email = Email('confirm_email@zotnride.tech')
    to_email = Email(u.email)
    subject = 'Confirm Your Zot N\' Ride Account'
    content = Content('text/plain', 'Click this link to verify your account: http://www.zotnride.tech/confirm.')
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    if response.status_code == 202:
        log.info('The email was successfully delivered to {}.'.format(u.email))
    else:
        log.error('There was an issue making the SendGrid API call. Please make sure that the recipient email address is valid.')

def confirm_phone(u: User):
    try:
        client = AuthyApiClient(TWILIO_API_KEY)
        user = client.users.create(u.email,u.phone,1)
        sms = client.users.request_sms(user.id)
        log.info('The confirmation code was successfully sent to {}.'.format(u.phone))
    except:
        log.error('There was an issue making the Twilio API call. Please make sure that the phone number is valid with the correct country code.')

def create_user_from_json(first_name: str, last_name: str):
    user = users.find_one({'name':{'first':first_name,'last':last_name}})
    if user['isDriver']:
        return Driver(first=user['name']['first'],last=user['name']['last'],age=int(user['age']),year=int(user['year']),netID=user['netID'],major=user['major'],phone=user['phone'],address=user['address'],car=Car(),zone=1)
    else:
        return Rider(first=user['name']['first'],last=user['name']['last'],age=int(user['age']),year=int(user['year']),netID=user['netID'],major=user['major'],phone=user['phone'],address=user['address'])

def load_all_users():
    riders,drivers = [],[]
    for user in users.find({}):
        users.update_one({'_id':user['_id']}, {'$set': {'time_to_uci':calc_driving_time(user['address'],'place_id:{}'.format(UCI_PLACE_ID))}}, upsert=False)
    for user in users.find({}):
        if user['isDriver']:
            drivers.append(user)
        else:
            riders.append(user)
    return riders,drivers

if __name__ == '__main__':
    riders,drivers = load_all_users()
    print(match_users_with_db(riders,drivers))
