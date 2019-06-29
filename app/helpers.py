"""
Helper methods for the c150.data data retrieval process
"""

from __future__ import division
from app import db, log, oauth_helper, constants, api_helper, db_helper
import pymysql
from datetime import datetime, timedelta
import requests
from app.models import AuthToken, Athlete, Workout
import math
import operator


remote = False  # CHANGE FOR DB CONNECTION


# DB schema
db_schema_name = "c150data"
# Local config
db_local_host = "localhost"
db_local_user = "root"
db_local_passwd = ""
db_local_port = 3306
# Remote config
# In order to make connection on ssh it needs to use a socket instead of host
db_remote_socket = "/var/run/mysqld/mysqld.sock"
db_remote_port = 3306
db_remote_user = "mamsterdam"
db_remote_passwd = "Columbia150"
# DB tables
db_auth_token_table = "auth_token"
db_athletes_table = "athletes"

refresh_padding_time = 300


def dbInsert(items):
    """
    Inserts items into the database

    Args:
        items: A single model object or a list of objects

    Returns:
       Integer: Number of rows inserted
    """
    if items is None:
        return False

    try:
        if isinstance(items, list):
            for item in items:
                db.session.add(item)
        else:
            result = db.session.add(items)
        db.session.commit()
        return True
    except Exception as e:
        log.error("Error inserting [%s] into the database: %s", items, e)
        db.session.rollback()
        db.session.flush()
        return False


# OAuth Token with database

def insertNewToken(token):
    """
    Inserts token into database. This method does NOT do expiration date checking,
    that is to be done by the method's caller

    Args:
        token (dict): dict object with the following fields: access_token, token_type, expires_in, refresh_token, and scope.

    Returns:
        Boolean: True on successful insertion, False on unsuccessful insertion
    """
    access_token, token_type, expires_in, refresh_token, scope = token['access_token'], token[
        'token_type'], token['expires_in'], token['refresh_token'], token['scope']

    # Give the expires_in time an extra 5 minutes as padding time and remove microseconds
    expires_at_date = datetime.now(
    ) + timedelta(seconds=(int(expires_in)-refresh_padding_time))

    token = AuthToken(access_token=access_token, token_type=token_type,
                      expires_at=expires_at_date, refresh_token=refresh_token, scope=scope)
    return dbInsert(token)


def refreshAuthTokenIfNeeded():
    """
    Checks if auth_token needs refreshing, and refreshes if necessary

    Returns:
        Boolean: True if successful, otherwise False
    """
    most_recent_token = AuthToken.query.order_by(AuthToken.id.desc())[0]
    if most_recent_token is not None:
        refresh_date = most_recent_token.expires_at
        if refresh_date < datetime.now():
            # Pass in the refresh_token from the most recent row
            return refreshAuthToken(most_recent_token.refresh_token)
        return True  # Returns True if token does not have to be refreshed

    return False


def refreshAuthToken(refresh_token):
    """
    Makes an API call to get a new token and inserts it into the
    Args:
        refresh_token (str): Refresh token

    Returns:
        Boolean: True if successful, False otherwise
    """
    return insertNewToken(oauth_helper.getRefreshedToken(refresh_token))


def getValidAuthToken():
    """
    Returns a valid authtoken to be used for API calls

    Returns:
        Row: The Row object of a valid token
        None: On error
    """
    if refreshAuthTokenIfNeeded() is False:
        log.error("Did not successfully refresh authentication token.")
        return None

    return AuthToken.query.order_by(AuthToken.id.desc()).first()


# Inserting athletes into database

def insertAllAthletesIntoDB():
    """
    Inserts all athletes into an empty athletes table in the database

    Returns:
        int: Number of athletes successfully inserted
        None: On error
    """
    athletesList = getAllAthletesUsingAPI()
    success = dbInsert(athletesList)
    if success:
        return len(athletesList)
    else:
        return None


