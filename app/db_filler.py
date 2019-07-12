from app import db_helper, api_helper, oauth_helper, log
from app.models import Athlete, Workout
from datetime import datetime, timedelta
import math

# Insert athletes in DB


def insertAllAthletesIntoDB():
    """
    Inserts all athletes into an empty athletes table in the database

    Returns:
        int: Number of athletes successfully inserted
        None: On error
    """
    athletesList = getAllAthletesUsingAPI()
    success = db_helper.dbInsert(athletesList)
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
    athletes_response = api_helper.getAthletes(
        oauth_helper.getValidAuthToken())

    # Error check
    if athletes_response is None:
        return None

    # Parse reponse into Athlete db objects
    athletes_to_return = list()
    for athlete in athletes_response.json():
        athletes_to_return.append(
            db_helper.getAthleteObjectFromJSON(athlete))

    return athletes_to_return


# Insert Workouts into database

def insertWorkoutsIntoDb(start_date, end_date):
    try:
        id_list = get_ids(getAllActiveAthletes())
        datesList = getListOfStartEndDates(start_date, end_date)
        log.info("Dates List: {dates}", dates=datesList)
        workoutsList = list()

        for id in id_list:
            for date_period in datesList:
                workoutsList += getListOfWorkoutsForAthletesFromAPI(
                    id, date_period)

        result = db_helper.dbInsert(workoutsList)
        if result:
            return len(workoutsList)
        else:
            return None
    except Exception as e:
        raise Exception("Error while inserting workouts into database: {error}".format(error=e))
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


def getListOfWorkoutsForAthletesFromAPI(athlete_id, date_period_tuple):
    start_date, end_date = date_period_tuple
    workouts_json = api_helper.getWorkoutsForAthlete(
        oauth_helper.getValidAuthToken(), athlete_id, start_date, end_date).json()
    dbWorkoutsList = list()
    for workout_j in workouts_json:
        dbWorkoutsList.append(db_helper.getWorkoutObjectFromJSON(workout_j))
    log.info("{} workouts found for athlete {} from {} to {}".format(
        len(dbWorkoutsList), athlete_id, start_date, end_date))
    return dbWorkoutsList


def processWorkoutUpdateJSON(workout_update_json):
    try:
        deleted_workouts = workout_update_json['Deleted']
        numDeleted, numModified = 0, 0
        if deleted_workouts is not None and len(deleted_workouts) > 0:
            numDeleted = processDeletedWorkouts(deleted_workouts)
        modified_workouts = workout_update_json['Modified']
        if modified_workouts is not None and len(modified_workouts) > 0:
            numModified = processModifiedWorkouts(modified_workouts)
        return numDeleted, numModified
    except Exception as e:
        log.error("Error occured while processing workout updates : {error}".format(error=e))
        return None


def processDeletedWorkouts(deleted_workouts):
    workoutsToDelete = list()
    for workout_id in deleted_workouts:
        workout = Workout.query.filter_by(id=workout_id)
        workoutsToDelete.append(workout)
    db_helper.dbDelete(workoutsToDelete)
    return len(workoutsToDelete)


def processModifiedWorkouts(modified_workouts):
    workoutsToInsert = list()
    for modified_workout in modified_workouts:
        workoutsToInsert.append(updateWorkout(modified_workout))
    db_helper.dbInsert(workoutsToInsert)
    return len(workoutsToInsert)


def updateWorkout(workout_json):
    if Workout.query.filter_by(id=workout_json['Id']) is None:
        # Workout does not exist in DB
        return db_helper.getWorkoutObjectFromJSON(workout_json)
    else:
        # Workout already exists in db, need to first delete existing then return new one to insert
        Workout.query.filter_by(id=workout_json['Id']).delete()
        return db_helper.getWorkoutObjectFromJSON(workout_json)


def getAllActiveAthletes():
    return Athlete.query.filter_by(is_active=True).all()
