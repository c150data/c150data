"""
Handles the functions necessary to display the hours table.
Eventually, when more fields and statistics are added to this
'ranking' page, this module will have to be broken up further
"""
from app import db, log
from app.data.utils import getZonePercents, getTpScore
from app.api.utils import InvalidZoneAthletes
from app.database import db_functions, db_filler, sql_statements as sql, db_updater
from app.api import api_requester
from app.database.db_models import Athlete
import operator
from datetime import datetime, timedelta, date

# Workouts will be refreshed when they are 30 minutes old or older
REFRESH_WORKOUT_MINUTES = 30


# The 'changed since' date that is used when the last_updated_workouts field
# in the athletes table is None. The use cases for this are something like:
# - The athletes table was cleared and reinserted, so all of the last_updated_workouts values are None
# - New athletes are added to the coach
# - Previously inactive athletes are now active
# Ask Ben about this??
# DEFAULT_LAST_UPDATED_TIME = datetime(year=2014, month=1, day=1) 
DEFAULT_LAST_UPDATED_TIME = datetime(year=2019, month=11, day=4) 


def getHoursForAllAthletes(start_date, end_date):
    """
    Main driver function for getting the hours table

    Arguments:
        start_date {str} -- Formatted MM/DD/YYYY
        end_date {str} -- Formatted MM/DD/YYYY

    Returns:
        JSON object - Json object with an array of athletes, along with their hours, and
        the total number of hours for all athletes.
    """

    # Run SQL query against DB for hours
    result = db_functions.dbSelect(sql.getAllHoursSQL(start_date, end_date))
    prescribed = db_functions.dbSelect(sql.getPrescribedDataSQL(start_date, end_date))[0]
    if result is None:
        raise Exception("Get data call returned none.")

    # Parses sql rows into list of objects formatted for UI
    athleteHourList = list()
    rank = 1
    total_hours = 0
    # List of lists with each inner list containing sum of all percentages and number of percentages, so at the end can determine average
    zoneAverages = [
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0]
    ]
    tp_scores = list()

    for row in result:
        hr_zones, power_zones = getZonePercents(row)
        if len(prescribed) == 0:
            tp_score = getTpScore(row, None)
        else:
            tp_score = getTpScore(row, prescribed)
        tp_scores.append(tp_score)
        athlete_info = {
            "rank": rank,
            "name": row['name'],
            "zone1": hr_zones['hrZone1Percent'],
            "zone2": hr_zones['hrZone2Percent'],
            "zone3": hr_zones['hrZone3Percent'],
            "zone4": hr_zones['hrZone4Percent'],
            "zone5": hr_zones['hrZone5Percent'],
            "rounded_hours": row['hours'],
            "tp_score": round(tp_score, 0)
        }
        if(hr_zones['hrZone1Percent'] is not '-'):
            zoneAverages[0][0] += hr_zones['hrZone1Percent']
            zoneAverages[0][1] += 1
        if(hr_zones['hrZone2Percent'] is not '-'):
            zoneAverages[1][0] += hr_zones['hrZone2Percent']
            zoneAverages[1][1] += 1
        if(hr_zones['hrZone3Percent'] is not '-'):
            zoneAverages[2][0] += hr_zones['hrZone3Percent']
            zoneAverages[2][1] += 1
        if(hr_zones['hrZone4Percent'] is not '-'):
            zoneAverages[3][0] += hr_zones['hrZone4Percent']
            zoneAverages[3][1] += 1
        if(hr_zones['hrZone1Percent'] is not '-'):
            zoneAverages[4][0] += hr_zones['hrZone5Percent']
            zoneAverages[4][1] += 1
        athleteHourList.append(athlete_info)
        hours = row['hours']
        if hours:
            total_hours += row['hours']
        rank += 1

    avgZone1 = round(zoneAverages[0][0]/zoneAverages[0][1], 1) if zoneAverages[0][1] is not 0 else None
    avgZone2 = round(zoneAverages[1][0]/zoneAverages[1][1], 1) if zoneAverages[1][1] is not 0 else None
    avgZone3 = round(zoneAverages[2][0]/zoneAverages[2][1], 1) if zoneAverages[2][1] is not 0 else None
    avgZone4 = round(zoneAverages[3][0]/zoneAverages[3][1], 1) if zoneAverages[3][1] is not 0 else None
    avgZone5 = round(zoneAverages[4][0]/zoneAverages[4][1], 1) if zoneAverages[4][1] is not 0 else None
    avgTpScore = round(sum(tp_scores)/len(tp_scores), 0)
    jsonToReturn = {
        "athlete_list": athleteHourList,
        "total_hours": round(total_hours, 2),
        "average_tp_score": avgTpScore,
        "average_zones": {
            "avgZone1": avgZone1,
            "avgZone2": avgZone2,
            "avgZone3": avgZone3,
            "avgZone4": avgZone4,
            "avgZone5": avgZone5
        }
    }
    return jsonToReturn


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
        response_json = api_requester.getWorkoutsChangedSince(
            athlete['id'], lastUpdatedTime)
        num_deleted, num_modified = db_updater.processWorkoutUpdateJSON(response_json)
        total_num_deleted += num_deleted
        total_num_modified += num_modified

    log.info("Wrong num HR zones: {}".format(InvalidZoneAthletes.wrongNumHrZones))
    log.info("Wrong num power zones: {}".format(InvalidZoneAthletes.wrongNumPowerZones))
    log.info("Reverse HR zones: {}".format(InvalidZoneAthletes.reverseHrZones))
    log.info("Reverse Power zones: {}".format(InvalidZoneAthletes.reversePowerZones))
    log.info("Deleted {num_deleted} workouts and modified {num_modified} workouts since {lastUpdatedTime}."
             .format(num_deleted=total_num_deleted, num_modified=total_num_modified, lastUpdatedTime=lastUpdatedTime))


def updateAthletesWorkoutsTime():
    """
    Update the last_updated_workouts field in the athletes table for all active athletes.
    This method is called directly after updating workouts
    """
    active_athletes = Athlete.query.filter_by(is_active=True).all()
    for athlete in active_athletes:
        # Note: UTC time needs to be used here, that is what we are using for updating workouts time
        athlete.last_updated_workouts = datetime.utcnow()
    db.session.commit()
