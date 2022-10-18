from flask_sqlalchemy import SQLAlchemy

"""Database models and model functions for Album Collect"""
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "User"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))

class Album(db.Model):
    __tablename__ = "Album"

    album_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100))
    artist = db.Column(db.String(50))
    genre = db.Column(db.String(25))
    release_date = db.Column(db.Integer)
    album_format = db.Column(db.String(20))
    album_tag = db.Column(db.String(100))


class List(db.Model):
    __tablename__ = "List"

    savedalbums_id = db.Column(db.Integer, auto)