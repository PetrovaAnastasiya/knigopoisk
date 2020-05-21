# -*- coding: utf-8 -*-
from datetime import datetime
from flask_login import current_user
from app import app, db, login
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

authors = db.Table('authors',
    db.Column('author_id', db.Integer, db.ForeignKey('author.id')),
    db.Column('ISBN', db.Integer, db.ForeignKey('book.ISBN'))
)

class Book(db.Model):
    ISBN = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    description = db.Column(db.String(120))
    book_rate = db.Column(db.Float, default=0)
    image = db.Column(db.String(255))
    feedback = db.relationship('Feedback', backref='book', lazy='dynamic')
    edition = db.relationship('Edition', backref='book', lazy='dynamic')

    def __repr__(self):
        return '<Книга {}>'.format(self.title)

    def rating(self):
        rate = 0
        all_feedback = Feedback.query.filter_by(book_ISBN=self.ISBN)
        if all_feedback is not None:
            for feedback in all_feedback:
                rate += feedback.rate
        if rate == 0:
            self.book_rate = 0
        else:
            self.book_rate = (rate / all_feedback.count())
        db.session.commit()
        return "%.1f" % self.book_rate

class Edition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(30))
    year = db.Column(db.String(4))
    book_ISBN = db.Column(db.Integer, db.ForeignKey('book.ISBN'), nullable=True)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'))

    def __repr__(self):
        return '<Издание {}>'.format(self.id)

class Publisher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    URL = db.Column(db.String(200))
    address = db.Column(db.String(100))
    phone = db.Column(db.String(25))
    edition = db.relationship('Edition', backref='publisher', lazy='dynamic')

    def __repr__(self):
        return '<Издательство {}>'.format(self.name)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    date_birth = db.Column(db.Date)
    date_death = db.Column(db.Date)
    country = db.Column(db.String(64))
    author_rate = db.Column(db.Float, default=0)
    image = db.Column(db.String(255))
    books = db.relationship(
        'Book', secondary=authors,
        primaryjoin=(authors.c.author_id == id),
        secondaryjoin=(authors.c.ISBN == Book.ISBN),
        backref=db.backref('authors', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<Автор {}>'.format(self.name)

    def rating(self):
        rate = 0
        all_books = self.books.all()
        if all_books is not None:
            for book in all_books:
                rate += book.book_rate
        if rate == 0:
            self.author_rate = 0
        else:
            self.author_rate = (rate / len(all_books))
        db.session.commit()
        return "%.1f" % self.author_rate


favourites = db.Table('favourites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('ISBN', db.Integer, db.ForeignKey('book.ISBN'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    feedback = db.relationship('Feedback', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.Integer, default=0)

    favourite = db.relationship(
        'Book', secondary=favourites,
        primaryjoin=(favourites.c.user_id == id),
        secondaryjoin=(favourites.c.ISBN == Book.ISBN),
        backref=db.backref('favourited', lazy='dynamic'), lazy='dynamic')

    def add_favourite(self, book):
        if not self.is_favourite(book):
            self.favourite.append(book)

    def remove_favourite(self, book):
        if self.is_favourite(book):
            self.favourite.remove(book)

    def is_favourite(self, book):
        return self.favourite.filter(
            favourites.c.ISBN == book.ISBN).count() > 0

    def favourite_books(self):
        return Book.query.join(
            favourites, (favourites.c.ISBN == Book.ISBN)).filter(
                favourites.c.user_id == self.id).order_by(
                    Book.title)

    def __repr__(self):
        return '<Пользователь {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    rate = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    book_title_reserved = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_ISBN = db.Column(db.Integer, db.ForeignKey('book.ISBN'))

    def __repr__(self):
        return '<Отзыв {}>'.format(self.body)

genres = db.Table('genres',
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id')),
    db.Column('ISBN', db.Integer, db.ForeignKey('book.ISBN'))
)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)

    bookGenre = db.relationship(
        'Book', secondary= genres,
        primaryjoin=(genres.c.genre_id == id),
        secondaryjoin=(genres.c.ISBN == Book.ISBN),
        backref=db.backref('genres', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<Жанр {}>'.format(self.name)
