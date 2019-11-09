"""
Handles getting alrge amounts of similar data using the Whoop API.

Generally, will make one or more Whoop API requests and parse the response into 
the respective database objects
"""
from app import log
from app.api import api_whoop_requester
from datetime import datetime
from dateutil.parser import parse
from app.database.db_models import WhoopDay, WhoopStrain, WhoopWorkout

def getDBObjectsForDays(whoopAthleteId, start_date, end_date):
    days_response = api_whoop_requester.getDays(whoopAthleteId, start_date, end_date)

    if days_response.status_code != 200:
        raise Exception('Whoop API returned status code: {}'.format(days_response.status_code))
    
    response_json = days_response.json()
    day_db_objects = list()
    strain_db_objects = list()
    workout_db_objects = list()

    for day in response_json:
        day_dt = datetime.strptime(day.get('days')[0], '%Y-%m-%d')
        curr_day = WhoopDay(
            whoopDayId=day.get('id'),
            whoopAthleteId=whoopAthleteId,
            day=day_dt
        )
        day_db_objects.append(curr_day)

        curr_strain = buildStrainDbObject(day)
        strain_db_objects.append(curr_strain)

        for workout in day.get('strain').get('workouts'):
            curr_workout = buildWorkoutDbObject(day.get('id'), workout)
            workout_db_objects.append(curr_workout)

    return day_db_objects, strain_db_objects, workout_db_objects
    

def buildStrainDbObject(day_json):
    strain_json = day_json.get('strain')
    return WhoopStrain(
        whoopDayId=day_json.get('id'),
        averageHeartRate=strain_json.get('averageHeartRate'),
        kilojoules=strain_json.get('kilojoules'),
        maxHeartRate=strain_json.get('maxHeartRate'),
        score=strain_json.get('score')
    )


def buildWorkoutDbObject(whoopDayId, workout_json):
    start_time_str = workout_json.get('during').get('lower')
    end_time_str = workout_json.get('during').get('upper')
    start_time_dt = parse(start_time_str)
    end_time_dt = parse(end_time_str)

    return WhoopWorkout(
        workoutId=workout_json.get('id'),
        whoopDayId=whoopDayId,
        startTime=start_time_dt,
        endTime=end_time_dt,
        kilojoules=workout_json.get('kilojoules'),
        averageHeartRate=workout_json.get('averageHeartRate'),
        maxHeartRate=workout_json.get('maxHeartRate'),
        sportId=workout_json.get('sportId'),
        timeZoneOffset=workout_json.get('timeZoneOffset')
    )