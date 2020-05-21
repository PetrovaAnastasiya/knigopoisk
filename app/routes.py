# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EditAuthorForm, AddAuthorForm, EditBookForm, \
    AddBookForm, AddGenreForm, EditGenreForm, AddFeedbackForm, AddPublisherForm, EditPublisherForm, EditionForm, SearchForm
from app.models import User, Book, Author, Genre, Feedback, Publisher, Edition

@app.route('/')
@app.route('/index')
def index():
    top_authors = Author.query.order_by(Author.author_rate.desc()).limit(4)
    top_books = Book.query.order_by(Book.book_rate.desc()).limit(4)
    if current_user.is_authenticated:
        fav_books = current_user.favourite_books().all()
        return render_template('index.html', title='Главная страница', fav_books=fav_books, top_authors=top_authors, top_books=top_books)
    return render_template('index.html', title='Главная страница', top_authors=top_authors, top_books=top_books)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверное имя пользователя или пароль!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем, вы успешно зарегестрировались!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    return render_template('user.html', user=user, title=username)


@app.route('/add_admin/<username>')
@login_required
def add_admin(username):
    if current_user.type == 0:
        return redirect(url_for('index'))
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Пользователь {} не найден.'.format(username))
        return redirect(url_for('index'))
    user.type = 1
    db.session.commit()
    flash('Вы добавили {} в список администраторов!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/remove_admin/<username>')
@login_required
def remove_admin(username):
    if current_user.type == 0:
        return redirect(url_for('index'))
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Пользователь {} не найден.'.format(username))
        return redirect(url_for('index'))
    user.type = 0
    db.session.commit()
    flash('Вы удалили {} из списка администраторов!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/admin_panel')
@login_required
def admin_panel():
    if current_user.type == 0:
        return redirect(url_for('index'))

    return render_template('admin_panel.html', title='Панель администрирования')


@app.route('/add_author', methods=['GET', 'POST'])
@login_required
def add_author():
    if current_user.type == 0:
        return redirect(url_for('index'))
    form = AddAuthorForm()
    if form.validate_on_submit():
        author = Author(name=form.name.data, date_birth=form.date_birth.data, date_death=form.date_death.data,
                        country=form.country.data, image=form.image.data)
        db.session.add(author)

        curr_books = form.books.data
        for ISBN in curr_books:
            curr = Book.query.filter_by(ISBN=int(ISBN)).first()
            author.books.append(curr)

        db.session.commit()
        flash('Автор успешно добавлен!')
        return redirect(url_for('authors'))
    return render_template('add_author.html', title='Добавление автора', form=form)


@app.route('/edit_author/<name>', methods=['GET', 'POST'])
@login_required
def edit_author(name):
    if current_user.type == 0:
        return redirect(url_for('index'))
    author = Author.query.filter_by(name=name).first_or_404()
    form = EditAuthorForm(author.name)
    if form.validate_on_submit():
        author.name = form.name.data
        author.image = form.image.data
        author.date_birth = form.date_birth.data
        author.date_death = form.date_death.data
        author.country = form.country.data

        for book in author.books.all():
            author.books.remove(book)

        curr_books = form.books.data
        for ISBN in curr_books:
            curr = Book.query.filter_by(ISBN=int(ISBN)).first()
            if curr not in author.books.all():
                author.books.append(curr)

        db.session.commit()
        flash('Изменения сохранены!')
        return redirect(url_for('author', name=form.name.data))
    elif request.method == 'GET':
        form.name.data = author.name
        form.image.data = author.image
        form.date_birth.data = author.date_birth
        form.date_death.data = author.date_death
        form.country.data = author.country

        list = []
        for book in author.books.all():
            ISBN = book.ISBN
            list.append(str(ISBN))
        form.books.data = list

    return render_template('edit_author.html', title='Редактирование автора', form=form)


@app.route('/delete_author/<name>')
@login_required
def delete_author(name):
    if current_user.type == 0:
        return redirect(url_for('index'))
    author = Author.query.filter_by(name=name).first()
    if author is None:
        flash('Автор не найден.')
        return redirect(url_for('index'))
    db.session.delete(author)
    db.session.commit()
    flash('Вы удалили автора!')
    return redirect(url_for('authors'))


