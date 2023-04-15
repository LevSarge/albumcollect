"""Flask server for Album Collect"""

from flask import Flask, render_template, redirect, url_for, request, flash, session
from jinja2 import StrictUndefined
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField 
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
    username = db.Column(db.String(25), nullable = False, unique = True),
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

#Flask forms for Data Entry

class RegisterForm(FlaskForm):
    username = StringField(name = "Username", validators = [DataRequired(),Length(3,20)])
    password = PasswordField(name = "Password", validators = [DataRequired(),Length(3,20)])

    submit = SubmitField("Register")

    def validate_user(self, username):
        existing_username = User.query.filter_by(username=username.data).first()
        if existing_username:
            raise ValueError("Username already taken. Please pick a different one.")


class AlbumForm(FlaskForm):
    title = StringField(name = "Album Title", validators = [DataRequired(), Length(1, 100)])
    artist = StringField(name = "Artist", validators = [DataRequired(), Length(1, 100)])
    genre = StringField(name = "Genre", validators= [DataRequired(), Length(1, 50)])
    release_date = StringField(name = "Year", validators= [DataRequired(), Length(1,4)])
    album_format = StringField(name = "Release Format", validators= [DataRequired(), Length(1, 50)])
    album_rating = IntegerField(name = "Rating", validators= [DataRequired(), NumberRange(min = 1, max =5)])

#User functions with login manager


#Album functions (Add, Delete and Get)
def get_albums():
    a = Album()

def add_album(new_album):
    a = Album(album = new_album, user_id = current_user.user_id)
    db.session.add(a)
    db.session.commit()

def delete_album(album):
    db.session.delete(album)
    db.session.commit()

#Website routing
@app.route('/')
def landing():
    return render_template('landing.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(id=user_id).first()

@app.route('/login', methods = ["GET", "POST"])
@login_required
def login():
    form = RegisterForm()
    return render_template("login.html", form = form)

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    submit = RegisterForm()

    return render_template("signup.html", form=submit)
        

app.run(port=5000, host="localhost", debug=True)