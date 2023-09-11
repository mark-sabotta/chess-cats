from datetime import datetime
import requests
from flask import session
from cacheout import Cache
from sqlalchemy import update, select, desc
from wtforms import validators
from random import sample
from models import User, Opponent, User_Opponent
from constants import PLAYER_URL, BULK_URL, REQUEST_HEADER, CHESS_BLITZ, LAST,\
    RATING, PLAYERS

cache = Cache()

#######User and Opponent API call functions######
@cache.memoize()
def bulk_pull_users():
    """Requests and returns 10000 users"""

    response = requests.get(BULK_URL, headers = REQUEST_HEADER)
    return response.json()[PLAYERS]



def add_opponents_to_table(list):
    """Samples 30 from list, checks if already in table, 
    then updates/adds opponents in sample to table"""

    working_list = sample(list, 30)
    for opp in working_list:
        Opponent.get_or_update_opponent(opp)



def swap(list, a, b):
    """Swaps 2 items in a list"""

    c = list[a]
    list[a] = list[b]
    list[b] = c



def assign_opponents_to_user(db, user):
    """Gets blitz rating of user then finds opponents in table"""

    user_profile = requests.get(f"{PLAYER_URL}{user.username}/stats", headers =
        REQUEST_HEADER).json()
    if CHESS_BLITZ not in user_profile:
        user_rating = 450
    else:
        user_rating = user_profile[CHESS_BLITZ][LAST][RATING]
    lower_query = select(Opponent).order_by(
        desc(Opponent.rating)).limit(3).where(Opponent.rating <= user_rating)
    lower_opponents = db.session.execute(lower_query)
    opponent_list = []
    for opponent in lower_opponents:
        opponent_list.append(opponent[0].id)
    swap(opponent_list, 0, 2)
    diff = 0
    if len(opponent_list) < 3:
        diff = 3 - len(opponent_list)
    upper_query = select(Opponent).order_by(
        Opponent.rating).limit(3 + diff).where(Opponent.rating > user_rating)
    upper_opponents = db.session.execute(upper_query)
    for opponent in upper_opponents:
        opponent_list.append(opponent[0].id)

    if len(opponent_list) < 6:
        top_six = []
        top_query = select(Opponent).order_by(
            desc(Opponent.rating)).limit(6)
        top_opponents = db.session.execute(top_query)
        for opponent in top_opponents:
            top_six.append(opponent[0].id)
        opponent_list = top_six
    
    for i in range(6):
        User_Opponent.match_opponent(db, user.id, opponent_list[i], i)

    return opponent_list