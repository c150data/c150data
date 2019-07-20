"""
Handles the functions necessary to display the hours table.
Eventually, when more fields and statistics are added to this
'ranking' page, this module will have to be broken up further
"""
from app import db, log
from app.database import db_functions, db_filler, sql_statements as sql, db_updater
from app.api import api_requester
from app.db_models import Athlete
import operator
from datetime import datetime, timedelta

# Workouts will be refreshed when they are 30 minutes old or older
REFRESH_WORKOUT_MINUTES = 30


# The 'changed since' date that is used when the last_updated_workouts field
# in the athletes table is None. The use cases for this are something like:
# - The athletes table was cleared and reinserted, so all of the last_updated_workouts values are None
# - New athletes are added to the coach
# - Previously inactive athletes are now active
# Ask Ben about this??
DEFAULT_LAST_UPDATED_TIME = datetime.utcnow() - timedelta(days=14)


def getHoursForAllAthletes(start_date, end_date):
    """
    Main driver function for getting the hours table

    Arguments:
        start_date {str} -- Formatted MM/DD/YYYY
        end_date {str} -- Formatted MM/DD/YYYY

    Returns:
        List -- Sorted list of objects, with each object representing an athlete
        with a name, number of hours (between the given dates), and number of rounded
        hours to be used by the UI
    """
    # Update workouts if they are old
    updateWorkoutsIfNecessary()

    # Run SQL query against DB for hours
    result = db_functions.dbSelect(sql.getAllHoursSQL(start_date, end_date))

    # Parses sql rows into list of objects formatted for UI
    athleteHourList = list()
    for row in result:
        athlete_info = {
            "rank": 0,
            "name": row['name'],
            "hours": row['hours'],
            "rounded_hours": round(row['hours'], 2)
        }
        athleteHourList.append(athlete_info)
    sortedAthleteHourList = sorted(
        athleteHourList, key=operator.itemgetter('hours'), reverse=True)
    rank = 1
    for athlete in sortedAthleteHourList:
        log.info(athlete)
        athlete["rank"] = rank
        rank+=1
    return sortedAthleteHourList


def updateWorkoutsIfNecessary():
    """
    Checks if the workouts need to be updated, and if so updates them.
    """
    lastUpdatedTime = db_functions.dbSelect(sql.getOldestLastWorkoutTimeSQL())[
        0]['last_updated_workouts']
    if lastUpdatedTime is None:
        lastUpdatedTime = DEFAULT_LAST_UPDATED_TIME  # Use default datetime if None
    else:
        lastUpdatedTime = datetime.strptime(
            lastUpdatedTime, "%Y-%m-%d %H:%M:%S.%f")  # Format time
    needToUpdate = hasExpired(lastUpdatedTime)
    if needToUpdate:
        updateWorkouts(lastUpdatedTime)
        updateAthletesWorkoutsTime()


def hasExpired(lastUpdatedTime):
    if lastUpdatedTime is None:
        return True  # Workouts have never been updated, so update them

    # Update workouts if they have not been updated in the past x minutes, where x = REFRESH_WORKOUT_MINUTES
    return (datetime.utcnow() > lastUpdatedTime + timedelta(minutes=REFRESH_WORKOUT_MINUTES))


def updateWorkouts(lastUpdatedTime):
    """
    Driver for updating workouts in the database

    Arguments:
        lastUpdatedTime {datetime} -- Will check for changes in workouts between this date and now, and
        update the database accordingly
    """
    log.info("Updating workouts...")

    active_athletes = db_functions.dbSelect(sql.getAllActiveAthletesSQL())

    total_num_deleted, total_num_modified = 0, 0
    for athlete in active_athletes:
        api_response = api_requester.getWorkoutsChangedSince(
            athlete['id'], lastUpdatedTime)
        num_deleted, num_modified = db_updater.processWorkoutUpdateJSON(
            api_response.json())
        total_num_deleted += num_deleted
        total_num_modified += num_modified

    log.info("Deleted {num_deleted} workouts and modified {num_modified} workouts since {lastUpdatedTime}."
             .format(total_num_deleted=total_num_deleted, total_num_modified=total_num_modified, lastUpdatedTime=lastUpdatedTime))


def updateAthletesWorkoutsTime():
    """
    Update the last_updated_workouts field in the athletes table for all active athletes.
    This method is called directly after updating workouts
    """
    active_athletes = Athlete.query.filter_by(is_active=True).all()
    for athlete in active_athletes:
        athlete.last_updated_workouts = datetime.utcnow()  # Note: UTC time needs to be used here, that is what we are using for updating workouts time
    db.session.commit()
