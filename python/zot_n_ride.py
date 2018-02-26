import random
from collections import defaultdict
import json
import urllib.parse
import urllib.request

### CONSTANTS
UCI_PLACE_ID = 'ChIJkb-SJQ7e3IAR7LfattDF-3k'
GOOGLE_API_KEY = 'AIzaSyAk1S7XvdmV-WpxfzuA7wuyeMuQfFkO1qA'
BUFFER_PICKUP_TIME = 5*60
DAY_ABBREVIATIONS = ['MON','TUE','WED','THU','FRI','SAT','SUN']
DEFAULT_ARRIVAL_TIME = '8:00'
DEFAULT_DEPARTURE_TIME = '18:00'

class User:
    def __init__(self, **kwargs):
        self.first_name = kwargs.get('first','Peter')
        self.last_name = kwargs.get('last','Anteater')
        assert type(self.first_name) == str and type(self.last_name) == str
        self.full_name = self.get_full_name()

        self.age = kwargs.get('age',18)
        assert type(self.age) == int and self.age >= 18

        self.year = kwargs.get('year',1)
        assert type(self.year) == int and self.year >= 1 and self.year <= 6

        self.major = kwargs.get('major','CS')
        assert type(self.major) == str

        self.UCInetID = kwargs.get('netID','panteater')
        assert type(self.UCInetID) == str
        self.email = self.get_email()

        self.phone = self.parse_phone(kwargs.get('phone','111-111-1111'))
        assert type(self.phone) == int
        assert len(str(self.phone)) == 10

        self.arrival_list = kwargs.get('arrivals',[DEFAULT_ARRIVAL_TIME]*len(DAY_ABBREVIATIONS))
        self.arrival_times = list(zip(DAY_ABBREVIATIONS,self.arrival_list))
        self.departure_list = kwargs.get('departures',[DEFAULT_DEPARTURE_TIME]*len(DAY_ABBREVIATIONS))
        self.departure_times = list(zip(DAY_ABBREVIATIONS,self.departure_list))

        self.address = kwargs.get('address','place_id:{}'.format(UCI_PLACE_ID))
        self.time_to_uci = self.calc_driving_time_to_uci()

    def __repr__(self):
        return self.full_name

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_email(self):
        return self.UCInetID + '@uci.edu'

    def parse_phone(self, phone_string: str) -> int:
        phone_numbers = ''
        for char in phone_string:
            try:
                int(char)
                phone_numbers += char
            except ValueError:
                pass
        return int(phone_numbers)

    def display_phone(self) -> str:
        phone = str(self.phone)
        return '({area_code}) {next_three_digits}-{last_four_digits}'.format(area_code=phone[0:3],next_three_digits=phone[3:6],last_four_digits=phone[6:])

    def calc_driving_time_to_uci(self) -> int:
        return calc_driving_time(self.address,'place_id:{}'.format(UCI_PLACE_ID))

    def print_user_info(self):
        base_string = 'Full Name: {}\nAge: {}\nAcademic Year: {}\nMajor: {}\nEmail: {}\nPhone Number: {}\nAddress: {}'
        formatted_string = base_string.format(self.full_name,self.age,self.year,self.major,self.email,self.display_phone(),self.address)
        print(formatted_string)

class Car:
    def __init__(self, **kwargs):
        self.make = kwargs.get('make','Honda')
        assert type(self.make) == str
        self.model = kwargs.get('model','Civic')
        assert type(self.model) == str
        self.year = kwargs.get('year',2000)
        assert type(self.year) == int and len(str(self.year)) == 4
        self.license_plate = kwargs.get('plate','HON1234')
        assert type(self.license_plate) == str

    def print_car_info(self):
        print('Manufacturer: {}\nModel: {}\nYear: {}\nLicense Plate: {}'.format(self.make, self.model, self.year, self.license_plate))

class Rider(User):
    pass

class Driver(User):
    def __init__(self, **kwargs):
        User.__init__(self, **kwargs)
        self.car = kwargs.get('car', Car())
        assert type(self.car) == Car
        self.permit_zone = kwargs.get('zone',1)
        assert type(self.permit_zone) == int and self.permit_zone >= 1 and self.permit_zone <= 6

def calc_driving_time(source: str, destination: str) -> int:
    BASE_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&'
    query_parameters = [('origins',source), ('destinations',destination), ('key',GOOGLE_API_KEY)]
    URL = BASE_URL + urllib.parse.urlencode(query_parameters)
    jsonToRead = get_json(URL)
    return jsonToRead['rows'][0]['elements'][0]['duration']['value']

def get_json(url: str) -> dict:
    response = None
    try:
        response = urllib.request.urlopen(url)
        return json.loads(response.read().decode(encoding='utf-8'))
    finally:
        if response != None:
            response.close()

def match_users(drivers: [Driver], riders: [Rider]) -> dict:
    result = defaultdict(dict)
    for rider in riders:
        for driver in drivers:
            delta_time = (calc_driving_time(driver.address,rider.address) + rider.time_to_uci + BUFFER_PICKUP_TIME) - driver.time_to_uci
            result[rider][driver] = delta_time
    return extract_matches(result)

def extract_matches(input_dict) -> dict:
    result = dict()
    for k in input_dict:
        result[k] = min(input_dict[k].items(),key = lambda x: x[1])[0]
    return result

if __name__ == '__main__':
    car = Car(make='Hyundai',model='Sonata',year=2012,plate='DWG4321')
    driver1 = Driver(first='Jeremy',last='Yang',age=21,year=4,netID='jeremy2',major='CS',phone='7142532338',address='175 Amerherst Aisle, Irvine, CA',car=car,zone=1)
    driver2 = Driver(first='Chris',last='Wong',age=21,year=4,netID='tvwong',major='CS',phone='1111111111',address='3 Rockview, Irvine CA, Irvine, CA',car=car,zone=1)
    rider1 = Rider(first='Anuj',last='Shah',age=21,year=4,netID='anujs3',major='CS',phone='914-482-1633',address='8 Scripps Aisle, Irvine, CA')
    rider1.print_user_info()
    rider2 = Rider(first='Jonathan',last='Nguyen',age=21,year=4,netID='jonatn8',major='CS',phone='2222222222',address='3 Rockview, Irvine, CA')
    drivers = [driver1,driver2]
    riders = [rider1,rider2]
    print(match_users(drivers,riders))