def getAllAthletesUsingAPI():
    """
    Makes an API call to get every athlete under the current coach

    Returns:
        List of Athlete db.Model objects.
        None on error.
    """
    # Make API call
    athletes_response = api_helper.getAthletes(getValidAuthToken())

    # Error check
    if athletes_response is None:
        return None

    # Parse reponse into Athlete db objects
    athletes_to_return = list()
    for athlete in athletes_response.json():
        athletes_to_return.append(
            db_helper.getAthleteObjectFromJSON(athlete))

    return athletes_to_return


# Inserting Workouts into Database

def insertWorkoutsIntoDb(start_date, end_date):
    try:
        id_list = get_ids(getAllActiveAthletes())
        datesList = getListOfStartEndDates(start_date, end_date)
        log.info("Dates List: %s", datesList)
        workoutsList = list()

        for id in id_list:
            for date_period in datesList:
                workoutsList += getListOfWorkoutsForAthletes(id, date_period)

        result = dbInsert(workoutsList)
        if result:
            return len(workoutsList)
        else:
            return None
    except Exception as e:
        raise Exception("Error while inserting workouts into database: %s", e)
        return None


def get_ids(athletes):
    ids = list()
    for athlete in athletes:
        ids.append(athlete.id)
    return ids


def getListOfStartEndDates(start_date, end_date):
    MAX_DAYS = 45  # From TP API
    if not start_date or not end_date:
        raise Exception("Dates cannot be empty.")

    dStart = datetime.strptime(start_date, '%m/%d/%Y')
    dEnd = datetime.strptime(end_date, '%m/%d/%Y')
    diff = dEnd - dStart
    total_days = diff.days
    num_api_calls = math.ceil(total_days/MAX_DAYS)
    listStartEndTuples = list()
    currStart = dStart
    for i in range(num_api_calls):
        start = currStart
        # Have to do minus 1 since the range from start to end is inclusive for both
        end = currStart + timedelta(days=MAX_DAYS-1)

        # Checks the last set of dates for overflow. If the currStart + 45 days is > overall end_date, then set end to end_date
        if end > dEnd:
            end = dEnd

        start_formatted_for_api = start.strftime('%Y-%m-%d')
        end_formatted_for_api = end.strftime('%Y-%m-%d')

        listStartEndTuples.append(
            (start_formatted_for_api, end_formatted_for_api)
        )

        currStart = end + timedelta(days=1)

    return listStartEndTuples


def getListOfWorkoutsForAthletes(athlete_id, date_period_tuple):
    start_date, end_date = date_period_tuple
    workouts_json = api_helper.getWorkoutsForAthlete(
        getValidAuthToken(), athlete_id, start_date, end_date).json()
    dbWorkoutsList = list()
    for workout_j in workouts_json:
        dbWorkoutsList.append(db_helper.getWorkoutObjectFromJSON(workout_j))
    log.info("{} workouts found for athlete {} from {} to {}".format(
        len(dbWorkoutsList), athlete_id, start_date, end_date))
    return dbWorkoutsList


def getAllActiveAthletes():
    return Athlete.query.filter_by(is_active=True).all()


# Data retrieval methods

def getHoursForAllAthletes(start_date, end_date):
    result = db.session.execute(getAllHoursSQL(start_date, end_date))
    athleteHourList = list()
    for row in result:
        athlete_info = {
            "name": row['name'],
            "hours": row['hours'],
            "rounded_hours": round(row['hours'], 2)
        }
        athleteHourList.append(athlete_info)
    sortedAthleteHourList = sorted(athleteHourList, key=operator.itemgetter('hours'), reverse=True)
    return len(sortedAthleteHourList), sortedAthleteHourList


def getAllHoursSQL(start_date, end_date):
    start_date_f = datetime.strptime(start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    end_date_f = datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    statement = "SELECT athletes.name, SUM(CASE WHEN workouts.startTime >= '{}' AND workouts.startTime <= '{}' then workouts.totalTime else 0 END) as hours FROM athletes INNER JOIN workouts ON athletes.id = workouts.athleteId GROUP BY athletes.id;".format(start_date_f, end_date_f)
    log.info(statement)
    return statement
