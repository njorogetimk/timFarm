import os
import unittest
from timsystem import app, db
from timsystem.farm.models import Farm, Users, House, Crop, Day
from timsystem.farm.models import Harvest, Condition, Activities

global farm_name, username, house_name, crop_no, day_no
farm_name = 'Kinoro'
username = 'njorogetm'
house_name = 'Alpha'
crop_no = '1-B1'
day_no = '1. June, 13'


class TestModels(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(
                                                self.basedir, 'data.sqlite')
        app.config['TESTING'] = True
        self.app = app.test_client()
        db.create_all()

    def anahilate(self):
        os.remove(os.path.join(self.basedir, 'data.sqlite'))

    def _insertFarm(self, farm_name, farm_email):
        farm = Farm(farm_name, farm_email)
        db.session.add(farm)
        db.session.commit()

    def _insertUser(self, name, username, email, password, farm_name, level):
        user = Users(name, username, email, password, farm_name, level)
        db.session.add(user)
        db.session.commit()

    def _insertHouse(self, farm_name, house_name):
        house = House(farm_name, house_name)
        db.session.add(house)
        db.session.commit()

    def _insertCrop(self, house_name, crop_name, crop_no, start_date):
        crop = Crop(house_name, crop_name, crop_no, start_date)
        db.session.add(crop)
        db.session.commit()

    def _insertDay(self, crop_no, day_no, date):
        day = Day(crop_no, day_no, date)
        db.session.add(day)
        db.session.commit()

    def _insertHarvest(self, day_no, punnets, chronicler):
        harv = Harvest(day_no, punnets, chronicler)
        db.session.add(harv)
        db.session.commit()

    def _insertCondition(self, day_no, temperature, humidity, chronicler):
        condt = Condition(day_no, temperature, humidity, chronicler)
        db.session.add(condt)
        db.session.commit()

    def _insertActivities(self, day_no, description, chronicler):
        actv = Activities(day_no, description, chronicler)
        db.session.add(actv)
        db.session.commit()

    def test_1farm(self):
        # app.logger.info('test 1')
        self._insertFarm(farm_name, '1@3d')
        farm = Farm.query.filter_by(farm_name=farm_name).first()
        self.assertFalse(not farm)

    def test_2user(self):
        password = '123'
        name = 'Timothy'
        email = 'njorogetm@gmail.com'
        level = 'Admin'
        self._insertUser(name, username, email, password, farm_name, level)
        farm = Farm.query.filter_by(farm_name=farm_name).first()
        user = farm.users.filter_by(username=username).first()
        trf = user.authenticate('123')
        self.assertTrue(trf)

    def test_3house(self):
        self._insertHouse(farm_name, house_name)
        farm = Farm.query.filter_by(farm_name=farm_name).first()
        house = farm.house.filter_by(house_name=house_name).first()
        self.assertTrue(house)

    def test_4crop(self):
        self._insertCrop(house_name, 'Button', crop_no, 'June, 13')
        farm = Farm.query.filter_by(farm_name=farm_name).first()
        house = farm.house.filter_by(house_name=house_name).first()
        crop = house.crop.filter_by(crop_no=crop_no).first()
        self.assertTrue(crop)

    def test_5day(self):
        self._insertDay(crop_no, day_no, 'June 13')
        farm = Farm.query.filter_by(farm_name=farm_name).first()
        house = farm.house.filter_by(house_name=house_name).first()
        crop = house.crop.filter_by(crop_no=crop_no).first()
        day = crop.day.filter_by(day_no=day_no).first()
        self.assertTrue(day)

    def test_6activity(self):
        self._insertActivities(day_no, 'Just testing', username)
        farm = Farm.query.filter_by(farm_name=farm_name).first()
        house = farm.house.filter_by(house_name=house_name).first()
        crop = house.crop.filter_by(crop_no=crop_no).first()
        day = crop.day.filter_by(day_no=day_no).first()
        actv = day.activities.all()
        self.assertTrue(actv)

    def test_7harvest(self):
        self._insertHarvest(day_no, '123', username)
        farm = Farm.query.filter_by(farm_name=farm_name).first()
        house = farm.house.filter_by(house_name=house_name).first()
        crop = house.crop.filter_by(crop_no=crop_no).first()
        day = crop.day.filter_by(day_no=day_no).first()
        harv = day.harvest.all()
        self.assertTrue(harv)

    def test_8condition(self):
        self._insertCondition(day_no, '32', '23', username)
        farm = Farm.query.filter_by(farm_name=farm_name).first()
        house = farm.house.filter_by(house_name=house_name).first()
        crop = house.crop.filter_by(crop_no=crop_no).first()
        day = crop.day.filter_by(day_no=day_no).first()
        condt = day.condition.all()
        self.assertTrue(condt)
        self.anahilate()


if __name__ == '__main__':
    unittest.main()
