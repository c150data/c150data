from flask import render_template, url_for, redirect, request, Blueprint, flash
from app.main.forms import ContactForm, WhoopTPSyncForm 
from flask_mail import Message
from app import app, log, mail, ACCESS
from requests import exceptions
from app.api import oauth_whoop
from app.database.db_models import Athlete, WhoopAthlete
from app.utils import requires_access_level

main = Blueprint('main', __name__)


@main.route("/", methods=['GET'])
def index():
    return redirect(url_for('main.about'))


@main.route("/about", methods=['GET', 'POST'])
def about():
    return render_template("about.html")


@main.route("/contact", methods=['GET', 'POST'])
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
            log.info("Sending message from {first} {last} to lwtpoodles150@gmail.com".format(
                first=form.firstname.data, last=form.lastname.data))
            mail.send(msg)
            flash('Message Sent!', 'success')
            # TODO: Handle error in case of unsuccessful sending
            return render_template('contact.html', form=form)
    elif request.method == 'GET':
        return render_template("contact.html", form=form)


@main.route('/whoop', methods=['GET', 'POST'])
def whoop():
    form = WhoopTPSyncForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            tp_athlete = Athlete.query.filter_by(email=form.tp_email.data).first()
            if not user:
                flash('Could not find a TrainingPeaks account with that email. Check your email and try again.')
            r = insertWhoopAthlete
    else:
        return render_template('whoop.html', form=form)


##########################################################################

def insertWhoopAthlete(username, password):
    try:
        athlete_info = oauth_whoop.getInfoForNewAthlete(username, password)
        athlete_to_insert = WhoopAthlete(
            whoopAthleteId=athlete_info['whoopAthleteId'], 
            firstName=athlete_info['firstName'],
            lastName=athlete_info['lastName'],
            username=username, 
            password=password,
            authorizationToken=athlete_info['token'], 
            expires_at=athlete_info['expiresAt'],
            last_updated_data = Whoop_Default_Last_Updated_Date
        )
        db.session.add(athlete_to_insert)
        db.session.commit()
        result='success'
        message='Successfully inserted a new Whoop Athlete with id {}'.format(athlete_info['whoopAthleteId'])
    except ValueError as e:
        return False, "Incorrect username or password for athlete."
    except exceptions.BaseHTTPError as e:
        return False, ""
    return render_template("alert.html", alert_type=result, alert_message=message)