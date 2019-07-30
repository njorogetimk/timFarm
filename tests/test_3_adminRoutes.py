import os
import unittest
from flask_login import login_user
from timsystem import db, app
from timsystem.farm.models import Farm, Users


class Test_AdminRoutes(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(
                                                self.basedir, 'data2.sqlite')
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        os.remove(os.path.join(self.basedir, 'data2.sqlite'))
        self.app_context.pop()

    def test_AdminDash(self):
        farm = Farm('Try', 'try@gmail.com', confirmed=True, pending=False)
        db.session.add(farm)
        user = Users('try', 'try', 'try@gmail.com', '112', 'Try', 'Admin', confirmed=True)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        rget = self.app.get('/Try/admin-dashboard')
        self.assertEqual(rget.status_code, 200)
