"""
Makes large batch requests to the API to fill the database.

Currently, able to get all the athletes under the current coach (Nich), and insert them all into the database.
Can also insert all workouts for every athlete under the current coach (Nich), and insert them all into the database.
Note: the workouts request accepts a date range and gets all requests within that range.
"""
from app import log
from app.database.db_models import Athlete, Workout
from app.database import db_functions, sql_statements as sql
from app.api import api_requester, oauth, api_service, api_whoop_service
from app.api.utils import InvalidZoneAthletes
from datetime import datetime, timedelta
import math

MAX_DAYS = 45


def insertAllAthletesIntoDB():
    """
    Inserts all athletes into an empty athletes table in the database

    Returns:
        int: Number of athletes inserted
    """
    athletesList = api_service.getDBAthletesUsingAPI()
    log.info("Inserting {} athletes into the database...".format(len(athletesList)))
    db_functions.dbInsert(athletesList)
    return len(athletesList)


def insertWorkoutsIntoDb(start_date, end_date):
    """
    Inserts all workouts from start_date to end_date into workout table

    Args:
        start_date (datetime): Start Datetime object
        end_date (datetime): End Datetime object

    Returns:
        int: number of workouts inserted into the database
    """
    athletes = db_functions.dbSelect(sql.getAllActiveAthletesSQL())
    datesList = getListOfStartEndDates(start_date, end_date, MAX_DAYS)
    workoutsList = list()

    for athlete in athletes:
        athlete_num_workouts = 0
        for date_period in datesList:
            currWorkouts = api_service.getDBWorkoutsUsingAPI(
                athlete.id, date_period)
            workoutsList += currWorkouts
            athlete_num_workouts += len(currWorkouts)
        log.info("{} workouts found for {} from {} to {}".format(
            athlete_num_workouts, athlete['name'], start_date, end_date))

    log.info("Wrong num HR zones: {}".format(InvalidZoneAthletes.wrongNumHrZones))
    log.info("Wrong num power zones: {}".format(InvalidZoneAthletes.wrongNumPowerZones))
    log.info("Reverse HR zones: {}".format(InvalidZoneAthletes.reverseHrZones))
    log.info("Reverse Power zones: {}".format(InvalidZoneAthletes.reversePowerZones))
    db_functions.dbInsert(workoutsList)
    return len(workoutsList)


def insertWhoopData(start_date, end_date):
    """
    Inserts all whoop workouts from start_date to end_date into whoop workout table

    Args:
        start_date (datetime): Date in form MM/DD/YYYY 
        end_date (datetime): Date in form MM/DD/YYYY 

    Returns:
        int: number of datab 
    """
    whoop_athletes = db_functions.dbSelect(sql.getAllWhoopAthletesSQL())
    all_db_objects_to_insert = list()
    total_workouts = 0 
    dStart = datetime.strptime(start_date, '%m/%d/%Y')
    dEnd = datetime.strptime(end_date, '%m/%d/%Y')

    for athlete in whoop_athletes:
        # Note that each day has several database objects within it. For example
        # a single day should have a WhoopDay, WhoopStrain, and possibly several WhoopWorkout objects
        day_db_object, strain_db_object, workout_db_objects = api_whoop_service.getDBObjectsForDay(
            athlete.whoopAthleteId, dStart, dEnd)
        # TODO: Should probably add here the call to insert all HR data between start and end date of the workout objects
        total_workouts += len(workout_db_objects) 
        
        all_db_objects_to_insert.append(day_db_object)
        all_db_objects_to_insert.append(strain_db_object)
        all_db_objects_to_insert += workout_db_objects

    db_functions.dbInsert(all_db_objects_to_insert)
    return num_days, total_workouts 

def getListOfStartEndDates(start_date, end_date, max_date_range):
    """
    The TP API can only accept getWorkouts request for an athlete for a 45 day maximum, per request.
    Because of this, in order to do large batches, we need to divide up a larger date range into smaller
    ranges, none of which can be more than 45 days. This function takes the large date range and returns
    a list of smaller date ranges (tuples)

    NOTE: Each date range consists of [start_date, end_date], with BOTH being INCLUSIVE. This is unconventional from
    a coding perspective but since the TP API does it like this, we follow suit.

    Arguments:
        start_date {Datetime}
        end_date {Datetime}

    Returns:
        List of Tuples -- List of (start_date, end_date), with difference never being more than  max_date_range
    """
    if not start_date or not end_date:
        raise Exception("Dates cannot be empty.")

    dStart = datetime.strptime(start_date, '%m/%d/%Y')
    dEnd = datetime.strptime(end_date, '%m/%d/%Y')
    diff = dEnd - dStart
    total_days = diff.days
    num_api_calls = math.ceil(total_days/max_date_range)
    listStartEndTuples = list()
    currStart = dStart
    for i in range(num_api_calls):
        start = currStart
        # Have to do minus 1 since the range from start to end is inclusive for both
        end = currStart + timedelta(days=max_date_range-1)

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
