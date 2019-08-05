"""
Makes the direct calls to the TrainingPeaks API

Generally, each method receives the parameters to add to the API request,
makes the request, and returns the API response
"""
import requests
from app.api import urls, oauth
from app import log


def getAthletes():
    valid_token = oauth.getValidAuthToken()
    headers = getAPIRequestHeaders(valid_token)
    return requests.get(urls.COACH_ATHLETES_URL(), headers=headers)


def getWorkoutsForAthlete(id, start_date, end_date):
    valid_token = oauth.getValidAuthToken()
    headers = getAPIRequestHeaders(valid_token)

    params = dict()
    params['includeDescription'] = True
    base_url = urls.WORKOUTS_FOR_ATHLETE_START_END(
        id, start_date, end_date)
    response = requests.get(base_url, headers=headers, params=params)
    try:
        return response.json()
    except Exception as e:
        # Invalid response that is not able to be jsonified
        return None


def getWorkoutsChangedSince(athlete_id, sinceDate):
    valid_token = oauth.getValidAuthToken()
    headers = getAPIRequestHeaders(valid_token)
    base_url = urls.WORKOUTS_CHANGED_SINCE(athlete_id, sinceDate)
    params = dict()
    # TODO fix this so it pages correctly. It should make an API call until the size of the returned JSON is less than the page size
    # Ask Ben about exactly what the page size signifies. Is it the number of workouts in the modified array or deleted array or both combined?
    params['includeDescription'] = True
    params['pageSize'] = 100
    params['page'] = 0
    return requests.get(base_url, headers=headers, params=params)


def getZonesForWorkout(athlete_id, workout_id):
    if athlete_id is None or workout_id is None:
        return None
    valid_token = oauth.getValidAuthToken()
    headers = getAPIRequestHeaders(valid_token)
    base_url = urls.ZONES_FOR_ATHLETE_WORKOUT(athlete_id, workout_id)
    response = requests.get(base_url, headers=headers)
    try:
        return response.json()
    except Exception as e:
        # Invalid response that is not able to be jsonified
        return None


def getAPIRequestHeaders(valid_token):
    if valid_token is None:
        raise Exception("Authentication token is None.")

    return {'host': 'api.sandbox.trainingpeaks.com', 'content-type':
            'application/json', 'Authorization': 'Bearer ' + valid_token.access_token, 'User-Agent': 'columbiac150'}
