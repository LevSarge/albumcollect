"""Flask server for Album Collect"""

from flask import Flask, render_template, redirect, url_for, request, flash, session

from database import User, Album

app = Flask(__name__)


@app.route('/')

@app.route('signup', methods=['GET'])
def signup_page():
    return render_template("signup.html")

@app.route('signup', methods=['POST'])
def process_signup():
    username = request.form["Username"]
    password = request.form["Password"]
    if User.query.filter_by(username = username).first() == None:
        u = User(username = username, password = password)
        db.session.add(u)
        db.session.commit()
        login_user(u)
        return redirect(url_for("index"))