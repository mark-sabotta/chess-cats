import os

from flask import Flask, render_template, request, flash, redirect, session, g, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from functions import bulk_pull_users
from forms import UserAddForm, LoginForm
from models import db, connect_db, User, Opponent

CURR_USER_KEY = "curr_user"
BULK_USERS = []


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///chesscats'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

connect_db(app)
with app.app_context():
    db.create_all()

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
        
    else:
        g.user = None

def get_bulk():
    """If bulk users not found, pulls users"""
    if BULK_USERS not in session:
        session[BULK_USERS] = bulk_pull_users()

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]



@app.route('/login', methods=["GET", "POST"]) 
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to home page.
    If form not valid, present form.
    If the there already is a user with that username: flash message
    and re-present form.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("Logged out!", "success")
    return redirect('/login')


@app.route('/')
def show_opponents():
    """Show current and defeated opponents"""
    get_bulk()
    if g.user:
        return render_template('home.html')
    else:
        return render_template('home-anon.html')

#home route: pull list of active users
#           update user_rating
#           sample 30, request ratings
#           sort by abs(ratings - user_rating)
#           assign closest 6 as pieces
#           sort 6 by true rating
#           show transparent picture, challenge link, report link

#report route: present report form (selection from pieces)
#               request user games, cache
#               look for piece as white or black
#               if found, 