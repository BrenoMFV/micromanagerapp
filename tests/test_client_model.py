import unittest
from app import create_app, db
from app.models import User, Client, ClientCategory

class ClientModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_client_has_soft_delete(self):
        new_category = ClientCategory(category_name="Categoria Teste")
        user = User(first_name='test', last_name='test', email='test@test.com', password='cat')
        db.session.add_all([new_category, user])
        db.session.commit()
        c = Client(name = 'Teste',
                   deleted = True,
                   category_id_fk = new_category.category_id,
                   user_id_fk = user.user_id
                )
        db.session.add(c)
        db.session.commit()
        
        query = Client.query.filter_by(name='Teste').first()
        self.assertFalse(query)
        query = Client.query.with_deleted().filter_by(name="Teste").first()
        self.assertTrue(query)
