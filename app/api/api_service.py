from app.api import api_requester
from app.database import db_functions
from app.mappers import athlete_mapper, workout_mapper
from datetime import datetime, timedelta
import math

def getDBAthletesUsingAPI():
    """
    Makes an API call to get every athlete under the current coach

    Returns:
        List of Athlete db.Model objects.
        None on error.
    """
    athletes_response = api_requester.getAthletes()

    # Parse response into Athlete db objects
    athletes_to_return = list()
    for athlete in athletes_response.json():
        athletes_to_return.append(
            athlete_mapper.getAthleteObjectFromJSON(athlete))

    return athletes_to_return


def getDBWorkoutsUsingAPI(athlete_id, date_period_tuple):
    start_date, end_date = date_period_tuple
    workouts_json = api_requester.getWorkoutsForAthlete(athlete_id, start_date, end_date).json()
    dbWorkoutsList = list()
    for workout_j in workouts_json:
        dbWorkoutsList.append(workout_mapper.getWorkoutObjectFromJSON(workout_j))
    return dbWorkoutsList


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