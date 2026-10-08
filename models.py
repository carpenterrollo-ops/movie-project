from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

user_favorites = db.Table(
    'user_favorites',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.movie_id', ondelete='CASCADE'), primary_key=True)
)


class User(db.Model):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str]

    favorites: Mapped[list["Movie"]] = relationship(
        'Movie',
        secondary=user_favorites,
        back_populates='favored_by'
    )


class Movie(db.Model):
    __tablename__ = 'movies'

    movie_id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    title: Mapped[str]
    director: Mapped[str]
    year: Mapped[int] = mapped_column(db.Integer)
    poster_url: Mapped[str]

    favored_by: Mapped[list["User"]] = relationship(
        'User',
        secondary=user_favorites,
        back_populates='favorites'
    )