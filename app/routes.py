"""
Routes module that handles all url endpoints. This module is the main
driver of the entire application.

Note: our general flow is going to be that these routes handle the error checking.
This means that any route that calls a function that throws errors should surround that
method with a try-catch block
"""
from flask import request, render_template, redirect, url_for, flash, session, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from authlib.client import OAuth2Session
from app import app, db, bcrypt, log, ACCESS, mail
from app.data import hours as athlete_hours
from app.api import oauth
from app.database import db_filler
from app.db_models import User
from app.forms.forms import (RegistrationForm, LoginForm, ContactForm, 
                            RequestResetForm, ResetPasswordForm)

# PAGES

# Any url route that does not exist will be redirected to this page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


# TODO Account/Profile page to change password, manage contact info, etc.

# DATA

