import requests
from app import urls, oauth_helper


def getAthletes(valid_token):
    headers = getAPIRequestHeaders(valid_token)
    if headers is None:
        return None
    return requests.get(urls.COACH_ATHLETES_URL, headers=headers)


def getWorkoutsForAthlete(valid_token, id, start_date, end_date):
    headers = getAPIRequestHeaders(valid_token)
    if headers is None:
        return None

    params = dict()
    params['includeDescription'] = True
    base_url = urls.WORKOUTS_FOR_ATHLETE_START_END(
        id, start_date, end_date)
    return requests.get(base_url, headers=headers, params=params)


def getWorkoutsChangedSince(athlete_id, sinceDate):
    valid_token = oauth_helper.getValidAuthToken()
    headers = getAPIRequestHeaders(valid_token)
    if headers is None:
        return None

    base_url = urls.WORKOUTS_CHANGED_SINCE(athlete_id, sinceDate)
    params = dict()
    params['includeDescription'] = True
    # TODO ask Ben about pageSize and page
    params['pageSize'] = 100
    params['page'] = 0
    return requests.get(base_url, headers=headers, params=params)


def getAPIRequestHeaders(valid_token):
    if valid_token is not None:
        return {'host': 'api.sandbox.trainingpeaks.com', 'content-type':
                'application/json', 'Authorization': 'Bearer ' + valid_token.access_token}
    return None

