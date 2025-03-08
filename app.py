"""
    Book Alchemy is a library of favorite books that records the following information:
    From the book: title, year of publication, details, author and isbn.
    From the Author: birth and death of the author.

"""
from flask import Flask, render_template, request, session
from data_models import db, Author, Book
import os

app = Flask(__name__)

# data_folder is el Path to folder database
data_folder = os.path.join(app.root_path, 'data')
#Ppath to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(data_folder, 'library.sqlite')

""" 
    To connect the Flask app to the flask-sqlalchemy code. 
    db is an object created in data_models.py
    db.init_app(app) allows app.py to access to the database
"""
db.init_app(app)

app.config['SECRET_KEY'] = 'ihb245hb/&kjb&%h'

# with app.app_context():
#   db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    """
        Displays all registered books.
        Allows to sort the list and search by keyword.
    """
    display = ''
    
    if request.method == 'POST':
        name_column = request.form.get('order_by')
        search = request.form.get('search')
        delete = request.form.get('delete')
        show_home = request.form.get('home')

        if delete:
            display = 'flex'

        if show_home:
            display = 'None'


        if search:
            books = db.session.query('*').select_from(Book). \
                    join(Author, Book.author_id == Author.author_id). \
                    filter( (Book.book_title.like(f'%{search}%')) | (Author.author_name.like(f'%{search}%')) )
            books_length = len(books.all())

            if books_length == 0:
                msg = """
                <p><h2>No book found</h2>
                Try searching with another keyword or phrase. <br>
                Click on the <b>submit</b> or <b>Home</b>
                 button to get the full list of available books.
                </p>
                """
                session['msg'] = msg
                return render_template('home.html', books=books, books_length=books_length, msg=msg)
        else:
            books = db.session.query('*').select_from(Book). \
                join(Author, Book.author_id == Author.author_id)
            books_length = len(books.all())

        if name_column:
            books = books.order_by(name_column)
            display = 'None'
            return render_template('home.html', books=books, books_length=books_length, display=display)

        return render_template('home.html', books=books, books_length=books_length, display=display)

    books = db.session.query('*').select_from(Book). \
        join(Author, Book.author_id == Author.author_id)
    books_length = len(books.all())
    return render_template('home.html', books=books, books_length=books_length, display=None)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
        Adds an author with his/her name and the possibility to add date of birth and death.
        Gets the data from a form and saves it in a new record in the authors table.
    """
    if request.method == 'POST':
        author = request.form.get('name')
        birth = request.form.get('birthdate')
        death = request.form.get('date_of_death')


        new_author = Author(
            author_name=author,
            birth_date=birth,
            date_of_death=death
        )
        if author:
            with app.app_context():
                db.session.add(new_author)
                db.session.commit()  # commits the session to the DB.

            return render_template('author_added.html', author=author)



    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
        Adds a book. The title and author are required.
        The user has to select an author from the selection list.
        If no author is selected a modal appears with a notification.
        If the author does not exist in the list, the author must first be added from 'add author'.
        If the required fields are filled in, the function saves the new author record in the author table of the database.
    """
    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author')
        details = request.form.get('details')

        new_book = Book(
            book_title=title,
            isbn=isbn,
            publication_year=publication_year,
            author_id=author_id,
            detail=details
        )

        if not author_id:
            show_modal = 'show'
            return render_template('add_book.html', title=title, show_modal=show_modal)
        else:
            author_data = db.session.execute(db.select(Author).filter_by(author_id=author_id)).scalar_one()
            author = author_data.author_name

            if title:
                with app.app_context():
                    db.session.add(new_book)
                    db.session.commit()  # commits the session to the DB.
                return render_template('book_added.html', title=title, author=author)


    authors = Author.query.all()

    return render_template('add_book.html', authors=authors)


@app.route('/book/<int:book_id>/book_details', methods=['GET', 'POST'])
def book_detail(book_id):
    """
        Select the book by book_id. Select the author by author_id
        Renders the template passing the book and author to show the detail of the selected book.
    """
    if request.method == 'POST':

        selected_book = db.session.execute(db.select(Book).filter_by(book_id=book_id)).scalar_one()
        selected_author = db.session.execute(db.select(Author).filter_by(author_id=selected_book.author_id)).scalar_one()
        author = selected_author.author_name
        return render_template('details_book.html', book=selected_book, author=author)


@app.route('/book/<int:book_id>/delete', methods=['GET', 'POST'])
def delete_book(book_id):
    """
        Select the book to delete by book_id
        Deletes the book record from the book table in the database.
        renders book_deleted.html to confirm the deletion.
    """
    if request.method == 'POST':
        book_to_delete = db.session.execute(db.select(Book).filter_by(book_id=book_id)).scalar_one()
        try:
            record = Book.query.get(book_id)
            if record:
                db.session.delete(record)
                db.session.commit()
                return render_template('book_deleted.html', title=book_to_delete.book_title)
            else:
                return False  # Record not found
        except Exception as e:  # Handle potential errors (e.g., database issues)
            db.session.rollback()  # Important: Rollback on error
            print(f"Error deleting record: {e}")
            return False


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)