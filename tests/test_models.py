import os
import unittest
from timsystem import app, db
from timsystem.farm.models import Farm, Users, House, Crop, Day, Level
from timsystem.farm.models import Harvest, Condition, Activities

global farm_name, username, house_name, crop_no, day_no
farm_name = 'Kinoros'
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

    def tearDown(self):
        os.remove(os.path.join(self.basedir, 'data.sqlite'))

    def test_1farm(self):
        farm = Farm('Kinoro', '1@2.3')
        db.session.add(farm)
        db.session.commit()
        created_farm = Farm.query.filter_by(farm_name='Kinoro').first()
        self.assertTrue(created_farm, msg='404, not found')

    def test_2farm(self):
        farm = Farm('Kinoros', '1@2.3')
        user = Users('tim', 'tim', 'tim@g', '123', 'Kinoros', 'Admin')
        db.session.add(user)
        db.session.add(farm)
        db.session.commit()
        created_user = Users.query.filter_by(username='tim').first()
        self.assertTrue(created_user, msg='User 404')

    def test_3house(self):
        farm = Farm('tims', '1@2.3')
        house = House('tims', 'trial1')
        db.session.add(farm)
        db.session.add(house)
        db.session.commit()
        created_house = House.query.filter_by(house_name='trial1').first()
        self.assertTrue(created_house, msg='house 404')

    def test_4crop(self):
        farm = Farm('crop', '1@2.3')
        house = House('crop', 'crop')
        db.session.add(farm)
        db.session.add(house)
        db.session.commit()
        crop = Crop('crop', 'crop', 'button', '1', '123')
        db.session.add(crop)
        db.session.commit()
        crop = Crop.query.filter_by(crop_no='1').first()
        self.assertTrue(crop, msg='crop 404')

    def test_5day(self):
        farm = Farm('day', '1@2.3')
        house = House('day', 'day')
        db.session.add(farm)
        db.session.add(house)
        db.session.commit()
        crop = Crop('day', 'day', 'button', '1', '123')
        db.session.add(crop)
        db.session.commit()
        day = Day('day', 'day', '1', '1', '123')
        db.session.add(day)
        db.session.commit()
        created_day = Day.query.filter_by(day_no='1').first()
        self.assertTrue(created_day, msg='day 404')

    def test_6harvest(self):
        farm = Farm('harv', '1@2.3')
        house = House('harv', 'harv')
        user = Users('me', 'me', '1@1', '123', 'harv', 'Admin')
        db.session.add(farm)
        db.session.add(house)
        db.session.add(user)
        db.session.commit()
        crop = Crop('harv', 'harv', 'button', '1', '123')
        db.session.add(crop)
        db.session.commit()
        day = Day('harv', 'harv', '1', '1', '123')
        db.session.add(day)
        db.session.commit()
        harvest = Harvest('harv', 'harv', '1', '1', '32', 'me')
        db.session.add(harvest)
        created_harv = Harvest.query.all()
        self.assertTrue(created_harv, msg='harvest 404')

    def test_7condition(self):
        farm = Farm('condt', '1@2.3')
        house = House('condt', 'condt')
        user = Users('me', 'me', '1@1', '123', 'condt', 'Admin')
        db.session.add(farm)
        db.session.add(house)
        db.session.add(user)
        db.session.commit()
        crop = Crop('condt', 'condt', 'button', '1', '123')
        db.session.add(crop)
        db.session.commit()
        day = Day('condt', 'condt', '1', '1', '123')
        db.session.add(day)
        db.session.commit()
        condt = Condition('condt', 'condt', '1', '1', '12', '12', '11:13', 'me')
        db.session.add(condt)
        db.session.commit()
        created_condt = Condition.query.all()
        self.assertTrue(created_condt, msg='condition 404')

    def test_8activ(self):
        farm = Farm('actv', '1@2.3')
        house = House('actv', 'actv')
        user = Users('me', 'me', '1@1', '123', 'actv', 'Admin')
        db.session.add(farm)
        db.session.add(house)
        db.session.add(user)
        db.session.commit()
        crop = Crop('actv', 'actv', 'button', '1', '123')
        db.session.add(crop)
        db.session.commit()
        day = Day('actv', 'actv', '1', '1', '123')
        db.session.add(day)
        db.session.commit()
        actv = Activities('actv', 'actv', '1', '1', 'testing', 'me')
        db.session.add(actv)
        db.session.commit()
        created_actv = Activities.query.all()
        self.assertTrue(created_actv, msg='Activities 404')


if __name__ == '__main__':
    unittest.main()
