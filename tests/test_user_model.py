import unittest
from app import create_app, db
from app.models import User


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.u = User(password='cat')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        self.assertTrue(self.u.password_hash is not None)

    def test_no_password_getter(self):
        with self.assertRaises(AttributeError):
            self.u.password

    def test_password_verification(self):
        self.assertTrue(self.u.verify_password('cat'))
        self.assertFalse(self.u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u2 = User(password='cat')
        self.assertTrue(self.u.password_hash != u2.password_hash)

    def test_confirmation_token_verification(self):
        user = User(first_name='test', last_name='test', email='test@test.com', password='cat')
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        self.assertTrue(user.confirm(token))

    def test_confirmation_token_false_positive_safe(self):
        u = User(first_name='user', last_name='1', email='test@test.com', password='cat')
        u2 = User(first_name='user', last_name='1', email='test2@test.com', password='dog')
        db.session.add_all([u2, u])
        db.session.commit()
        token1 = u.generate_confirmation_token()
        self.assertFalse(u2.confirm(token1))
