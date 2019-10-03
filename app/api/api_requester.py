"""
Makes the direct calls to the TrainingPeaks API

Generally, each method receives the parameters to add to the API request,
makes the request, and returns the API response
"""
import requests
from app.api import urls, oauth
from app import log

PAGE_SIZE = 50


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
    except Exception:
        # Invalid response that is not able to be jsonified
        return None


def getWorkoutsChangedSince(athlete_id, sinceDate):
    valid_token = oauth.getValidAuthToken()
    headers = getAPIRequestHeaders(valid_token)
    base_url = urls.WORKOUTS_CHANGED_SINCE(athlete_id, sinceDate)
    params = dict()
    params['includeDescription'] = True
    params['pageSize'] = PAGE_SIZE
    params['page'] = 0
    full_response = {
        'Deleted': [],
        'Modified': []
    }
    while True:
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code == 200:
            try:
                response_json = response.json()
                full_response['Deleted'] = full_response['Deleted'] + response_json['Deleted']
                full_response['Modified'] = full_response['Modified'] + response_json['Modified']
            except Exception:
                print('Error while parsing workouts changed response')
            if len(response_json['Modified']) < PAGE_SIZE:
                break
            else:
                params['page'] += 1
        else:
            log.info('NOTE: athlete with id {} does not have a TP premium account. We should deactivate this athlete.'.format(athlete_id))
            break
    return full_response



def getZonesForWorkout(athlete_id, workout_id):
    if athlete_id is None or workout_id is None:
        return None
    valid_token = oauth.getValidAuthToken()
    headers = getAPIRequestHeaders(valid_token)
    base_url = urls.ZONES_FOR_ATHLETE_WORKOUT(athlete_id, workout_id)
    response = requests.get(base_url, headers=headers)
    try:
        return response.json()
    except Exception:
        # Invalid response that is not able to be jsonified
        return None


def getAPIRequestHeaders(valid_token):
    if valid_token is None:
        raise Exception("Authentication token is None.")

    return {'host': urls.get_api_host(), 'content-type':
            'application/json', 'Authorization': 'Bearer ' + valid_token.access_token, 'User-Agent': 'columbiac150'}
