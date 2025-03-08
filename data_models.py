from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from sqlalchemy import ForeignKey


""" SQLAlchemy() creates a db object. 
From this object we will be able to create tables with a model 'parent class' (db.Model) """
db = SQLAlchemy()

class Book(db.Model):
    """  Each instance BkUp of mapped_column() generate a Column object """
    book_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    book_title: Mapped[str] = mapped_column(nullable=False)
    isbn: Mapped[str]
    publication_year: Mapped[str]
    detail: Mapped[str]

    author_id: Mapped[int] = mapped_column(ForeignKey("author.author_id"))
    author: Mapped["Author"] = db.relationship(back_populates="book")


    def __repr__(self):
        return f"<Author(author_id={self.author_id}, name='{self.name}')>"

    def __str__(self):
        return f"Author: {self.name} (ID: {self.author_id})"

class Author(db.Model):
    """  Each instance BkUp of mapped_column() generate a Column object """
    author_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    author_name: Mapped[str] = mapped_column(nullable=False)
    birth_date: Mapped[str]
    date_of_death: Mapped[str]
    book: Mapped[List["Book"]] = db.relationship(back_populates="author")

    def __repr__(self):
        return f"<Book(book_id={self.book_id}, title='{self.title}', author_id={self.author_id})>"

    def __str__(self):
        return f"Book: {self.title} by {self.author.name if self.author else 'Unknown Author'}"
