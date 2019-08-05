from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.widgets import TextArea


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
