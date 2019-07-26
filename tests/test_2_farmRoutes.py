import os
import unittest
from timsystem import app, db
from timsystem.farm.models import Farm


class Test_FarmRoutes(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(
                                                self.basedir, 'data1.sqlite')
        app.config['TESTING'] = True
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        os.remove(os.path.join(self.basedir, 'data1.sqlite'))

    def test_home(self):
        home = self.app.get('/')
        code = home.status_code
        self.assertEqual(code, 200)

    def test_regFarm(self):
        rget = self.app.get('/register-farm')
        farm_details = {
            'farm_name': 'testing', 'farm_email': 'new@email.com'
        }
        rpost = self.app.post('/register-farm', data=farm_details)
        self.assertEqual(rget.status_code, 200)
        self.assertEqual(rpost.status_code, 302)

    def test_regAdmin(self):
        farm_details = {
            'farm_name': 'testing', 'farm_email': 'new@email.com'
        }
        rpost = self.app.post('/register-farm', data=farm_details)
        admin_details = {
            'admin_name': 'tim', 'username':'tim', 'password': '123', 'confirm': '123'
        }
        rApost = self.app.post('/register-admin/testing', data=admin_details)
        self.assertEqual(rApost.status_code, 302)
