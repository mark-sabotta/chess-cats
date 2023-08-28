"""SQLAlchemy models for ChessCats."""

from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import requests
from random import sample

bcrypt = Bcrypt()
db = SQLAlchemy()

player_url = "https://api.chess.com/pub/player/"
bulk_url = "https://api.chess.com/pub/us"

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

    victories = db.relationship('User_Victory')

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
        print(user)
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

    opponent = db.Column(
        db.Text,
        nullable = False
    )

    pic_id = db.Column(
        db.Integer,
        nullable = False
    )

    user = db.relationship('User')


class User_Opponent(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User')

    opponent_id = db.Column(
        db.Integer,
        nullable=False,
    )

    opponent = db.Column(
        db.Text,
        nullable=False,
    )

    profile = db.Column(
        db.Text,
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )
    @classmethod
    def get_opponents(cls, user, opponent_id, opponent, timestamp):
        #request user from chess.com
        user_response = requests.get(f"{player_url}{user.username}")
        #find user rating
        user_rating = user_response.json().rating
        #pull 10000 users
        bulk_response = requests.get(bulk_url)
        #randomly sample 30
        bulk_users = bulk_response.json()
        final_thirty = sample(bulk_users, 30)
        #get 30 ratings
        player_tuples = []
        for player in final_thirty:
            player_response = requests.get(f"{player_url}{player}")
            player_rating = player_response.json().rating
            player_profile = player_response.json.url
            player_tuples.append((player, player_rating, player_profile))
        #sort by rating difference
        #player_tuples[n][1]
        player_tuples.sort(key= abs(user_rating-player_tuples[1]))
        #grab first 6
        first_six = player_tuples[0:5:1]
        #sort 6 by true rating
        first_six.sort(key=first_six[1])
        for i in range(6):
            new_opponent = User_Opponent(
                user_id = user.id,
                opponent_id = i,
                opponent = first_six[i][0],
                profile = first_six[i][2],
                timestamp = datetime.utcnow(),
            )
            db.session.add(new_opponent)
        return True


            
    @classmethod
    def reroll(cls, user, opponent_id, opponent, timestamp):
        #Has it been 12 hours?
        if (datetime.uctnow()-timestamp).total_seconds > 43200:
            #request user from chess.com
            user_response = requests.get(f"{player_url}{user.username}")
            #find user rating
            user_rating = user_response.json().rating
            #pull 10000 users
            bulk_response = requests.get(bulk_url)
            #randomly sample 30
            bulk_users = bulk_response.json()
            final_thirty = sample(bulk_users, 30)
            #get 30 ratings
            player_tuples = []
            for player in final_thirty:
                player_response = requests.get(f"{player_url}{player}")
                player_rating = player_response.json().rating
                player_profile = player_response.json().url
                player_tuples.append((player, player_rating, player_profile))
            #sort by rating difference
            #player_tuples[n][1]
            player_tuples.sort(key= abs(user_rating-player_tuples[1]))
            #grab first 6
            first_six = player_tuples[0:5:1]
            #sort 6 by true rating
            #first_six[n][1]
            first_six.sort(key=first_six[1])
            success = False
            i = 6
            while success == False:
                if first_six[opponent_id][0] != opponent:
                    User_Opponent.opponent = first_six[opponent_id][0]
                    User_Opponent.timestamp = datetime.utcnow()
                    User_Opponent.profile = first_six[opponent_id][2]
                    success = True
                else:
                    first_six[opponent_id] = player_tuples[i]
                    i += 1
            return User_Opponent.opponent
        else:
            return False




def connect_db(app):
    """Connect this database to provided Flask app.
    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

