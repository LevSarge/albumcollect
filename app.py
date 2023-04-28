"""Flask server for Album Collect"""

from flask import Flask, render_template, redirect, url_for, request
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

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(25), nullable = False)
    password = db.Column(db.String(25), nullable = False)

#Album database where users will be submitting their owned albums
class Album(db.Model):
    __tablename__ = "albums"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(100))
    artist = db.Column(db.String(50))
    genre = db.Column(db.String(25))
    release_date = db.Column(db.Integer)
    album_format = db.Column(db.String(20))
    album_rating = db.Column(db.Integer)
    album_tag = db.Column(db.String(100))

#This is the object class for individual lists each user recieves whenever they signup for the website and can start catalogging their music with
class List(db.Model):
    __tablename__ = "lists"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    album_id = db.Column(db.Integer, db.ForeignKey(Album.id))
    user = db.relationship(User, backref=db.backref("lists", lazy=True))
    album = db.relationship(Album, backref=db.backref("lists", lazy=True))

with app.app_context():
    db.create_all()

#Flask forms for Data Entry

class LoginForm(FlaskForm):
    username = StringField(name = "Username", validators = [DataRequired()])
    password = PasswordField(name = "Password", validators = [DataRequired(),Length(3,20)])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired()])
    password = PasswordField("Password", validators = [DataRequired()])
    submit = SubmitField("Register")

class AlbumForm(FlaskForm):
    title = StringField(name = "Album Title", validators = [DataRequired(), Length(1, 100)])
    artist = StringField(name = "Artist", validators = [DataRequired(), Length(1, 100)])
    genre = StringField(name = "Genre", validators= [DataRequired(), Length(1, 50)])
    release_date = IntegerField(name = "Year", validators= [DataRequired()])
    album_format = SelectField(name = "Release Format", validators= [DataRequired()], choices=[('Vinyl'),('CD'),('Cassette'),('Digital')])
    album_rating = IntegerField(name = "Rating", validators= [DataRequired(), NumberRange(min = 1, max =5)])
    album_tag = TextAreaField(name="Tags", validators= [Length(max=200)])
    submit = SubmitField('Submit')

#User functions with login manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Album functions (Add, Delete and Get)

def add_album(new_album):
    a = Album(album = new_album, user_id = current_user.id)
    db.session.add(a)
    db.session.commit()

def delete_album(album):
    db.session.delete(album)
    db.session.commit()

#Website routing
@app.route('/')
def landing():
    return render_template('landing.html')

#Registering users routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("signup.html", form=form)

#Logging users in/out
@app.route('/login', methods = ["GET", "POST"])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('list', user_id=current_user.id))
    
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

#Routes for user's lists (login needs to be required)
@app.route('/list/<int:user_id>', methods=['GET'])
@login_required
def list(user_id):
    user = User.query.get(user_id)
    albums = Album.query.join(List).filter(List.user_id == user.id).all()

    return render_template('list.html', user=user, albums=albums)

#Routes for adding and deleting albums in a user's list
@app.route('/add_album', methods=['GET','POST'])
@login_required
def add_album():
    form = AlbumForm()

    if form.validate_on_submit():
        new_album = Album(
            title=form.title.data,
            artist=form.artist.data,
            genre=form.genre.data,
            release_date=form.release_date.data,
            album_format=form.album_format.data,
            album_rating=form.album_rating.data,
            album_tag=form.album_tag.data
        )

        db.session.add(new_album)
        db.session.commit()

        list_entry = List(user_id=current_user.id, album=new_album)
        db.session.add(list_entry)
        db.session.commit()

        return redirect(url_for('list', user_id=current_user.id))
    return render_template('add_album.html', form=form)

@app.route('/album/<int:album_id>', methods=['GET'])
@login_required
def album(album_id):
    album = Album.query.get(album_id)
    return render_template('album.html', album = album)

@app.route('/edit_album/<int:album_id>', methods=['GET', 'POST'])
@login_required
def edit_album(album_id):
    album = Album.query.get(album_id)
    form = AlbumForm(obj=album)
    if form.validate_on_submit():
        form.populate_obj(album)
        db.session.commit()
        return redirect(url_for('album', album_id=album_id))
    return render_template('edit_album.html', form=form, album=album)

@app.route('/album/<int:album_id>/delete', methods=['POST'])
@login_required
def delete_album(album_id):
    album = Album.query.get(album_id)
    if not album:
        return redirect(url_for('list'))
    
    list_entry = List.query.filter_by(user_id=current_user.id, album_id=album.id).first()
    if list_entry:
        db.session.delete(list_entry)
    
    db.session.delete(album)
    db.session.commit()
    print("Album deleted")

    return redirect(url_for('list', user_id=current_user.id))
    
app.run(port=5000, host="localhost", debug=True)