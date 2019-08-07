from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt, log, ACCESS
from app.database.db_models import User
from app.users.forms import (RegistrationForm, LoginForm,
                             RequestResetForm, ResetPasswordForm)
from app.users.utils import send_reset_email
from app.utils import requires_access_level

users = Blueprint('users', __name__)


# LOGIN

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.about'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # check if password matches
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.about'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/register", methods=['GET', 'POST'])
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
        log.info("A new account has been created with the username: {}".format(
            form.username.data))
        flash('A new account has been created with the username: {}. You are now able to log in.'.format(
            form.username.data), 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/logout")
@requires_access_level(ACCESS['user'])
def logout():
    logout_user()
    return redirect(url_for('main.about'))


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.about'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.about'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():  # Enters this section when registration form has been submitted
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated. You are now able to log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
