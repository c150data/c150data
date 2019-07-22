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
from app.admin import admin
from flask_mail import Message
from app.db_models import User
from app.forms.forms import (RegistrationForm, LoginForm, ContactForm, 
                            RequestResetForm, ResetPasswordForm)

# Admin decorator
from functools import wraps


def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please login to view this site', 'danger')
                return redirect(url_for('login'))

            elif not current_user.allowed(access_level):
                flash(
                    'You do not have the right priviledges to access this page.', 'danger')
                return redirect(url_for('about'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# PAGES

# Any url route that does not exist will be redirected to this page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.route("/", methods=['GET'])
def index():
    return redirect(url_for('about'))


@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template("about.html")


@app.route("/data", methods=['GET', 'POST'])
@requires_access_level(ACCESS['user'])
def data():
    return render_template("data.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        if form.validate() is False:
            flash('All fields are required', 'danger')
            return render_template('contact.html', form=form)
        else:
            msg = Message(form.subject.data, sender="lwtpoodles150@gmail.com", recipients=[
                'lwtpoodles150@gmail.com'])
            msg.body = """
                       From: %s %s <%s>
                       %s
                       """ % (form.firstname.data, form.lastname.data, form.email.data, form.message.data)
            log.info("Sending message from {first} {last} to lwtpoodles150@gmail.com".format(first=form.firstname.data, last=form.lastname.data))
            mail.send(msg)
            return 'Form sent.'
    elif request.method == 'GET':
        return render_template("contact.html", form=form)

# TODO Account/Profile page to change password, manage contact info, etc.

# DATA


@app.route("/data/getData")
@requires_access_level(ACCESS['user'])
def getData():
    """
    On error, this returns a 500 internal server error status code. The Jquery call that
    calls this end point then reloads the page, forcing the flash message to appear.

    On success though, the webpage does not need to be reloaded at all.
    """
    start_date, end_date = request.args.get('start_date'), request.args.get('end_date')
    athletes = None
    try:
        athletes = athlete_hours.getHoursForAllAthletes(start_date, end_date)
        response_code = 200
    except Exception as e:
        log.exception("Was not able to get hours: {error}".format(error=e))
        response_code = 500
    return jsonify(athletes), response_code


# LOGIN

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('about'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # check if password matches
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('about'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
@requires_access_level(ACCESS['admin'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():  # Enters this section when registration form has been submitted
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        log.info("A new account has been created with the username: {}".format(form.username.data))
        flash('A new account has been created with the username: {}. You are now able to log in.'.format(
            form.username.data), 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/logout")
@requires_access_level(ACCESS['user'])
def logout():
    logout_user()
    return redirect(url_for('index'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
        sender='lwtpoodles150@gmail.com', 
        recipients=[user.email])
    # Format of this is important or tabs will be shown in the email
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made. 
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('about'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.','info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('about'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token','warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():  # Enters this section when registration form has been submitted
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated. You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


# ADMIN

@app.route("/admin")
@requires_access_level(ACCESS['admin'])
def admin():
    return render_template("/admin/home.html")


@app.route("/admin/authorize")
@requires_access_level(ACCESS['admin'])
def user_authorization():
    try:
        url = oauth.getAuthorizationUrl()
        log.info("Redirecting user to {} for authorization...".format(url))
        return redirect(url)
    except Exception as e:
        log.exception(
            "Error occurred while getting the authorization url: {}".format(e))
        flash("An error occurred while getting the authorization url", 'danger')
        return render_template("about.html")


@app.route("/admin/insertNewToken")
@requires_access_level(ACCESS['admin'])
def insertNewToken():
    try:
        log.info("Getting new token...")
        oauth.insertNewToken(oauth.getNewAccessToken())
        flash("A new access token was successfuly inserted into the database.", 'success')
    except Exception as e:
        log.exception("Error occurred while inserting new token: {}".format(e))
        flash("An error occurred while inserting a new acccess token into the database.", 'danger')
    return render_template("/admin/home.html")


@app.route("/admin/insertAllAthletes")
@requires_access_level(ACCESS['admin'])
def insertAllAthletesApp():
    try:
        log.info("Inserting all athletes into database...")
        numAthletesInserted = db_filler.insertAllAthletesIntoDB()
        flash("Successfully inserted {} athletes into the database.".format(
            numAthletesInserted), 'success')
    except Exception as e:
        log.exception("Error occurred while inserting all athletes: {}".format(e))
        flash("Error while inserting athletes into database.", 'danger')
    return render_template("/admin/home.html")


@app.route("/admin/insertAllWorkouts")
@requires_access_level(ACCESS['admin'])
def insertAllWorkoutsApp():
    """
    Note: this endpoint is called with JQuery, so flash() does not work.
    Instead, we return an alert.html component that gets inserted into the page.
    """
    start_date, end_date = request.args.get(
        'start_date'), request.args.get('end_date')
    try:
        log.info("Inserting all workouts into the database...")
        numWorkoutsInserted = db_filler.insertWorkoutsIntoDb(
            start_date, end_date)
        result = "success"
        message = "Successfully inserted {} workouts into the database.".format(
            numWorkoutsInserted)
    except Exception as e:
        log.exception("Error occurred while inserting all workouts: {}".format(e))
        result = "danger"
        message = "Error while inserting workouts."
    return render_template("alert.html", alert_type=result, alert_message=message)
