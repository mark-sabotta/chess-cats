"""SQLAlchemy models for ChessCats."""

from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import requests


bcrypt = Bcrypt()
db = SQLAlchemy()
player_url = "https://api.chess.com/pub/player/"


class User(db.Model):
    """User in the system"""
    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.
        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )


        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.
        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.
        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False




class Opponent(db.Model):
    """Opponents in the system"""
    __tablename__ = 'opponents'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    url = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    @classmethod
    def get_opponent(cls, username):
        details = requests.get(f"{player_url}{username}", headers={'User-Agent': 'mark.sabotta@gmail.com'})
        profile = details.json()
        stats = requests.get(f"{player_url}{username}/stats", headers={'User-Agent': 'mark.sabotta@gmail.com'})
        ratings = stats.json()

        opponent = Opponent(
            username=username,
            url=profile['url'],
            rating=ratings['chess_blitz']['last']['rating'],
        )

        db.session.add(opponent)
        return opponent






class User_Opponent(db.Model):
    """User-opponent matchings"""
    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    opponent_id = db.Column(
        db.Integer,
        db.ForeignKey('opponents.id', ondelete='CASCADE'),
        nullable=False,
    )


    strength = db.Column(
        db.Integer,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )





class User_Victory(db.Model):
    """Recorded victories for users"""
    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    opponent_id = db.Column(
        db.Integer,
        db.ForeignKey('opponents.id', ondelete='CASCADE'),
        nullable=False,
    )

    strength = db.Column(
        db.Integer,
        nullable = False
    )

    user = db.relationship('User')



def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

