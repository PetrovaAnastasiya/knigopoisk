# -*- coding: utf-8 -*-
import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, SelectMultipleField, RadioField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
from app.models import User, Book, Author, Genre, Publisher, Edition


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Адрес электронной почты', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Подтверждение пароля', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегестрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста, используйте другое имя пользователя.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Пожалуйста, используйте другой адрес электронной почты .')


class EditProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=140)])
    submit = SubmitField('Подтвердить')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Пожалуйста, используйте другое имя пользователя.')


class AddAuthorForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    image = TextAreaField('Ссылка на изображение', validators=[Length(min=0, max=255)])
    date_birth = DateField('Дата рождения', validators=[DataRequired()])
    date_death = DateField('Дата смерти', validators=[Optional()])
    country = StringField('Страна', validators=[DataRequired()])
    books = SelectMultipleField('Книги')
    submit = SubmitField('Отправить')

    def __init__(self, *args, **kwargs):
        super(AddAuthorForm, self).__init__(*args, **kwargs)
        self.books.choices = [(str(s.ISBN), s.title) for s in (
            Book.query.all())]
        self.books.id = "books-select"

    def validate_name(self, name):
        author = Author.query.filter_by(name=name.data).first()
        if author is not None:
            raise ValidationError('Такой автор уже существует!')


class EditAuthorForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    image = TextAreaField('Ссылка на изображение', validators=[Length(min=0, max=255)])
    date_birth = DateField('Дата рождения', validators=[DataRequired()])
    date_death = DateField('Дата смерти', validators=[Optional()])
    country = StringField('Страна', validators=[DataRequired()])
    books = SelectMultipleField('Книги')

    submit = SubmitField('Подтвердить')

    def __init__(self, original_name, *args, **kwargs):
        super(EditAuthorForm, self).__init__(*args, **kwargs)
        self.original_name = original_name
        self.books.choices = [(str(s.ISBN), s.title) for s in (
            Book.query.all())]
        self.books.id = "books-select"

    def validate_name(self, name):
        if name.data != self.original_name:
            author = Author.query.filter_by(name=self.name.data).first()
            if author is not None:
                raise ValidationError('Такой автор уже существует!')


class AddBookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    image = TextAreaField('Ссылка на изображение', validators=[Length(min=0, max=255)])
    description = TextAreaField('Описание', validators=[Length(min=0, max=560)])
    authors = SelectMultipleField('Автор(ы)')
    genres = SelectMultipleField('Жанр(ы)')
    edition = SelectMultipleField('Издание')
    submit = SubmitField('Отправить')

    def __init__(self, *args, **kwargs):
        super(AddBookForm, self).__init__(*args, **kwargs)
        self.authors.choices = [(s.name, s.name) for s in (
            Author.query.all())]
        self.genres.choices = [(s.name, s.name) for s in (
            Genre.query.all())]
        self.edition.choices = [(str(s.id), str(s.publisher.name) + ' ' + str(s.year)) for s in (
            Edition.query.filter(Edition.book_ISBN.is_(None)).all())]
        self.authors.id = "authors-select"
        self.genres.id = "genres-select"
        self.edition.id = "edition-select"


class EditBookForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    image = TextAreaField('Ссылка на изображение', validators=[Length(min=0, max=255)])
    description = TextAreaField('Описание', validators=[Length(min=0, max=560)])
    authors = SelectMultipleField('Автор(ы)')
    genres = SelectMultipleField('Жанр(ы)')
    edition = SelectMultipleField('Издание')
    submit = SubmitField('Подтвердить')

    def __init__(self, *args, **kwargs):
        super(EditBookForm, self).__init__(*args, **kwargs)
        self.authors.choices = [(s.name, s.name) for s in (
            Author.query.all())]
        self.genres.choices = [(s.name, s.name) for s in (
            Genre.query.all())]
        self.edition.choices = [(str(s.id), str(s.publisher.name) + ' ' + str(s.year)) for s in (
            Edition.query.filter(Edition.book_ISBN.is_(None)).all())]
        self.authors.id = "authors-select"
        self.genres.id = "genres-select"
        self.edition.id = "edition-select"


class AddGenreForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Отправить')

    def validate_name(self, name):
        genre = Genre.query.filter_by(name=name.data).first()
        if genre is not None:
            raise ValidationError('Такой жанр уже существует!')


class EditGenreForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')

    def __init__(self, original_name, *args, **kwargs):
        super(EditGenreForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            genre = Genre.query.filter_by(name=self.name.data).first()
            if genre is not None:
                raise ValidationError('Такой жанр уже существует!')


class AddFeedbackForm(FlaskForm):
    body = TextAreaField('Оставить свой отзыв', validators=[DataRequired(), Length(min=0, max=560)])
    rate = RadioField('Оценка', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    submit = SubmitField('Отправить')


class AddPublisherForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    URL = StringField('URL-адрес')
    address = StringField('Адрес', validators=[DataRequired()])
    phone = StringField('Номер телефона', validators=[DataRequired()])
    submit = SubmitField('Отправить')

    def validate_name(self, name):
        publisher = Publisher.query.filter_by(name=name.data).first()
        if publisher is not None:
            raise ValidationError('Такое издательство уже существует!')

    def validate_URL(self, URL):
        if URL.data != '':
            result = re.match('((https?):\/\/)?(www.)?[a-z0-9]+\.[a-z]+(\/[a-zA-Z0-9#]+\/?)*', URL.data)
            if result is None:
                raise ValidationError('Неверный URL-адрес')

    def validate_phone(self, phone):
        result = re.match('((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}', phone.data)
        if result is None:
            raise ValidationError('Неверный номер телефона')


class EditPublisherForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    URL = StringField('URL-адрес')
    address = StringField('Адрес', validators=[DataRequired()])
    phone = StringField('Номер телефона', validators=[DataRequired()])
    submit = SubmitField('Подтвердить')

    def __init__(self, original_name, *args, **kwargs):
        super(EditPublisherForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            publisher = Publisher.query.filter_by(name=self.name.data).first()
            if publisher is not None:
                raise ValidationError('Такое издательство уже существует!')

    def validate_URL(self, URL):
        if URL.data != '':
            result = re.match('^((https?):\/\/)?(www.)?[a-z0-9]+\.[a-z]+(\/[a-zA-Z0-9#]+\/?)*$', URL.data)
            if result is None:
                raise ValidationError('Неверный URL-адрес')

    def validate_phone(self, phone):
        result = re.match('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$', phone.data)
        if result is None:
            raise ValidationError('Неверный номер телефона')


class EditionForm(FlaskForm):
    language = StringField('Язык', validators=[DataRequired()])
    year = StringField('Год выпуска', validators=[DataRequired()])
    publisher = SelectField('Издательство', validators=[DataRequired()])
    submit = SubmitField('Отправить')

    def __init__(self, *args, **kwargs):
        super(EditionForm, self).__init__(*args, **kwargs)
        self.publisher.choices = [(str(s.id), s.name) for s in (
            Publisher.query.all())]

    def validate_year(self, year):
        result = re.match('^\d{4}$', year.data)
        if result is None:
            raise ValidationError('Неверный формат года')

class SearchForm(FlaskForm):
    body = StringField('Поиск', validators=[DataRequired()], render_kw={"placeholder": "Поиск", "type": "text",
                                                                        "class": "search-query form-control"})
    submit = SubmitField('Отправить')
