from datetime import datetime
import requests
from sqlalchemy import update
from wtforms import validators
from random import sample
from models import User, Opponent, User_Opponent

player_url = "https://api.chess.com/pub/player/"
bulk_url = "https://api.chess.com/pub/us"
request_header = {'User-Agent': 'mark.sabotta@gmail.com'}

#Should this be in forms.py?
#######Custom Validators for add-user form########
def on_chess_com_validator(form, field):
    """Checks if the username is on chess.com"""
    query_username = field.data.lower()
    response = requests.head(f"{player_url}{query_username}", headers=request_header)
    if response.status_code != 200:
        raise validators.ValidationError('User Not Found')

def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise validators.ValidationError('Username already in use.')


#######User and Opponent API call functions######
def bulk_pull_users():
    """Requests and returns 10000 users"""
    response = requests.get(bulk_url, headers = request_header)
    return response.json()

def add_opponents_to_table(list):
    """Samples 30 from list, checks if already in table, 
    then updates/adds opponents in sample to table"""

    working_list = sample(list, 30)
    for opp in working_list:
        if Opponent.query.get(opp):
            stats = requests.get(f"{player_url}{opp}/stats", headers = request_header)
            update(Opponent).where(username=opp).values(rating=stats.json()['chess_blitz']['last']['rating'],
                                                        timestamp=datetime.utcnow())
        else:
            Opponent.get_opponent(opp)

def swap(list, a, b):
    c = list[a]
    list[a] = list[b]
    list[b] = c


def assign_opponents_to_user(user):
    user_rating = requests.get(f"{player_url}{user}/stats", headers = request_header).json()['chess_blitz']['last']['rating']
    select(Opponent.)