@app.route('/authors')
def authors():
    authors = Author.query.order_by(Author.name).all()
    return render_template('authors.html', title='Авторы', authors=authors)


@app.route('/author/<name>')
def author(name):
    author = Author.query.filter_by(name=name).first_or_404()

    return render_template('author.html', author=author, title=name)


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if current_user.type == 0:
        return redirect(url_for('index'))
    form = AddBookForm()
    if form.validate_on_submit():
        book = Book(title=form.title.data, description=form.description.data, image=form.image.data)
        db.session.add(book)

        curr_authors = form.authors.data
        for name in curr_authors:
            curr = Author.query.filter_by(name=name).first()
            book.authors.append(curr)

        curr_genres = form.genres.data
        for name in curr_genres:
            curr = Genre.query.filter_by(name=name).first()
            book.genres.append(curr)

        curr_edition = form.edition.data
        for id in curr_edition:
            curr = Edition.query.filter_by(id=int(id)).first()
            if curr not in book.edition.all():
                book.edition.append(curr)

        db.session.commit()
        flash('Книга успешно добавлена!')
        return redirect(url_for('books'))
    return render_template('add_book.html', title='Добавление книги', form=form)



@app.route('/edit_book/<ISBN>', methods=['GET', 'POST'])
@login_required
def edit_book(ISBN):
    if current_user.type == 0:
        return redirect(url_for('index'))
    book = Book.query.filter_by(ISBN=ISBN).first_or_404()
    form = EditBookForm()
    if form.validate_on_submit():
        book.title = form.title.data
        book.image = form.image.data
        book.description = form.description.data

        for author in book.authors.all():
            book.authors.remove(author)

        for genre in book.genres.all():
            book.genres.remove(genre)

        for edition in book.edition.all():
            book.edition.remove(edition)

        curr_authors = form.authors.data
        for name in curr_authors:
            curr = Author.query.filter_by(name=name).first()
            if curr not in book.authors.all():
                book.authors.append(curr)

        curr_genres = form.genres.data
        for name in curr_genres:
            curr = Genre.query.filter_by(name=name).first()
            if curr not in book.genres.all():
                book.genres.append(curr)

        curr_edition = form.edition.data
        for id in curr_edition:
            curr = Edition.query.filter_by(id=int(id)).first()
            if curr not in book.edition.all():
                book.edition.append(curr)

        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('book', ISBN=book.ISBN))
    elif request.method == 'GET':
        form.title.data = book.title
        form.image.data = book.image
        form.description.data = book.description

        au_list = []
        for author in book.authors.all():
            author = author.name
            au_list.append(author)
        form.authors.data = au_list

        gen_list = []
        for genre in book.genres.all():
            genre = genre.name
            gen_list.append(genre)
        form.genres.data = gen_list

        ed_list = []
        for edition in book.edition.all():
            edition = edition.id
            ed_list.append(str(edition))
        form.edition.data = ed_list
    return render_template('edit_book.html', title='Редактирование книги', form=form)


@app.route('/delete_book/<ISBN>')
@login_required
def delete_book(ISBN):
    if current_user.type == 0:
        return redirect(url_for('index'))
    book = Book.query.filter_by(ISBN=ISBN).first()
    if book is None:
        flash('Книга не найдена.')
        return redirect(url_for('index'))
    db.session.delete(book)
    db.session.commit()
    flash('Вы удалили книгу!')
    return redirect(url_for('books'))


@app.route('/books')
def books():
    books = Book.query.order_by(Book.title).all()
    return render_template('books.html', title='Книги', books=books)


@app.route('/book/<ISBN>', methods=['GET', 'POST'])
def book(ISBN):
    book = Book.query.filter_by(ISBN=ISBN).first_or_404()
    form = AddFeedbackForm()

    if form.validate_on_submit():
        body = form.body.data
        rate = form.rate.data
        feedback = Feedback(body=body, rate=rate, author=current_user, book_title_reserved=book.title)
        book.feedback.append(feedback)
        db.session.commit()
        flash('Отзыв успешно добавлен!')
        form.body.data = ''
        form.rate.data = None

    return render_template('book.html', book=book, ISBN=ISBN, form=form)


