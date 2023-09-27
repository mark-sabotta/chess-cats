import os
from flask import Flask, render_template, flash, redirect, session, g
from sqlalchemy.exc import IntegrityError
from messages import INVALID_LOGIN, USERNAME_TAKEN, LOGOUT, MUST_LOGIN, \
    GREETING
from apifunctions import bulk_pull_users, assign_opponents_to_user, \
    find_opponents, find_victories, reroll, check_victory
from forms import UserAddForm, LoginForm, ReportForm
from models import db, connect_db, User, Opponent, User_Opponent
import threading


CURR_USER_KEY = "curr_user"


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

threading.Timer(43200, bulk_pull_users).start()

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
            flash(f"{GREETING}, {user.username}!", "success")
            return redirect("/")

        flash(INVALID_LOGIN, 'danger')

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
            flash(USERNAME_TAKEN, 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash(LOGOUT, "success")
    return redirect('/login')


@app.route('/')
def show_opponents():
    """Show current and defeated opponents"""
    
    if g.user:
        opponents = find_opponents(db, g.user)
        victories = find_victories(db, g.user)

        return render_template('home.html', opponents=opponents, victories=victories)
    else:
        return render_template('home-anon.html')

@app.route('/get-opponents')
def get_opponents():
    """Request opponents from API then add them to the table"""
    if g.user:
        assign_opponents_to_user(db, g.user)
        db.session.commit()
    else:
        flash(MUST_LOGIN, 'danger')
    return redirect('/')


@app.route('/reroll/<int:strength>')
def reroll_opponent(strength):

    if g.user:
        opponents = find_opponents(db, g.user)
        if not opponents:
            return redirect("/get-opponents")
        else:
            reroll(db, g.user, opponents, strength)
            return redirect("/")

    else:
        flash(MUST_LOGIN, 'danger')


@app.route('/report/<int:strength>', methods=["GET", "POST"])
def render_report_form(strength):
    """Show the form to report the user's victory"""
    form = ReportForm()
    user = g.user
    match = User_Opponent.get_user_opponent(db, user.id, strength)
    opponent = Opponent.query.get(match[0].opponent_id)

    if form.validate_on_submit():
        year = form.year.data
        month = form.month.data
        if check_victory(strength, user, opponent, year, month):
            return redirect(f'/reroll/{strength}')
        else:
            return redirect(f'/report/{strength}')
    else:
        return render_template("report.html", form = form, opponent = opponent)
