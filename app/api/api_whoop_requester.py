"""
Makes the direct calls to the Whoop API

Generally, each method receives the parameters to add to the API request, 
makes the request, and returns the API response
"""

import requests
from datetime import datetime
from app.api import whoop_urls
from app.database import db_functions, sql_statements as sql


def getDaysSince(whoopAthleteId, since_date):
    valid_token = getValidTokenForAthlete(whoopAthleteId)
    headers = getAPIRequestHeaders(valid_token)
    return requests.get(whoop_urls.WHOOP_DAYS_URL(whoopAthleteId, since_date, datetime.now()),
                        headers=headers)

def getHeartRate(whoopAthleteId, start_date, end_date):
    valid_token = getValidTokenForAthlete(whoopAthleteId)
    headers = getAPIRequestHeaders(valid_token)
    return requests.get(whoop_urls.WHOOP_HEART_RATE_URL(whoopAthleteId, start_date, end_date),
                        headers=headers)


def getAPIRequestHeaders(valid_token):
    if valid_token is None:
        raise Exception("Authorization token is None.")

    return {'host': whoop_urls.get_api_host(), 'content-type': 'application/json',
           'Authorization': 'Bearer {}'.format(valid_token)}


def getValidTokenForAthlete(whoopAthleteId):
    auth_token = db_functions.dbSelect(
        sql.getAuthorizationTokenSQL(whoopAthleteId))
    return auth_token[0].authorizationToken
