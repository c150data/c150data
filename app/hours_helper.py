from app import db, log, sql_statements as sql, db_helper
from app.models import Athlete
import operator
from datetime import datetime

REFRESH_WORKOUT_MINUTES = 30
DEFAULT_LAST_UPDATED_TIME = datetime.now() - timedelta(days = 7)


def getHoursForAllAthletes(start_date, end_date):
    # Try block for error checking
    updateWorkoutsIfNecessary()
    result = db.session.execute(sql.getAllHoursSQL(start_date, end_date))
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
    return len(sortedAthleteHourList), sortedAthleteHourList


def updateWorkoutsIfNecessary():
    # Uses the lastUpdatedTime date from workoutsHaveExpired and passes that to updateWorkouts
    # May have to refactor the line below
    lastUpdatedTime = db.session.execute(sql.getOldestLastWorkoutTimeSQL())[
        0]['last_updated_workouts']
    # Format lastUpdatedTime??? if so, do it here and should match: 2017-10-01T00:00:00.00000Z
    needToUpdate = hasExpired(lastUpdatedTime)
    if needToUpdate:
        updateWorkouts(lastUpdatedTime)
        updateAthletesWorkoutsTime()


def hasExpired(lastUpdatedTime):
    if lastUpdatedTime is None:
        # Update workouts if the last_updated_workouts has never been set (workouts have never been updated)
        return True
    return (datetime.now() > lastUpdatedTime + timedelta(minutes=REFRESH_WORKOUT_MINUTES))


def updateWorkouts(lastUpdatedTime):
    # For every active athlete, make an api call to workouts/changed?date={date}
    # Then, process every api response by updating the respective workouts
    if lastUpdatedTime = None:
        lastUpdatedTime = DEFAULT_LAST_UPDATED_TIME
    athlete_ids = db.session.execute(sql.getAllActiveAthleteIdsSQL())
    for athlete_id in athlete_ids:
        api_response = api_helper.workoutsChangedSince(
            athlete_id, lastUpdatedTime)
        db_helper.processWorkoutUpdateJSON(api_response)


def updateAthletesWorkoutsTime():
    # For every active athlete, update the last_updated_workouts field to datetime.now()
    active_athletes = Athlete.query.filter_by(is_active=True).all()
    for athlete in active_athletes:
        athlete.last_updated_workouts = datetime.now()
    db.session.commit()
