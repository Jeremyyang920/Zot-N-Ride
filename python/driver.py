import user
import car

class Driver(user.User):
    def __init__(self, **kwargs):
        user.User.__init__(self, **kwargs)
        self.car = kwargs.get('car', car.Car())
        assert type(self.car) == car.Car
        self.permit_zone = kwargs.get('zone',1)
        assert type(self.permit_zone) == int and self.permit_zone >= 1 and self.permit_zone <= 6
