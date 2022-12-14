"""Flask server for Album Collect"""

from flask import Flask, render_template, redirect, url_for, request, flash, session
from jinja2 import StrictUndefined
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField 
from wtforms.validators import DataRequired, Length, NumberRange
from flask_login import LoginManager, login_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
SECRET_KEY = "asdf"
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

"""Database models and model functions for Album Collect"""

#Album Collector database tables
class User(db.Model, UserMixin):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(25), nullable = False)
    password = db.Column(db.String(25), nullable = False)

class Album(db.Model):
    __tablename__ = "albums"

    album_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100))
    artist = db.Column(db.String(50))
    genre = db.Column(db.String(25))
    release_date = db.Column(db.Integer)
    album_format = db.Column(db.String(20))
    album_rating = db.Column(db.Integer)
    album_tag = db.Column(db.String(100))


class List(db.Model):
    __tablename__ = "lists"

    savedalbums_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id =db.Column(db.Integer, db.ForeignKey('users.user_id'))
    album_id = db.Column(db.Integer, db.ForeignKey('albums.album_id'))
    album_rating = db.Column(db.Integer, db.ForeignKey('albums.album_rating'))

#db.create_all()

"""Flask forms for Data Entry"""

class RegisterForm(FlaskForm):
    username = StringField(name = "Username", validators = [DataRequired(),Length(3,20)])
    password = StringField(name = "Password", validators = [DataRequired(),Length(3,20)])

class AlbumForm(FlaskForm):
    title = StringField(name = "Album Title", validators = [DataRequired(), Length(1, 100)])
    artist = StringField(name = "Artist", validators = [DataRequired(), Length(1, 100)])
    genre = StringField(name = "Genre", validators= [DataRequired(), Length(1, 50)])
    release_date = StringField(name = "Year", validators= [DataRequired(), Length(1,4)])
    album_format = StringField(name = "Release Format", validators= [DataRequired(), Length(1, 50)])
    album_rating = IntegerField(name = "Rating", validators= [DataRequired(), NumberRange(min = 1, max =5)])

def add_album(new_album):
    a = Album(album = new_album, user_id = current_user.user_id)
    db.session.add(a)
    db.session.commit()

def delete_album(album):
    db.session.delete(album)
    db.session.commit()

"""Website routing"""
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

@app.route('/login', methods = ["GET"])
@login_required
def login():
    form = RegisterForm()
    return render_template("login.html", form = form)

@app.route('/signup', methods=['GET'])
def signup_page():
    form = RegisterForm()
    return render_template("signup.html", form=form)

@app.route('/signup', methods=['POST'])
def process_signup():
    username = request.form["Username"]
    password = request.form["Password"]
    if User.query.filter_by(username = username).first() == None:
        u = User(username = username, password = password)
        db.session.add(u)
        db.session.commit()
        login_user(u)
        return redirect(url_for("login.html"))

app.run(port=5000, host="localhost")