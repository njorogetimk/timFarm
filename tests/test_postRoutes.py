import os
from timsystem import app, db
import unittest2 as unittest


class PostRoutes(unittest.TestCase):

    def setUp(self):
        self.db_file = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(
            self.db_file, 'post.sqlite')
        app.config['TESTING'] = True
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        os.remove(os.path.join(
            self.db_file, 'post.sqlite'))

    def test_home(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_registerFarm(self):
        resp = self.app.get('/register-farm')
        self.assertEqual(resp.status_code, 200)

        resp = self.app.post('/register-farm')
        self.assertEqual(resp.status_code, 200)

        data = {'farm_name': 'Kinoro', 'farm_email': 'kin@gmail.com'}
        resp = self.app.post('/register-farm', data=data)
        self.assertEqual(resp.status_code, 302)

        resp = self.app.post('/register-farm', data=data)
        self.assertEqual(resp.status_code, 200)

    def test_registerAdmin(self):
        resp = self.app.get('/register-admin/Kinoro')
        self.assertEqual(resp.status_code, 200)

        resp = self.app.post('/register-admin/Kinoro')
        self.assertEqual(resp.status_code, 200)

        self.test_registerFarm()

        data = {
            'admin_name': 'Junior', 'username': 'eaglejr',
            'admin_email': 'junior@eagle.com', 'phone_no': '1234',
            'password': '123', 'confirm': '123'
        }
        resp = self.app.post('/register-admin/Kinoro', data=data)
        self.assertEqual(resp.status_code, 302)

        resp = self.app.post('/register-admin/Kinoro', data=data)
        self.assertEqual(resp.status_code, 302)

    def test_signin(self):
        resp = self.app.get('/signin')
        self.assertEqual(resp.status_code, 200)

        self.test_registerAdmin()

        data = {
            'farm_name': 'Kinoro', 'username': 'eaglejr', 'password': '123'
        }
        resp = self.app.post('/signin', data=data)
        self.assertEqual(resp.status_code, 302)


if __name__ == '__main__':
    unittest.main()
