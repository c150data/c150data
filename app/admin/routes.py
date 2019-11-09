from flask import Blueprint, request, render_template, redirect, flash
from app.admin import admin
from app import log, ACCESS, db
from app.database import db_filler 
from app.database.db_models import WhoopAthlete
from app.api import oauth, oauth_whoop
from app.utils import requires_access_level

admin1 = Blueprint('admin1', __name__)


# ADMIN

@admin1.route("/admin")
@requires_access_level(ACCESS['admin'])
def admin():
    return render_template("/admin/home.html")


@admin1.route("/admin/authorize")
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
        return render_template("/admin/home.html")


@admin1.route("/admin/insertNewToken")
@requires_access_level(ACCESS['admin'])
def insertNewToken():
    try:
        log.info("Getting new token...")
        oauth.insertNewToken(oauth.getNewAccessToken())
        flash("A new access token was successfuly inserted into the database.", 'success')
    except Exception as e:
        log.exception("Error occurred while inserting new token: {}".format(e))
        flash("An error occurred while inserting a new acccess token into the database.", 'danger')
    return render_template("about.html")


@admin1.route("/admin/insertAllAthletes")
@requires_access_level(ACCESS['admin'])
def insertAllAthletesApp():
    try:
        log.info("Inserting all athletes into database...")
        numAthletesInserted = db_filler.insertAllAthletesIntoDB()
        flash("Successfully inserted {} athletes into the database.".format(
            numAthletesInserted), 'success')
    except Exception as e:
        log.exception(
            "Error occurred while inserting all athletes: {}".format(e))
        flash("Error while inserting athletes into database.", 'danger')
    return render_template("/admin/home.html")


@admin1.route("/admin/insertAllWorkouts")
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
        log.exception(
            "Error occurred while inserting all workouts: {}".format(e))
        result = "danger"
        message = "Error while inserting workouts."
    return render_template("alert.html", alert_type=result, alert_message=message)


@admin1.route("/admin/insertWhoopData")
@requires_access_level(ACCESS['admin'])
def insertAllWhoopWorkouts():
    start_date, end_date = request.args.get('start_date'), request.args.get('end_date')
    try:
        log.info("Inserting all whoop workouts between {} and {}".format(start_date, end_date))
        num_days_affected, total_workouts_affected = db_filler.insertWhoopData(start_date, end_date)
        result = "success"
        message = "Successfully inserted {} days worth of data into the database, including a total of {} workouts".format(
            num_days_affected,
            total_workouts_affected
        )
    except Exception as e:
        log.exception(
            "Error occurred while inserting all whoop workouts: {}".format(e))
        result = "danger"
        message = "Error while inserting workouts."
    return render_template("alert.html", alert_type=result, alert_message=message)


@admin1.route("/admin/insertWhoopAthlete")
@requires_access_level(ACCESS['admin'])
def insertWhoopAthlete():
    username, password = request.args.get('username'), request.args.get('password')
    try:
        athlete_info = oauth_whoop.getInfoForNewAthlete(username, password)
        athlete_to_insert = WhoopAthlete(
            whoopAthleteId=athlete_info['whoopAthleteId'], 
            firstName=athlete_info['firstName'],
            lastName=athlete_info['lastName'],
            username=username, 
            password=password,
            authorizationToken=athlete_info['token'], 
            expires_at=athlete_info['expiresAt']
        )
        db.session.add(athlete_to_insert)
        db.session.commit()
        result='success'
        message='Successfully inserted a new Whoop Athlete with id {}'.format(athlete_info['whoopAthleteId'])
    except Exception as e:
        log.exception('Error occurred while inserting a new whoop athlete: {}'.format(e))
        result='danger'
        message='Error while inserting new whoop athlete.'
    return render_template("alert.html", alert_type=result, alert_message=message)

    
