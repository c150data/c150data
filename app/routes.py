from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from authlib.client import OAuth2Session
from app import app, db, bcrypt, log, hours_helper, oauth_helper, db_filler
from app.models import User
from app.forms import RegistrationForm, LoginForm


# PAGES

@app.route("/", methods=['GET'])
def index():
    return redirect(url_for('about'))


@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template("about.html")


@app.route("/hours", methods=['GET', 'POST'])
@login_required
def hours():
    return render_template("hours.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    # TODO contact form submission should email lwtpoodles150@gmail.com
    return render_template("contact.html")


# TODO Account/Profile page to change password, manage contact info, etc.

# DATA 

@app.route("/hours/getData")
@login_required
def getData():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    len, athletes = hours_helper.getHoursForAllAthletes(start_date, end_date)
    return render_template("data.html", len=len, athletes=athletes)


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
@login_required
def register():
    # Commenting this out since our new flow will be only admins can register new users. 
    # if current_user.is_authenticated:  # Logged in user will be forwarded to about page
    #     return redirect(url_for('about'))
    form = RegistrationForm()
    if form.validate_on_submit():  # Enters this section when registration form has been submitted
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('A new account has been created with the username: {}. You are now able to log in.'.format(form.username.data), 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ADMIN

@app.route("/admin")
@login_required  # Ideally, this is where we can put something like admin_required
def admin():
    if app.config['ENV'] == 'production':
        return redirect(url_for('about'))
    return render_template("admin.html")


@app.route("/admin/authorize")
@login_required
def user_authorization():
    return redirect(oauth_helper.getAuthorizationUrl())


@app.route("/admin/insertNewToken")
@login_required
def insertNewToken():
    success = oauth_helper.insertNewToken(oauth_helper.getNewAccessToken())
    if success:
        flash("A new access token was successfuly inserted into the database.", 'success')
    else:
        flash("An error occurred while inserting a new acccess token into the database.", 'error')
    return render_template("admin.html")


@app.route("/admin/insertAllAthletes")
@login_required
def insertAllAthletesApp():
    numAthletesInserted = db_filler.insertAllAthletesIntoDB()
    if numAthletesInserted is None:
        flash("Error while inserting athletes into database.", 'danger')
    else:
        flash("Successfully inserted {} athletes into the database.".format(
            numAthletesInserted), 'success')
    return render_template("admin.html")


@app.route("/admin/insertAllWorkouts")
@login_required
def insertAllWorkoutsApp():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    numWorkoutsInserted = db_filler.insertWorkoutsIntoDb(start_date, end_date)
    if numWorkoutsInserted is None:
        result = "danger"
        message = "Error while inserting workouts."
    else:
        result = "success"
        message = "Successfully inserted {} workouts into the database.".format(numWorkoutsInserted)
    return render_template("alert.html", alert_type=result, alert_message=message)
