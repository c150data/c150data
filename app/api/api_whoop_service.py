"""
Handles getting alrge amounts of similar data using the Whoop API.

Generally, will make one or more Whoop API requests and parse the response into 
the respective database objects
"""
from app import log
from app.api import api_whoop_requester

def getDBObjectsForDay(whoopAthleteId, start_date, end_date):
    days_response = api_whoop_requester.getDays(whoopAthleteId, start_date, end_date)

    if days_response.status_code != 200:
        raise Exception('Whoop API returned status code: {}'.format(days_response.status_code))
    
    response_json = days_response.json()
    db_objects = list()
    num_days = 0
    num_workouts = 0

    # Parse response into the respective WhoopDay, 
    # WhoopStrain, and WhoopWorkout Db objects

    return db_objects, num_days, num_workouts