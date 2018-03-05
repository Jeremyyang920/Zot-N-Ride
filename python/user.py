import maps

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
        self.password = kwargs.get('password')

        self.phone = self.parse_phone(kwargs.get('phone','111-111-1111'))
        assert type(self.phone) == int
        assert len(str(self.phone)) == 10

        self.arrival_list = kwargs.get('arrivals',[DEFAULT_ARRIVAL_TIME]*len(DAY_ABBREVIATIONS))
        self.arrival_times = list(zip(DAY_ABBREVIATIONS,self.arrival_list))
        self.departure_list = kwargs.get('departures',[DEFAULT_DEPARTURE_TIME]*len(DAY_ABBREVIATIONS))
        self.departure_times = list(zip(DAY_ABBREVIATIONS,self.departure_list))

        self.address = kwargs.get('address','place_id:{}'.format(maps.UCI_PLACE_ID))
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
        return '{area_code}-{next_three_digits}-{last_four_digits}'.format(area_code=phone[0:3],next_three_digits=phone[3:6],last_four_digits=phone[6:])

    def calc_driving_time_to_uci(self) -> int:
        return maps.calc_driving_time(self.address,'place_id:{}'.format(maps.UCI_PLACE_ID))

    def print_user_info(self):
        base_string = 'Full Name: {}\nAge: {}\nAcademic Year: {}\nMajor: {}\nEmail: {}\nPhone Number: {}\nAddress: {}'
        formatted_string = base_string.format(self.full_name,self.age,self.year,self.major,self.email,self.display_phone(),self.address)
        print(formatted_string)
