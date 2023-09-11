from constants import PLAYER_URL, REQUEST_HEADER
from wtforms import validators
from models import User
import requests

def on_chess_com_validator(form, field):
    """Checks if the username is on chess.com"""
    query_username = field.data.lower()
    response = requests.head(f"{PLAYER_URL}{query_username}", headers=REQUEST_HEADER)
    if response.status_code != 200:
        raise validators.ValidationError('User Not Found')

def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise validators.ValidationError('Username already in use.')