@app.route('/remove_feedback/<id>')
@login_required
def remove_feedback(id):
    if current_user.type == 0:
        return redirect(url_for('index'))
    feedback = Feedback.query.filter_by(id=id).first()
    if feedback is None:
        flash('Отзыв не найден.')
        return redirect(url_for('index'))
    db.session.delete(feedback)
    db.session.commit()
    flash('Вы удалили отзыв!')
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')
    return redirect(next_page)


@app.route('/add_favourite/<ISBN>')
@login_required
def add_favourite(ISBN):
    book = Book.query.filter_by(ISBN=ISBN).first()
    if book is None:
        flash('Книга {} не найдена.'.format(book.title))
        return redirect(url_for('index'))
    current_user.add_favourite(book)
    db.session.commit()
    flash('Вы добавили {} в избранное!'.format(book.title))
    return redirect(url_for('book', ISBN=ISBN))


@app.route('/remove_favourite/<ISBN>')
@login_required
def remove_favourite(ISBN):
    book = Book.query.filter_by(ISBN=ISBN).first()
    if book is None:
        flash('Книга {} не найдена.'.format(book.title))
        return redirect(url_for('index'))
    current_user.remove_favourite(book)
    db.session.commit()
    flash('Вы удалили {} из избранного.'.format(book.title))
    return redirect(url_for('book', ISBN=ISBN))


@app.route('/add_genre', methods=['GET', 'POST'])
@login_required
def add_genre():
    if current_user.type == 0:
        return redirect(url_for('index'))
    form = AddGenreForm()
    if form.validate_on_submit():
        genre = Genre(name=form.name.data)
        db.session.add(genre)
        db.session.commit()
        flash('Жанр успешно добавлен!')
        return redirect(url_for('genres'))
    return render_template('add_genre.html', title='Добавление жанра', form=form)


@app.route('/edit_genre/<name>', methods=['GET', 'POST'])
@login_required
def edit_genre(name):
    if current_user.type == 0:
        return redirect(url_for('index'))
    genre = Genre.query.filter_by(name=name).first_or_404()
    form = EditGenreForm(genre.name)
    if form.validate_on_submit():
        genre.name = form.name.data
        db.session.commit()
        flash('Изменения сохранены!')
        return redirect(url_for('genre', name=form.name.data))
    elif request.method == 'GET':
        form.name.data = genre.name
    return render_template('edit_genre.html', title='Редактирование жанра', form=form)


@app.route('/delete_genre/<name>')
@login_required
def delete_genre(name):
    if current_user.type == 0:
        return redirect(url_for('index'))
    genre = Genre.query.filter_by(name=name).first()
    if genre is None:
        flash('Жанр не найден.')
        return redirect(url_for('index'))
    db.session.delete(genre)
    db.session.commit()
    flash('Вы удалили жанр!')
    return redirect(url_for('genres'))


@app.route('/genres')
def genres():
    genres = Genre.query.order_by(Genre.name).all()
    return render_template('genres.html', title='Жанры', genres=genres)


@app.route('/genre/<name>')
def genre(name):
    genre = Genre.query.filter_by(name=name).first_or_404()
    return render_template('genre.html', genre=genre, name=name)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Изменения сохранены!')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Редактирование профиля', form=form)


@app.route('/add_publisher', methods=['GET', 'POST'])
@login_required
def add_publisher():
    if current_user.type == 0:
        return redirect(url_for('index'))
    form = AddPublisherForm()
    if form.validate_on_submit():
        publisher = Publisher(name=form.name.data, URL=form.URL.data, address=form.address.data,
                        phone=form.phone.data)
        db.session.add(publisher)
        db.session.commit()
        flash('Издательство успешно добавлено!')
        return redirect(url_for('publishers'))
    return render_template('add_publisher.html', title='Добавление издательства', form=form)


