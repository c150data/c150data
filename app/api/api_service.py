"""
Contains methods that handle getting large amounts of similar data using
the TrainingPeaks API.

Generally, will make one or several API requests, and parses the response
into database objects.
"""
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
    """
    athletes_response = api_requester.getAthletes()

    # Parse response into Athlete db objects
    athletes_to_return = list()
    for athlete in athletes_response.json():
        athletes_to_return.append(
            athlete_mapper.getAthleteObjectFromJSON(athlete))

    return athletes_to_return


def getDBWorkoutsUsingAPI(athlete_id, date_period_tuple):
    """
    Makes an API call to get all workouts for a given athlete between
    two given dates. The inputted date period should be no more than
    45 days in length.

    Arguments:
        athlete_id {int} -- athlete identifier
        date_period_tuple {tuple} -- containing the correctly formatted start and end date}

    Returns:
        List of Workout db.Model objects
    """
    start_date, end_date = date_period_tuple
    workouts_json = api_requester.getWorkoutsForAthlete(athlete_id, start_date, end_date).json()
    dbWorkoutsList = list()
    for workout_j in workouts_json:
        dbWorkoutsList.append(workout_mapper.getWorkoutObjectFromJSON(workout_j))
    return dbWorkoutsList