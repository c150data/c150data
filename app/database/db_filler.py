from app import log
from app.db_models import Athlete, Workout
from app.database import db_functions, sql_statements as sql
from app.api import api_requester, oauth, api_service


def insertAllAthletesIntoDB():
    """
    Inserts all athletes into an empty athletes table in the database

    Returns:
        int: Number of athletes successfully inserted, -1 if unsuccessful
    """
    athletesList = api_service.getDBAthletesUsingAPI()
    result = db_functions.dbInsert(athletesList)
    return len(athletesList) if result else -1


def insertWorkoutsIntoDb(start_date, end_date):
    """
    Inserts all workouts from start_date to end_date into workout table
    
    Args:
        start_date (datetime): Start Datetime object
        end_date (datetime): End Datetime object 
    
    Returns:
        int: number of workouts inserted into the database, -1 if unsuccessful
    """
    athletes = db_functions.dbSelect(sql.getAllActiveAthletesSQL()) 
    datesList = api_service.getListOfStartEndDates(start_date, end_date)
    workoutsList = list()

    for athlete in athletes:
        numWorkouts = 0
        for date_period in datesList:
            workoutsList += api_service.getDBWorkoutsUsingAPI(
                athlete.id, date_period)
            numWorkouts += len(workoutsList)
        log.info("{} workouts found for {} from {} to {}".format(numWorkouts, athlete['name'], start_date, end_date))

    result = db_functions.dbInsert(workoutsList)
    return len(workoutsList) if result else -1 



