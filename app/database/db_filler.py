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
    datesList = getListOfStartEndDates(start_date, end_date)
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