@app.route('/edit_publisher/<name>', methods=['GET', 'POST'])
@login_required
def edit_publisher(name):
    if current_user.type == 0:
        return redirect(url_for('index'))
    publisher = Publisher.query.filter_by(name=name).first_or_404()
    form = EditPublisherForm(publisher.name)
    if form.validate_on_submit():
        publisher.name = form.name.data
        publisher.URL = form.URL.data
        publisher.address = form.address.data
        publisher.phone = form.phone.data

        db.session.commit()
        flash('Изменения сохранены!')
        return redirect(url_for('publisher', name=publisher.name))
    elif request.method == 'GET':
        form.name.data = publisher.name
        form.URL.data = publisher.URL
        form.address.data = publisher.address
        form.phone.data = publisher.phone
    return render_template('edit_publisher.html', title='Редактирование издательства', form=form)


@app.route('/delete_publisher/<name>')
@login_required
def delete_publisher(name):
    if current_user.type == 0:
        return redirect(url_for('index'))
    publisher = Publisher.query.filter_by(name=name).first()
    if publisher is None:
        flash('Издатель не найден.')
        return redirect(url_for('index'))
    db.session.delete(publisher)
    db.session.commit()
    flash('Вы удалили издательство!')
    return redirect(url_for('publishers'))


@app.route('/publishers')
def publishers():
    publishers = Publisher.query.order_by(Publisher.name).all()
    return render_template('publishers.html', title='Издательства', publishers=publishers)


@app.route('/publisher/<name>')
def publisher(name):
    publisher = Publisher.query.filter_by(name=name).first_or_404()

    return render_template('publisher.html', publisher=publisher, title=name)


@app.route('/add_edition', methods=['GET', 'POST'])
@login_required
def add_edition():
    if current_user.type == 0:
        return redirect(url_for('index'))
    form = EditionForm()
    if form.validate_on_submit():
        edition = Edition(language=form.language.data, year=form.year.data, publisher_id=form.publisher.data)

        db.session.add(edition)
        db.session.commit()
        flash('Издание успешно добавлено!')
        return redirect(url_for('editions'))
    return render_template('add_edition.html', title='Добавление издания', form=form)


@app.route('/edit_edition/<id>', methods=['GET', 'POST'])
@login_required
def edit_edition(id):
    if current_user.type == 0:
        return redirect(url_for('index'))
    edition = Edition.query.filter_by(id=id).first_or_404()
    form = EditionForm()
    if form.validate_on_submit():
        edition.language = form.language.data
        edition.year = form.year.data
        edition.publisher_id = form.publisher.data
        db.session.commit()
        flash('Изменения сохранены!')
        return redirect(url_for('edition', id=edition.id))
    elif request.method == 'GET':
        form.language.data = edition.language
        form.year.data = edition.year
        form.publisher.data = str(edition.publisher_id)
    return render_template('edit_edition.html', title='Редактирование издательства', form=form)


@app.route('/delete_edition/<id>')
@login_required
def delete_edition(id):
    if current_user.type == 0:
        return redirect(url_for('index'))
    edition = Edition.query.filter_by(id=id).first()
    if edition is None:
        flash('Издание не найдено.')
        return redirect(url_for('index'))
    db.session.delete(edition)
    db.session.commit()
    flash('Вы удалили издание!')
    return redirect(url_for('editions'))


@app.route('/editions')
@login_required
def editions():
    if current_user.type == 0:
        return redirect(url_for('index'))

    editions = Edition.query.all()
    return render_template('editions.html', title='Издания', editions=editions)


@app.route('/edition/<id>')
@login_required
def edition(id):
    if current_user.type == 0:
        return redirect(url_for('index'))

    edition = Edition.query.filter_by(id=id).first_or_404()

    return render_template('edition.html', edition=edition, title=(str(edition.publisher.name)+' '+str(edition.year)))

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        text = form.body.data

        book_result = Book.query.filter(Book.title.ilike('%'+text+'%')).all()
        author_result = Author.query.filter(Author.name.ilike('%'+text+'%')).all()
        genre_result = Genre.query.filter(Genre.name.ilike('%'+text+'%')).all()
        publisher_result = Publisher.query.filter(Publisher.name.ilike('%'+text+'%')).all()

        return render_template('search.html', title="Поиск", form=form, book_result=book_result, author_result=author_result,
                               genre_result=genre_result, publisher_result=publisher_result)
    elif request.method == "GET":
        return render_template('search.html', title="Поиск", form=form)
