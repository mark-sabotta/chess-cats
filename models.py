"""SQLAlchemy models for ChessCats."""

from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import requests
from constants import PLAYER_URL, PLAYERS, REQUEST_HEADER, CHESS_BLITZ, \
    LAST, RATING, URL


bcrypt = Bcrypt()
db = SQLAlchemy()


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
    def get_or_update_opponent(cls, username):
        """Looks for opponent in database. If found updates rating, timestamp.
        If opponent not found, creates and adds opponent"""

        profile = requests.get(f"{PLAYER_URL}{username}", 
            headers=REQUEST_HEADER).json()
        info = requests.get(f"{PLAYER_URL}{username}/stats",
            headers=REQUEST_HEADER).json()

        #Not all players have a blitz rating
        if CHESS_BLITZ not in info:
            return 'none'

        found_rating = info[CHESS_BLITZ][LAST][RATING]

        #This scopes the opponent variable so it can be accessed later
        opponent = 'none' 

        if not cls.query.filter_by(username=username).first():
            opponent = Opponent(
                username=username,
                url=profile[URL],
                rating=found_rating
            )

            db.session.add(opponent)
        else:
            opponent = cls.query.filter_by(username=username).first()
            opponent.rating = found_rating
            opponent.timestamp = datetime.utcnow()

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

    opponent = db.relationship("Opponent")

    strength = db.Column(
        db.Integer,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )
    @classmethod
    def match_opponent(cls, db, user_id, opponent_id, strength):
        
        match = User_Opponent.query.filter_by(user_id=user_id,
            strength=strength).first()


        if match:
            match.opponent_id = opponent_id
        else:
            match = User_Opponent(
                user_id = user_id,
                opponent_id = opponent_id,
                strength = strength,
                timestamp = datetime.utcnow(),
            )
            db.session.add(match)

        db.session.commit()
        return match

    @classmethod
    def list_opponents(cls, user):
        return cls.query.filter_by(user_id = user.id)

    @classmethod
    def get_user_opponent(cls, db, user_id, strength):
        query = cls.query.filter_by(user_id = user_id).filter_by(strength=strength)
        results = db.session.execute(query)
        list = []
        for res in results:
            list.append(res[0])
        return list




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
    opponent = db.relationship('Opponent')
    user = db.relationship('User')

    @classmethod
    def list_victories(cls, user):
        return cls.query.filter_by(user_id = user.id)

    @classmethod
    def add_user_victory(cls, user_id, opponent_id, strength):
        victory = User_Victory(
            user_id = user_id,
            opponent_id = opponent_id,
            strength = strength
        )

        db.session.add(victory)
        return victory



def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

