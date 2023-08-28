from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, validators
from wtforms.validators import DataRequired, Email, Length
import requests

player_url = "https://api.chess.com/pub/player/"

#def on_chess_com_validator(form, field):
    #query_username = field.data.lower()
    #response = requests.get(f"{player_url}{query_username}")
    #if response.status_code == "404":
        #raise validators.ValidationError("User not found")

    #if response.status_code == "403":
        #raise validators.ValidationError("Please try again later")
    
    


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


#{"avatar":"https://images.chesscomfiles.com/uploads/v1/user/3166377.99e3e36a.200x200o.3810c0ef7901.jpeg","player_id":3166377,"@id":"https://api.chess.com/pub/player/marcussabotta","url":"https://www.chess.com/member/MarcusSabotta","name":"Mark Sabotta","username":"marcussabotta","followers":35,"country":"https://api.chess.com/pub/country/US","last_online":1692811615,"joined":1211784330,"status":"basic","is_streamer":false,"verified":false,"league":"Elite"}
#{"code":0,"message":"User \"mditploggth\" not found."}