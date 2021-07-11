import unittest
from flask import current_app
from app import create_app, db


class MainViewsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)
        self.response = self.client.get('/')

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_main_view_get(self):
        self.assertEqual(self.response.status_code, 200)

    # def test_main_correct_html(self):
    #     pass