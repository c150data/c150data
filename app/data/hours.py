from app import db, log
from app.database import db_functions, db_filler, sql_statements as sql, db_updater
from app.api import api_requester
from app.db_models import Athlete
import operator
from datetime import datetime, timedelta

REFRESH_WORKOUT_MINUTES = 30
# Ask ben about this
DEFAULT_LAST_UPDATED_TIME = datetime.utcnow() - timedelta(days=14)


def getHoursForAllAthletes(start_date, end_date):
    try:
        updateWorkoutsIfNecessary()
        result = db_functions.dbSelect(sql.getAllHoursSQL(start_date, end_date))
        if result is None:
            raise Exception("Hours query returned None.")
    except Exception as e:
        raise Exception("Error occured while getting hours: {error}".format(error=e))

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
    lastUpdatedTime = db_functions.dbSelect(sql.getOldestLastWorkoutTimeSQL())[0]['last_updated_workouts']
    if lastUpdatedTime is not None:
        # Format time
        lastUpdatedTime = datetime.strptime(lastUpdatedTime, "%Y-%m-%d %H:%M:%S.%f")
    needToUpdate = hasExpired(lastUpdatedTime)
    if needToUpdate:
        updateWorkouts(lastUpdatedTime)
        updateAthletesWorkoutsTime()


def hasExpired(lastUpdatedTime):
    if lastUpdatedTime is None:
        # Workouts have never been updated, so update them
        return True
    # Update workouts if htey have not been updated in the past x minutes, where x = REFRESH_WORKOUT_MINUTES
    return (datetime.utcnow() > lastUpdatedTime + timedelta(minutes=REFRESH_WORKOUT_MINUTES))


def updateWorkouts(lastUpdatedTime):
    log.info("Updating workouts...")
    if lastUpdatedTime is None:
        lastUpdatedTime = DEFAULT_LAST_UPDATED_TIME
    athletes = db_functions.dbSelect(sql.getAllActiveAthletesSQL())
    num_deleted, num_modified = 0, 0
    for athlete in athletes:
        api_response = api_requester.getWorkoutsChangedSince(
            athlete['id'], lastUpdatedTime)
        curr_num_deleted, curr_num_modified = db_updater.processWorkoutUpdateJSON(api_response.json())
        num_deleted += curr_num_deleted
        num_modified += curr_num_modified
    log.info("Deleted {num_deleted} workouts and modified {num_modified} workouts since {lastUpdatedTime}."
        .format(num_deleted=num_deleted, num_modified=num_modified, lastUpdatedTime=lastUpdatedTime))


def updateAthletesWorkoutsTime():
    active_athletes = Athlete.query.filter_by(is_active=True).all()
    for athlete in active_athletes:
        athlete.last_updated_workouts = datetime.utcnow()
    db.session.commit()
