from flask import request, render_template, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from authlib.client import OAuth2Session
from app import app, db, bcrypt, helpers, log
from app.models import User
from app.forms import RegistrationForm, LoginForm

# TODO Constants that should be moved elsewhere 
client_id = 'columbiac150'
client_secret = 'kzSN7CYgZYUMzb8DfhEqRnqrHAqiAEUHOgSAJo8' # TODO move this somewhere else out of version control 
coach_scope = ["coach:athletes", "workouts:read"]
redirect_uri = "https://localhost:5000"
authorization_base_url = 'https://oauth.sandbox.trainingpeaks.com/OAuth/Authorize'
token_base_url = 'https://oauth.sandbox.trainingpeaks.com/oauth/token'


# PAGES

@app.route("/", methods=['GET'])
def index():
    return redirect(url_for('about'))


@app.route("/about", methods=['GET', 'POST'])
def about():
    log.info("got the about page...")
    return render_template("about.html")


@app.route("/hours", methods=['GET', 'POST'])
@login_required
def hours():
    return render_template("hours.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    # TODO contact form submission should email lwtpoodles150@gmail.com
    return render_template("contact.html")


#possible account page for user
#@login_required
#@app.route("/account")
#def account():


# REQUESTS

@app.route("/insertAllAthletes")
def insertAllAthletesApp():
    numAthletesInserted = helpers.insertAllAthletesIntoDB()
    log.info("Successfully inserted {} athletes.", numAthletesInserted) 
    return render_template("admin.html") 


@app.route("/insertAllWorkouts")
def insertAllWorkoutsApp():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    numWorkoutsInserted = helpers.insertWorkoutsIntoDb(start_date, end_date)
    log.info("Successfully inserted {} workouts.", numWorkoutsInserted) 
    return render_template("admin.html") 


@app.route("/getData")
@login_required
def getData():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    len, athletes = helpers.getAllAthletesHours(start_date, end_date)
    return render_template("data.html", len=len, athletes=athletes)



# LOGIN

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('about'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data): # check if password matches
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('about'))
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: # Logged in user will be forwarded to about page
        return redirect(url_for('about'))
    form = RegistrationForm()
    if form.validate_on_submit(): # Enters this section when registration form has been submitted
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form) 


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))



# ADMIN

@app.route("/admin")
@login_required # Ideally, this is where we can put something like admin_required
def admin():
    return render_template("admin.html")


@app.route("/authorize")
@login_required
def user_authorization():
    oauth_session = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri,
                                  scope=coach_scope)
    authorization_url, state = oauth_session.create_authorization_url(authorization_base_url)
    print(authorization_url)
    return redirect(authorization_url)


@app.route("/insertNewToken")
@login_required
def insertNewToken():
    oauth_session = OAuth2Session(client_id, client_secret,
                                  redirect_uri=redirect_uri, scope=coach_scope)
    authorization_response = input(str("authorization_response: "))
    token = oauth_session.fetch_access_token(token_base_url,
                                             authorization_response=authorization_response)
    print("Got a new token: ", token)
    print("Inserting token...")
    helpers.insertNewToken(token)
    return render_template("admin.html")

