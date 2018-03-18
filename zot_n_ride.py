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
searches = db.searches

def match_users_to_uci(riders:list, drivers:list) -> dict:
    result = defaultdict(dict)
    for rider_tuple in riders:
        rider,rider_time = rider_tuple
        for driver_tuple in drivers:
            driver,driver_time = driver_tuple
            detour_time = calc_detour_time_to_uci(driver['address'],rider['address'],rider['time_to_uci'])
            delta_route = abs(detour_time - driver['time_to_uci'])
            delta_arrival = abs(rider_time - driver_time)
            result[driver['netID']][rider['netID']] = {'solo_time':driver['time_to_uci'],'carpool_time':detour_time,'delta_route':delta_route,'delta_time':delta_arrival,
                                                       'score':delta_route+delta_arrival}
    ranked_results = rank_matches(result)
    for k,v in ranked_results.items():
        if searches.find_one({'driverID':k,'direction':0}) == None:
            searches.insert_one({'driverID':k,'direction':0,'rankedMatches':v})
    return ranked_results

def match_users_to_home(riders:list, drivers:list) -> dict:
    result = defaultdict(dict)
    for rider_tuple in riders:
        rider,rider_time = rider_tuple
        for driver_tuple in drivers:
            driver,driver_time = driver_tuple
            detour_time = calc_detour_time_to_home(driver['address'],rider['address'],rider['time_to_home'])
            delta_route = abs(detour_time - driver['time_to_home'])
            delta_departure = abs(rider_time - driver_time)
            result[driver['netID']][rider['netID']] = {'solo_time':driver['time_to_home'],'carpool_time':detour_time,'delta_route':delta_route,'delta_time':delta_departure,
                                                       'score':delta_route+delta_departure}
    ranked_results = rank_matches(result)
    for k,v in ranked_results.items():
        if searches.find_one({'driverID':k,'direction':1}) == None:
            searches.insert_one({'driverID':k,'direction':1,'rankedMatches':v})
    return ranked_results

def rank_matches(input_dict:dict) -> dict:
    result = dict()
    for k in input_dict:
        result[k] = [{'riderID':tup[0],'results':tup[1]} for tup in sorted(input_dict[k].items(),key = lambda x: x[1]['score'])]
    return result

def calc_detour_time_to_uci(driver_address:str, rider_address:str, rider_to_uci:int) -> int:
    return (maps.calc_driving_time(driver_address,rider_address) + rider_to_uci) + BUFFER_PICKUP_TIME

def calc_detour_time_to_home(driver_address:str, rider_address:str, rider_to_home:int) -> int:
    return (rider_to_home + maps.calc_driving_time(rider_address,driver_address)) + BUFFER_PICKUP_TIME

def calc_delta_time(rider:dict, driver:dict, key:str, day:str) -> int:
    delta_time = 0
    if time_exists(rider,driver,key,day):
        delta_time = abs(rider[key][day] - driver[key][day])
    return delta_time

def time_exists(rider:dict, driver:dict, key:str, day:str) -> bool:
    return day in rider[key] and day in driver[key]

def calc_tomorrow() -> str:
    return DAYS_OF_WEEK[(datetime.datetime.today().weekday()+1)%len(DAYS_OF_WEEK)]

def match_users_with_classes(riders:[rider.Rider], drivers:[driver.Driver]) -> dict:
    result = defaultdict(dict)
    for rider in riders:
        for driver in drivers:
            delta_time = (maps.calc_driving_time(driver.address,rider.address) + rider.time_to_uci + BUFFER_PICKUP_TIME) - driver.time_to_uci
            result[rider][driver] = delta_time
    return rank_matches(result)

def load_all_requests() -> (list,list,list,list):
    uci_riders,uci_drivers = [],[]
    home_riders,home_drivers = [],[]
    update_driving_times()
    for request in requests.find({}):
        user = users.find_one({'netID':request['netID']})
        if user['isDriver']:
            if going_towards_uci(request):
                uci_drivers.append((user,request['time']))
            else:
                home_drivers.append((user,request['time']))
        else:
            if going_towards_uci(request):
                uci_riders.append((user,request['time']))
            else:
                home_riders.append((user,request['time']))
    return uci_riders,uci_drivers,home_riders,home_drivers

def update_driving_times() -> None:
    for request in requests.find({}):
        user = users.find_one({'netID':request['netID']})
        if going_towards_uci(request):
            if 'time_to_uci' not in user:
                users.update_one({'netID':request['netID']}, {'$set': {'time_to_uci':maps.calc_driving_time(user['address'],'place_id:{}'.format(maps.UCI_PLACE_ID))}}, upsert=False)
        else:
            if 'time_to_home' not in user:
                users.update_one({'netID':request['netID']}, {'$set': {'time_to_home':maps.calc_driving_time('place_id:{}'.format(maps.UCI_PLACE_ID),user['address'])}}, upsert=False)

def going_towards_uci(request:dict) -> bool:
    return request['direction'] == 0

