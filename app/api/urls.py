"""
Module used to build the urls to make API requests to
"""
from app import app

is_production = app.config['TP_SERVER'] == 'production'

api_base_url = 'https://api.trainingpeaks.com' if is_production else 'https://api.sandbox.trainingpeaks.com' 
api_host =  'api.trainingpeaks.com' if is_production else 'api.sandbox.trainingpeaks.com' 
oauth_base_url = 'https://oauth.trainingpeaks.com' if is_production else 'https://oauth.sandbox.trainingpeaks.com'


def get_api_base_url():
    return api_base_url

def get_api_host():
    return api_host


def token_url():
    return "{}/oauth/token".format(oauth_base_url) 


def authorization_url():
    return '{}/OAuth/Authorize'.format(oauth_base_url)


def COACH_ATHLETES_URL():
    return '{}/v1/coach/athletes'.format(api_base_url)


def WORKOUTS_FOR_ATHLETE_START_END(athlete_id, start, end):
    return '{}/v1/workouts/{}/{}/{}'.format(api_base_url, athlete_id, start, end)


def WORKOUTS_CHANGED_SINCE(athlete_id, sinceDate):
    # Date in URL must be formatted like: 2017-10-01T00:00:00.00000Z
    formattedDate = sinceDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return '{}/v1/workouts/{}/changed?date={}'.format(api_base_url, athlete_id, formattedDate)


def ZONES_FOR_ATHLETE_WORKOUT(athlete_id, workout_id):
    return '{}/v1/workouts/{}/id/{}/timeinzones'.format(api_base_url, athlete_id, workout_id)
