import requests
from app.api import urls, oauth


def getAthletes():
    valid_token = oauth.getValidAuthToken()
    headers = getAPIRequestHeaders(valid_token)
    return requests.get(urls.COACH_ATHLETES_URL, headers=headers)


def getWorkoutsForAthlete(id, start_date, end_date):
    valid_token = oauth.getValidAuthToken()
    headers = getAPIRequestHeaders(valid_token)

    params = dict()
    params['includeDescription'] = True
    base_url = urls.WORKOUTS_FOR_ATHLETE_START_END(
        id, start_date, end_date)
    return requests.get(base_url, headers=headers, params=params)


def getWorkoutsChangedSince(athlete_id, sinceDate):
    valid_token = oauth.getValidAuthToken()
    headers = getAPIRequestHeaders(valid_token)
    base_url = urls.WORKOUTS_CHANGED_SINCE(athlete_id, sinceDate)
    params = dict()
    params['includeDescription'] = True
    # TODO ask Ben about pageSize and page
    params['pageSize'] = 100
    params['page'] = 0
    return requests.get(base_url, headers=headers, params=params)


def getAPIRequestHeaders(valid_token):
    if valid_token is None:
        raise Exception("Authentication token is None.")

    return {'host': 'api.sandbox.trainingpeaks.com', 'content-type':
            'application/json', 'Authorization': 'Bearer ' + valid_token.access_token}

