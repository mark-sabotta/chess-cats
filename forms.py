from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, validators
from wtforms.validators import DataRequired, Email, Length

from myvalidators import on_chess_com_validator, validate_username


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired(), on_chess_com_validator, validate_username])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


#{"avatar":"https://images.chesscomfiles.com/uploads/v1/user/3166377.99e3e36a.200x200o.3810c0ef7901.jpeg","player_id":3166377,"@id":"https://api.chess.com/pub/player/marcussabotta","url":"https://www.chess.com/member/MarcusSabotta","name":"Mark Sabotta","username":"marcussabotta","followers":35,"country":"https://api.chess.com/pub/country/US","last_online":1692811615,"joined":1211784330,"status":"basic","is_streamer":false,"verified":false,"league":"Elite"}
#{"code":0,"message":"User \"mditploggth\" not found."}