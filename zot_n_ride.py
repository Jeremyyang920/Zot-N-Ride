from app import app
from collections import defaultdict
import sendgrid
from sendgrid.helpers.mail import *
from authy.api import AuthyApiClient
from pymongo import MongoClient
import logger
import maps
import user
import rider
import driver
import bcrypt
from os import environ
import datetime

SENDGRID_API_KEY = environ.get('SENDGRID_API_KEY')
TWILIO_API_KEY = environ.get('TWILIO_API_KEY')
BASE_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&'
BUFFER_PICKUP_TIME = 5*60
DAYS_OF_WEEK = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

log = logger.configure_logger()
client = MongoClient(environ.get('MONGO_CLIENT_URI'))
db = client['test']
users = db.users
requests = db.requests
matches = db.matches

def match_users_with_db(riders, drivers) -> dict:
    tomorrow = DAYS_OF_WEEK[(datetime.datetime.today().weekday()+1)%len(DAYS_OF_WEEK)]
    result = defaultdict(dict)
    for rider in riders:
        for driver in drivers:
            delta_distance = abs((maps.calc_driving_time(driver['address'],rider['address']) + rider['time_to_uci'] + BUFFER_PICKUP_TIME) - driver['time_to_uci'])
            if tomorrow in rider['arrivals'] and tomorrow in driver['arrivals']:
                delta_arrival = abs(rider['arrivals'][tomorrow] - driver['arrivals'][tomorrow])
            else:
                delta_arrival = 0
            if tomorrow in rider['departures'] and tomorrow in driver['departures']:
                delta_departure = abs(rider['departures'][tomorrow] - driver['departures'][tomorrow])
            else:
                delta_departure = 0
            rider_name = rider['name']['first'] + ' ' + rider['name']['last']
            driver_name = driver['name']['first'] + ' ' + driver['name']['last']
            result[rider_name][driver_name] = delta_distance + delta_arrival + delta_departure
    return extract_matches(result)

def match_users_with_classes(riders: [rider.Rider], drivers: [driver.Driver]) -> dict:
    result = defaultdict(dict)
    for rider in riders:
        for driver in drivers:
            delta_time = (maps.calc_driving_time(driver.address,rider.address) + rider.time_to_uci + BUFFER_PICKUP_TIME) - driver.time_to_uci
            result[rider][driver] = delta_time
    return extract_matches(result)

def extract_matches(input_dict: dict) -> dict:
    result = dict()
    for k in input_dict:
        result[k] = sorted(input_dict[k].items(),key = lambda x: x[1])[:3]
    return result

def confirm_email(u: user.User):
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

def confirm_phone(u: user.User):
    try:
        client = AuthyApiClient(TWILIO_API_KEY)
        user = client.users.create(u.email,u.phone,1)
        sms = client.users.request_sms(user.id)
        log.info('The confirmation code was successfully sent to {}.'.format(u.phone))
    except:
        log.error('There was an issue making the Twilio API call. Please make sure that the phone number is valid with the correct country code.')

def load_all_users():
    riders,drivers = [],[]
    for user in requests.find({}):
        users.update_one({'_id':user['_id']}, {'$set': {'time_to_uci':maps.calc_driving_time(user['address'],'place_id:{}'.format(maps.UCI_PLACE_ID))}}, upsert=False)
    for user in requests.find({}):
        if 'arrivals' in user and 'departures' in user:
            if user['isDriver']:
                drivers.append(user)
            else:
                riders.append(user)
    return riders,drivers

def create_user_from_json(first_name: str, last_name: str):
    user = users.find_one({'name':{'first':first_name,'last':last_name}})
    if user['isDriver']:
        return driver.Driver(first=user['name']['first'],last=user['name']['last'],age=int(user['age']),year=int(user['year']),netID=user['netID'],major=user['major'],phone=user['phone'],address=user['address'],car=Car(),zone=1)
    else:
        return rider.Rider(first=user['name']['first'],last=user['name']['last'],age=int(user['age']),year=int(user['year']),netID=user['netID'],major=user['major'],phone=user['phone'],address=user['address'])

def create_user_into_db(netID:str,password:str,first_name:str,last_name:str,major:str,address:str,isDriver:bool,arrivals:dict,departures:dict):
    if users.find_one({'netID':netID}) != None:
        log.error('User already exists.')
        return None
    user = users.insert_one({'netID':netID,'password':password,'name':{'first':first_name,'last':last_name},'major':major,'address':address,'isDriver':isDriver,'arrivals':arrivals,'departures':departures})
    log.info('User successfully created.')
    return get_user(netID)

def validate_login(netID:str,password:str):
    if users.find_one({'netID':netID}) == None:
        log.error('The netID was not found.')
        return False
    match = bcrypt.checkpw(password.encode('utf-8'),users.find_one({'netID':netID})['password'])
    if not match:
        log.error('Password does not match.')
        return False
    log.info('User successfully validated.')
    return get_user(netID)

def get_user(netID:str):
    return users.find_one({'netID':netID})

def update_user_times(netID:str,arrivals:dict,departures:dict):
    user = users.find_one({'netID':netID})
    for k,v in arrivals.items():
        users.update_one({'_id':user['_id']}, {'$set': {'arrivals.'+k:v}}, upsert=False)
    for k,v in departures.items():
        users.update_one({'_id':user['_id']}, {'$set': {'departures.'+k:v}}, upsert=False)
    return user

def update_classes(netID:str,classes:[str]):
    user = users.find_one({'netID':netID})
    users.update_one({'_id':user['_id']}, {'$set': {'classes':classes}}, upsert=False)

def add_user_request(netID:str,direction:int,time:int):
    requests.insert_one({'netID':netID,'direction':direction,'time':time})
    return get_user(netID)

def remove_user_request(netID:str,direction:int):
    # this function assumes that a user will only have one "to" and one "from" request (no duplicates)
    result = requests.delete_one({'netID':netID,'direction':direction})
    return result

if __name__ == '__main__':
    riders,drivers = load_all_users()
    print(match_users_with_db(riders,drivers))
