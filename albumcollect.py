"""Flask server for Album Collect"""

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectField, TextAreaField 
from wtforms.validators import DataRequired, Length, NumberRange
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.static_folder = 'static'
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
    username = db.Column(db.String(25), nullable = False),
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
    user_id =db.Column(db.Integer, db.ForeignKey(User.user_id))
    album_id = db.Column(db.Integer, db.ForeignKey(Album.album_id))
    album_rating = db.Column(db.Integer, db.ForeignKey(Album.album_rating))

db.create_all()

#Flask forms for Data Entry

class LoginForm(FlaskForm):
    username = StringField(name = "Username", validators = [DataRequired(),Length(3,20)])
    password = PasswordField(name = "Password", validators = [DataRequired(),Length(3,20)])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField(name = "Username", validators = [DataRequired()])
    password = PasswordField(name = "Password", validators = [DataRequired()])
    submit = SubmitField("Register")


class AlbumForm(FlaskForm):
    title = StringField(name = "Album Title", validators = [DataRequired(), Length(1, 100)])
    artist = StringField(name = "Artist", validators = [DataRequired(), Length(1, 100)])
    genre = StringField(name = "Genre", validators= [DataRequired(), Length(1, 50)])
    release_year = IntegerField(name = "Year", validators= [DataRequired(), Length(1,4)])
    album_format = SelectField(name = "Release Format", validators= [DataRequired()], choices=[('Vinyl'),('CD'),('Cassette'),('Digital')])
    album_rating = IntegerField(name = "Rating", validators= [DataRequired(), NumberRange(min = 1, max =5)])
    album_tag = TextAreaField(name="Tags", validators= [Length(max=200)])
    submit = SubmitField('Submit')

#User functions with login manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(id=user_id).first()

#Album functions (Add, Delete and Get)
def get_albums():
    albums = Album.query.all()
    return [a.album for a in albums]

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

@app.route('/login', methods = ["GET"])
def login():
    form = LoginForm()
    return render_template("login.html", form = form)

@app.route('/login', methods = ["POST"])
def login_request():
    username = request.form["Username"]
    password = request.form["Password"]
    u = User.query.filter_by(username = username, password=password).first()
    if u != None:
        login_user(u)
        return redirect(url_for("list"))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        #Add user and password to User database
        db.session.add(user)
        db.session.commit()

        flash('User registered! Go login.')
        return redirect(url_for('login'))

    return render_template("signup.html", form=form)

app.run(port=5000, host="localhost", debug=True)