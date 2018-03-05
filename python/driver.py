from user import User
from car import Car

class Driver(User):
    def __init__(self, **kwargs):
        User.__init__(self, **kwargs)
        self.car = kwargs.get('car', Car())
        assert type(self.car) == Car
        self.permit_zone = kwargs.get('zone',1)
        assert type(self.permit_zone) == int and self.permit_zone >= 1 and self.permit_zone <= 6
