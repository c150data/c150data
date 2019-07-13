from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.widgets import TextArea
from app.db_models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
            validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
            validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
            validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_username(self, username): #check if username already exists in database
        user = User.query.filter_by(username=username.data).first()
        if user: 
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email): #check if username already exists in database
        user = User.query.filter_by(email=email.data).first()
        if user: 
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', 
            validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
            validators=[DataRequired()])
    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')

class ContactForm(FlaskForm):
    firstname = StringField('First Name',
        validators=[DataRequired(), Length(min=2, max=25)])
    lastname = StringField('Last Name',
        validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Email', 
            validators=[DataRequired(), Email()])
    subject = StringField('Subject of Message',
        validators=[DataRequired(), Length(min=2, max=25)])
    message = StringField('Feedback, Comments, Concerns?', widget=TextArea(),
        validators=[DataRequired()])
    submit = SubmitField('Send')
