from app import db, log, sql_statements as sql, db_helper, api_helper, db_filler
from app.models import Athlete
import operator
from datetime import datetime, timedelta

REFRESH_WORKOUT_MINUTES = 30
DEFAULT_LAST_UPDATED_TIME = datetime.utcnow() - timedelta(days=14)


def getHoursForAllAthletes(start_date, end_date):
    try:
        updateWorkoutsIfNecessary()
        result = db_helper.dbSelect(sql.getAllHoursSQL(start_date, end_date))
        if result is None:
            raise Exception("Hours query returned None.")
    except Exception as e:
        raise Exception("Error occured while getting hours: {error}".format(error=e))

    athleteHourList = list()
    for row in result:
        athlete_info = {
            "name": row['name'],
            "hours": row['hours'],
            "rounded_hours": round(row['hours'], 2)
        }
        athleteHourList.append(athlete_info)
    sortedAthleteHourList = sorted(
        athleteHourList, key=operator.itemgetter('hours'), reverse=True)
    return sortedAthleteHourList


def updateWorkoutsIfNecessary():
    lastUpdatedTime = db_helper.dbSelect(sql.getOldestLastWorkoutTimeSQL())[0]['last_updated_workouts']
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
    athletes = db_helper.dbSelect(sql.getAllActiveAthletesSQL())
    num_deleted, num_modified = 0, 0
    for athlete in athletes:
        api_response = api_helper.getWorkoutsChangedSince(
            athlete['id'], lastUpdatedTime)
        curr_num_deleted, curr_num_modified = db_filler.processWorkoutUpdateJSON(api_response.json())
        num_deleted += curr_num_deleted
        num_modified += curr_num_modified
    log.info("Deleted {num_deleted} workouts and modified {num_modified} workouts.".format(num_deleted=num_deleted, num_modified=num_modified))


def updateAthletesWorkoutsTime():
    active_athletes = Athlete.query.filter_by(is_active=True).all()
    for athlete in active_athletes:
        athlete.last_updated_workouts = datetime.utcnow()
    db.session.commit()
