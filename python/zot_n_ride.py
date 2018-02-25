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
        self.first_name = kwargs.get("first")
        self.last_name = kwargs.get("last")
        assert type(self.first_name) == str and type(self.last_name) == str
        self.full_name = self.get_full_name()

        self.age = kwargs.get("age")
        assert type(self.age) == int and self.age >= 18

        self.year = kwargs.get("year")
        assert type(self.year) == int and self.year >= 1 and self.year <= 6

        self.major = kwargs.get("major")
        assert type(self.major) == str

        self.UCInetID = kwargs.get("netID")
        assert type(self.UCInetID) == str
        self.email = self.get_email()

        self.phone = kwargs.get("phone")
        assert type(self.phone) == int
        assert len(str(self.phone)) == 10

        self.arrival_times = {"Mon": "", "Tue": "", "Wed": "", "Thu": "", "Fri": "", "Sat": "", "Sun": ""}
        self.departure_times = {"Mon": "", "Tue": "", "Wed": "", "Thu": "", "Fri": "", "Sat": "", "Sun": ""}

        self.address_street, self.address_zip = kwargs.get("address").split(";")
        self.distance_to_uci = self.calc_driving_distance()

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def get_email(self):
        return self.UCInetID + "@uci.edu"

    def display_phone(self):
        phone = str(self.phone)
        return "({}) {}-{}".format(phone[0:3],phone[3:6],phone[6:])

    def calc_driving_distance(self):
        URL='https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=place_id:ChIJkb-SJQ7e3IAR7LfattDF-3k&destinations=2842+longspur+dr+Fullerton,CA&key=AIzaSyAk1S7XvdmV-WpxfzuA7wuyeMuQfFkO1qA'
        jsonToRead=get_json(URL);

        return(jsonToRead['rows'][0]['elements'][0]['duration']['value'])

    def print_user_info(self):
        print("Full Name: {}\nAge: {}\nMajor: {}\nEmail: {}\nPhone: {}\nDistance: {}".format(self.full_name, self.age, self.major, self.email, self.display_phone(),self.distance_to_uci))

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
        print("Manufacturer: {}\nModel: {}\nYear: {}\nLicense Plate: {}".format(self.make, self.model, self.year, self.license_plate))

class Rider(User):
    pass

class Driver(User):
    def __init__(self, **kwargs):
        User.__init__(self, **kwargs)
        self.car = kwargs.get("car")
        assert type(self.car) == Car
        self.permit_zone = kwargs.get("zone")
        assert type(self.permit_zone) == int and self.permit_zone >= 1 and self.permit_zone <= 6

def get_json(url: str) -> dict:
    response = None
    try:
        response=urllib.request.urlopen(url)
        return json.loads(response.read().decode(encoding='utf-8'))
    finally:
        if response != None:
            response.close()


if __name__ == "__main__":
    c = Car(make="Hyundai",model="Sonata",year=2012,plate="DWG4321")
    c.print_car_info()
    d = Driver(first="Anuj",last="Shah",age=21,year=4,netID="anujs3",major="CS",phone=9144821633,address="Scripps Aisle; 92612",car=c,zone=1)
    d.print_user_info()