from flask import Blueprint, request, render_template, flash, jsonify
from app import log, ACCESS
from app.data import hours as athlete_hours
from app.utils import requires_access_level

data1 = Blueprint('data1', __name__)


@data1.route("/data", methods=['GET', 'POST'])
@requires_access_level(ACCESS['user'])
def data():
    return render_template("data.html")

@data1.route("/data/getData")
@requires_access_level(ACCESS['user'])
def getData():
    """
    On error, this returns a 500 internal server error status code. The Jquery call that
    calls this end point then reloads the page, forcing the flash message to appear.

    On success though, the webpage does not need to be reloaded at all.
    """
    start_date, end_date = request.args.get('start_date'), request.args.get('end_date')
    try:
        athletes = athlete_hours.getHoursForAllAthletes(start_date, end_date)
        response = 200
    except Exception as e:
        log.exception("Was not able to get hours: {error}".format(error=e))
        athletes = None
        response = 404
    return jsonify(athletes), response

@data1.route("/data/updateData", methods=['POST'])
@requires_access_level(ACCESS['user'])
def updateData():
    athlete_hours.updateWorkoutsIfNecessary()
    return "Results updated"