def create_user_from_json(first_name:str, last_name:str) -> user.User:
    user = users.find_one({'name':{'first':first_name,'last':last_name}})
    if user['isDriver']:
        return driver.Driver(first=user['name']['first'],last=user['name']['last'],age=int(user['age']),year=int(user['year']),netID=user['netID'],major=user['major'],phone=user['phone'],address=user['address'],car=Car(),zone=1)
    else:
        return rider.Rider(first=user['name']['first'],last=user['name']['last'],age=int(user['age']),year=int(user['year']),netID=user['netID'],major=user['major'],phone=user['phone'],address=user['address'])

def create_user_into_db(netID:str, password:str, first_name:str, last_name:str, major:str, address:str, is_driver:bool, arrivals:dict, departures:dict):
    if users.find_one({'netID':netID}) != None:
        log.error('User already exists.')
        return None
    user = users.insert_one({'netID':netID,'password':password,'name':{'first':first_name,'last':last_name},'major':major,'address':address,'isDriver':is_driver,'arrivals':arrivals,'departures':departures})
    log.info('User successfully created.')
    return get_user(netID)

def validate_login(netID:str, password:str) -> dict:
    if users.find_one({'netID':netID}) == None:
        log.error('The netID was not found.')
        return False
    match = bcrypt.checkpw(password.encode('utf-8'),users.find_one({'netID':netID})['password'])
    if not match:
        log.error('Password does not match.')
        return False
    log.info('User successfully validated.')
    return get_user(netID)

def get_user(netID:str) -> dict:
    return users.find_one({'netID':netID})

def update_user_times(netID:str, arrivals:dict, departures:dict) -> dict:
    user = users.find_one({'netID':netID})
    for k,v in arrivals.items():
        users.update_one({'_id':user['_id']}, {'$set': {'arrivals.'+k:v}}, upsert=False)
    for k,v in departures.items():
        users.update_one({'_id':user['_id']}, {'$set': {'departures.'+k:v}}, upsert=False)
    return user

def update_classes(netID:str, classes:[str]) -> dict:
    user = users.find_one({'netID':netID})
    users.update_one({'_id':user['_id']}, {'$set': {'classes':classes}}, upsert=False)
    return user

def add_user_request(netID:str, direction:int, time:int) -> dict:
    if users.find_one({'netID':netID}) == None or requests.find_one({'netID':netID,'direction':direction}) != None:
        return False
    requests.insert_one({'netID':netID,'direction':direction,'time':time})
    return get_user(netID)

def remove_user_request(netID:str, direction:int) -> int:
    # this function assumes that a user will only have one "to" and one "from" request (no duplicates)
    result = requests.delete_one({'netID':netID,'direction':direction})
    return result

def find_previous_search(netID:str, direction:int) -> dict:
    return searches.find_one({'netID':netID,'direction':direction})

def is_driver(netID:str) -> bool:
    user = users.find_one({'netID':netID})
    return user['isDriver']

def remove_users_from_request_pool(driverID:str,riderID:str,direction:int) -> None:
    remove_user_request(driverID,direction)
    remove_user_request(riderID,direction)

def add_match(driverID:str,riderID:str,direction:int) -> dict:
    new_match = dict()
    if matches.find_one({'driverID':driverID,'riderID':riderID,'direction':direction}) == None:
        new_match = matches.insert_one({'driverID':driverID,'riderID':riderID,'direction':direction})
    return new_match

def remove_match(driverID:str,riderID:str,direction:int) -> bool:
    if matches.find_one({'driverID':driverID,'riderID':riderID,'direction':direction}) == None:
        return False
    result = matches.delete_one({'driverID':driverID,'riderID':riderID,'direction':direction})
    return True

def get_rides(netID:str) -> dict:
    result = {}
    for match in matches.find({}):
        if match['riderID'] == netID:
            if match['direction'] == 0:
                result['toSchool'] = {'driverID':match['driverID']}
            elif match['direction'] == 1:
                result['fromSchool'] = {'driverID':match['driverID']}
        elif match['driverID'] == netID:
            if match['direction'] == 0:
                result['toSchool'] = {'riderID':match['riderID']}
            elif match['direction'] == 1:
                result['fromSchool'] = {'riderID':match['riderID']}
    return result

def confirm_email(u:user.User) -> None:
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
    from_email = Email('confirm_email@zotnride.stream')
    to_email = Email(u.email)
    subject = 'Confirm Your Zot N\' Ride Account'
    content = Content('text/plain', 'Click this link to verify your account: http://www.zotnride.stream/confirm.')
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    if response.status_code == 202:
        log.info('The email was successfully delivered to {}.'.format(u.email))
    else:
        log.error('There was an issue making the SendGrid API call. Please make sure that the recipient email address is valid.')

def confirm_phone(u:user.User) -> None:
    try:
        client = AuthyApiClient(TWILIO_API_KEY)
        user = client.users.create(u.email,u.phone,1)
        sms = client.users.request_sms(user.id)
        log.info('The confirmation code was successfully sent to {}.'.format(u.phone))
    except:
        log.error('There was an issue making the Twilio API call. Please make sure that the phone number is valid with the correct country code.')

if __name__ == '__main__':
    uci_riders,uci_drivers,home_riders,home_drivers = load_all_requests()
    uci_matches = match_users_to_uci(uci_riders,uci_drivers)
    home_matches = match_users_to_home(home_riders,home_drivers)
    print('To UCI: {}'.format(uci_matches))
    print('From UCI: {}'.format(home_matches))
