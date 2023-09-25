from datetime import datetime
import requests
import threading
from flask import session, flash
from cacheout import Cache
from sqlalchemy import update, select, desc
from wtforms import validators
from random import sample
from models import User, Opponent, User_Opponent, User_Victory
from constants import PLAYER_URL, BULK_URL, REQUEST_HEADER, CHESS_BLITZ, LAST,\
    RATING, PLAYERS, WHITE, USERNAME, URL, GAMES, BLACK, RESULT

cache = Cache(ttl = 432000)
players_list = []
#######User and Opponent API call functions######
@cache.memoize()
def bulk_pull_users():
    """Requests and returns 10000 users"""

    response = requests.get_or_404(BULK_URL, headers = REQUEST_HEADER)
    player_list = response.json()[PLAYERS]
    return player_list




def add_opponents_to_table(list):
    """Samples 30 from list, checks if already in table, 
    then updates/adds opponents in sample to table"""
    
    working_list = sample(list, 30)
    for opp in working_list:
        Opponent.get_or_update_opponent(opp)



def get_lower_opponents(db, rating, count):
    """Queries the db for a number of opponents rated lower than the user"""

    lower_query = select(Opponent).order_by(
        desc(Opponent.rating)).limit(count).where(Opponent.rating <= rating)
    lower_opponents = db.session.execute(lower_query)
    opponent_list = []
    for opponent in lower_opponents:
        opponent_list.append(opponent[0].id)
    opponent_list.reverse()
    return opponent_list

def get_upper_opponents(db, rating, count, list):
    """Queries the db for a number of opponents rated higher than the user"""

    upper_query = select(Opponent).order_by(
        Opponent.rating).limit(count).where(Opponent.rating > rating)
    upper_opponents = db.session.execute(upper_query)
    
    for opponent in upper_opponents:
        list.append(opponent[0].id)
    return list

def get_user_rating(user):
    """Requests the user's rating from Chess.com. 
    If not blitz rated returns 450"""

    user_profile = requests.get(f"{PLAYER_URL}{user.username}/stats", headers =
        REQUEST_HEADER).json()
    user_rating = 450
    if CHESS_BLITZ in user_profile:
        user_rating = user_profile[CHESS_BLITZ][LAST][RATING]
    
    return user_rating

def generate_opponent_list(db, user, count):
    """Combines lower and higher rated opponent lists to ensure 6 results"""

    user_rating = get_user_rating(user)
    opponent_list = get_lower_opponents(db, user_rating, 3)
    #If there are not enough opponents lower rated, diff will ensure we still get 6 total
    diff = 0
    if opponent_list and len(opponent_list) < 3:
        diff = count - len(opponent_list)
    
    opponent_list = get_upper_opponents(db, user_rating, diff, opponent_list)
    if len(opponent_list) < count:
        opponent_list = get_lower_opponents(db, user_rating, count)

    return opponent_list

def assign_opponents_to_user(db, user):
    """Gets blitz rating of user then finds opponents in table"""

    opponent_list = generate_opponent_list(db, user)
    
    for i in range(6):
        User_Opponent.match_opponent(db, user.id, opponent_list[i], i)

    return opponent_list

def find_opponents(db, user):
    """Queries and returns the matchings assigned to the user"""
    opponents_query = User_Opponent.list_opponents(
            user).join(Opponent, User_Opponent.opponent_id == Opponent.id)
    opponents_bulk = db.session.execute(opponents_query)
    opponents = []
    for opp in opponents_bulk:
        opponents.append(opp[0])

    return opponents

def find_victories(db, user):
    """Queries and returns the recorded victories of the user"""

    victories_query = User_Victory.list_victories(
        user).join(Opponent, User_Victory.opponent_id == Opponent.id)
    victories_bulk = db.session.execute(victories_query)
    victories = []
    for vict in victories_bulk:
        victories.append(vict[0])

    return victories

def find_new_opponent(opponents, strength, pairings):
    """Searches for an opponent not currently in the list of pairings"""

    if opponents[strength] in pairings:
        return find_new_opponent(opponents, (strength+1)%7, pairings)
    else:
        return opponents[strength]

def reroll(db, user, pairings, strength):
    """Selects 7 opponents and compares id's to ensure a new opponent"""

    opponent_list = generate_opponent_list(db, user, 7)
    new_opponent = find_new_opponent(opponent_list, strength, pairings)
    
    User_Opponent.match_opponent(db, user.id, new_opponent, strength)
    
    return new_opponent


def check_victory(strength, user, opponent, year, month):
    "Requests game history of the user to check for victory over opponent"

    request = requests.get(f"{PLAYER_URL}{user.username}/{GAMES}/{year}/{month}",
        headers=REQUEST_HEADER)
    games = request.json()[GAMES] 
    if not games:
        flash("No games found", "danger")
        return False

    for game in games:
        white = game[WHITE][USERNAME].lower()
        black = game[BLACK][USERNAME].lower()

    if white == opponent.username or black == opponent.username:
        if (white == opponent.username and game[BLACK][RESULT] == "win") or (white != opponent.username and game[WHITE][RESULT] == "win"):
            User_Victory.add_user_victory(user.id, opponent.id, strength)
            flash ("Congratulations!", "success")
            return True
	

    flash("Game not found", "danger")
    return False