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
