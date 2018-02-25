import random
import collections
import json
import urllib.parse
import urllib.request

### CONSTANTS
UCI_PLACE_ID = 'ChIJkb-SJQ7e3IAR7LfattDF-3k'
GOOGLE_API_KEY = 'AIzaSyAk1S7XvdmV-WpxfzuA7wuyeMuQfFkO1qA'

class User:
    def __init__(self, **kwargs):
        self.first_name = kwargs.get('first')
        self.last_name = kwargs.get('last')
        assert type(self.first_name) == str and type(self.last_name) == str
        self.full_name = self.get_full_name()

        self.age = kwargs.get('age')
        assert type(self.age) == int and self.age >= 18

        self.year = kwargs.get('year')
        assert type(self.year) == int and self.year >= 1 and self.year <= 6

        self.major = kwargs.get('major')
        assert type(self.major) == str

        self.UCInetID = kwargs.get('netID')
        assert type(self.UCInetID) == str
        self.email = self.get_email()

        self.phone = kwargs.get('phone')
        assert type(self.phone) == int
        assert len(str(self.phone)) == 10

        self.arrival_times = {'Mon': '8:00', 'Tue': '8:00', 'Wed': '8:00', 'Thu': '8:00', 'Fri': '8:00', 'Sat': '8:00', 'Sun': '8:00'}
        self.departure_times = {'Mon': '18:00', 'Tue': '18:00', 'Wed': '18:00', 'Thu': '18:00', 'Fri': '18:00', 'Sat': '18:00', 'Sun': '18:00'}

        self.address = kwargs.get('address')
        # self.address_street, self.address_zip = kwargs.get('address').split(';')
        self.time_to_uci = self.calc_driving_time_to_uci()

    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_email(self):
        return self.UCInetID + '@uci.edu'

    def display_phone(self):
        phone = str(self.phone)
        return '({}) {}-{}'.format(phone[0:3],phone[3:6],phone[6:])

    def calc_driving_time_to_uci(self):
        return calc_driving_time(self.address,'place_id:{}'.format(UCI_PLACE_ID))

    def print_user_info(self):
        print('Full Name: {}\nAge: {}\nMajor: {}\nEmail: {}\nPhone: {}\nDistance: {} Seconds'.format(self.full_name, self.age, self.major, self.email, self.display_phone(),self.time_to_uci))

class Car:
    def __init__(self, **kwargs):
        self.make = kwargs.get("make")
        assert type(self.make) == str
        self.model = kwargs.get("model")
        assert type(self.model) == str
        self.year = kwargs.get("year")
        assert type(self.year) == int
        self.license_plate = kwargs.get("plate")
        assert type(self.license_plate) == str

    def print_car_info(self):
        print('Manufacturer: {}\nModel: {}\nYear: {}\nLicense Plate: {}'.format(self.make, self.model, self.year, self.license_plate))

class Rider(User):
    pass

class Driver(User):
    def __init__(self, **kwargs):
        User.__init__(self, **kwargs)
        self.car = kwargs.get('car')
        assert type(self.car) == Car
        self.permit_zone = kwargs.get('zone')
        assert type(self.permit_zone) == int and self.permit_zone >= 1 and self.permit_zone <= 6

def calc_driving_time(source,destination):
    BASE_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&'
    query_parameters = [('origins',source), ('destinations',destination), ('key',GOOGLE_API_KEY)]
    URL = BASE_URL + urllib.parse.urlencode(query_parameters)
    jsonToRead = get_json(URL)
    return jsonToRead['rows'][0]['elements'][0]['duration']['value']

def get_json(url: str) -> dict:
    response = None
    try:
        response=urllib.request.urlopen(url)
        return json.loads(response.read().decode(encoding='utf-8'))
    finally:
        if response != None:
            response.close()

def match_users(drivers: [Driver], riders: [Rider]):
    result = []
    for d in drivers:
        for r in riders:
            delta_t = (calc_driving_time(d.address,r.address) + r.time_to_uci + 5) - d.time_to_uci
            result.append(d,r,delta_t)
    return result

if __name__ == '__main__':
    c = Car(make="Hyundai",model="Sonata",year=2012,plate="DWG4321")
    c.print_car_info()
    d = Driver(first="Anuj",last="Shah",age=21,year=4,netID="anujs3",major="CS",phone=9144821633,address="63921 Arroyo Dr, Irvine CA 92617",car=c,zone=1)
    d.print_user_info()
