import unittest
from app import app, db
from app.models import User, Book

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_add_favourite(self):
        u1 = User(username='john', email='john@example.com')
        b1 = Book(title='hobbit')
        db.session.add(u1)
        db.session.add(b1)
        db.session.commit()
        self.assertEqual(u1.favourite.all(), [])
        self.assertEqual(b1.favourited.all(), [])

        u1.add_favourite(b1)
        db.session.commit()
        self.assertTrue(u1.is_favourite(b1))
        self.assertEqual(u1.favourite.count(), 1)
        self.assertEqual(u1.favourite.first().title, 'hobbit')
        self.assertEqual(b1.favourited.count(), 1)
        self.assertEqual(b1.favourited.first().username, 'john')

        u1.remove_favourite(b1)
        db.session.commit()
        self.assertFalse(u1.is_favourite(b1))
        self.assertEqual(u1.favourite.count(), 0)
        self.assertEqual(b1.favourited.count(), 0)

    def test_favourite_books(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four books
        b1 = Book(title="book #1")
        b2 = Book(title="book #2")
        b3 = Book(title="book #3")
        b4 = Book(title="book #4")
        db.session.add_all([b1, b2, b3, b4])
        db.session.commit()

        # setup the favourites
        u1.add_favourite(b2)  # john favs book #2
        u1.add_favourite(b4)  # john favs book #4
        u2.add_favourite(b3)  # susan favs book #3
        u3.add_favourite(b4)  # mary favs book #4
        db.session.commit()

        # check the favourite books of each user
        f1 = u1.favourite_books().all()
        f2 = u2.favourite_books().all()
        f3 = u3.favourite_books().all()
        f4 = u4.favourite_books().all()
        self.assertEqual(f1, [b2, b4])
        self.assertEqual(f2, [b3])
        self.assertEqual(f3, [b4])
        self.assertEqual(f4, [])

if __name__ == '__main__':
    unittest.main(verbosity=2)