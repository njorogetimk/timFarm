"""
import os
import unittest2 as unittest
from timsystem import app, db


class AdminRoutes(unittest.TestCase):

    def setUp(self):
        self.dbpath = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(
            self.dbpath, 'admin.sqlite')
        app.config['TESTING'] = True
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        os.remove(os.path.join(self.dbpath, 'admin.sqlite'))

    def test_starter(self):
        farm_data = {'farm_name': 'Kinoro', 'farm_email': 'kin@gmail.com'}
        resp = self.app.post('/register-farm', data=farm_data)
        self.assertEqual(resp.status_code, 302)

        admin_data = {
            'admin_name': 'Junior', 'username': 'eaglejr',
            'admin_email': 'junior@eagle.com', 'phone_no': '1234',
            'password': '123', 'confirm': '123'
        }
        resp = self.app.post('/register-admin/Kinoro', data=admin_data)
        self.assertEqual(resp.status_code, 302)

    def test_admin_dashboard(self):
        self.test_starter()
        # If farm_name not registered
        resp = self.app.get('/not-registered/admin-dashboard')
        self.assertEqual(resp.status_code, 302)

        # If farm_name is registered
        resp = self.app.get('/Kinoro/admin-dashboard')
        self.assertEqual(resp.status_code, 200)

"""
