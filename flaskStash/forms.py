from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, MonthField, SubmitField, BooleanField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
from flaskStash.database import Users
from flask_login import current_user

class SearchForm(FlaskForm):
    searched=StringField("Searched", validators=[DataRequired()])
    submit=SubmitField('')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8), EqualTo('password')])
    birthMonth = MonthField('Birth Month', validators=[DataRequired()])
    submit=SubmitField('Register')

    def validate_username(self, username):
        user=Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    remember = BooleanField('Remember Me')
    submit=SubmitField('Login')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    birthMonth = MonthField('Birth Month', validators=[DataRequired()])
    submit=SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user=Users.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username already exists. Please choose a different one.')

class AddToDatabase(FlaskForm):
    artist=StringField('Artist', validators=[DataRequired()])
    album=StringField('Album', validators=[DataRequired()])
    year=StringField('Year', validators=[DataRequired()])
    image_file=FileField('Add Album Art', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    format=SelectField('Format', choices=['Digital', 'CD', 'Vinyl', 'Cassette', '8-Track', 'Other'], validators=[DataRequired()])
    submit=SubmitField('Add')

class AddToStashForm(FlaskForm):
    package_condition=SelectField('Package Condition', choices=['N/A', 'Mint', 'Very Good', 'Good', 'Fair', 'Poor', 'Trashed'], validators=[DataRequired()])
    media_condition=SelectField('Media Condition', choices=['N/A', 'Mint', 'Very Good', 'Good', 'Fair', 'Poor', 'Trashed'], validators=[DataRequired()])
    approx_resale_value=IntegerField('Resale Value', validators=[DataRequired()])
    overall_rating=FloatField('Overall Rating (out of 5)', validators=[NumberRange(min=0, max=5, message='Must between 0 and 5')])
    production_rating=FloatField('Production Rating (out of 5)', validators=[NumberRange(min=0, max=5, message='Must between 0 and 5')])
    musicianship_rating=FloatField('Musicianship Rating (out of 5)', validators=[NumberRange(min=0, max=5, message='Must between 0 and 5')])
    songwriting_rating=FloatField('Songwriting Rating (out of 5)', validators=[NumberRange(min=0, max=5, message='Must between 0 and 5')])
    vocals_rating=FloatField('Vocals Rating (out of 5)', validators=[NumberRange(min=0, max=5, message='Must between 0 and 5')])
    lyrics_rating=FloatField('Lyrics Rating (out of 5)', validators=[NumberRange(min=0, max=5, message='Must between 0 and 5')])
    genre=SelectField('Genre', choices=['Pop', 'Rock', 'Alternative', 'Metal', 'Jazz', 'Hip-Hop', 'R&B', 'Funk', 'Country/Western', 'Folk', 'Electronica', '"Classical" aka. Common Practice Period', 'Avant-Guard', 'Other' ])
    subgenre=StringField('Subgenre', validators=[])
    submit=SubmitField('Add To Stash')

class AddToWishlist(FlaskForm):
    purchase_priority=SelectField('Purchase Priority Rating', validators=[DataRequired()], choices=["1 (Least)", "2", "3", "4", "5 (Most)"])
    submit=SubmitField('Add To Wishlist')