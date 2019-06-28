import requests
from app import constants, helpers


def getAthletes(valid_token):
    headers = getAPIRequestHeaders(valid_token)
    if headers is None:
        return None
    return requests.get(constants.COACH_ATHLETES_URL, headers=headers)


def getWorkoutsForAthlete(valid_token, id, start_date, end_date):
    headers = getAPIRequestHeaders(valid_token)
    if headers is None:
        return None

    url = constants.WORKOUTS_FOR_ATHLETE_START_END(
        id, start_date, end_date)
    return requests.get(url, headers=headers)


def getAPIRequestHeaders(valid_token):
    if valid_token is not None:
        return {'host': 'api.sandbox.trainingpeaks.com', 'content-type':
                'application/json', 'Authorization': 'Bearer ' + valid_token.access_token}
    return None
