

from app import log, db
from app.api import whoop_urls
from app.database import db_functions, sql_statements as sql
from app.database.db_models import WhoopAthlete
from datetime import datetime,timedelta
import requests
from requests import exceptions
import json

token_url = whoop_urls.get_whoop_token_url()
offset = 300  # 300 Second offset, 5 minutes padding time for getting a new token

def refreshTokenIfNeeded(whoopAthleteId):
    whoop_athlete = WhoopAthlete.query.filter_by(whoopAthleteId=whoopAthleteId).first()

    if whoop_athlete is None:
        raise Exception("Error while getting athlete with id {} from database".format(whoopAthleteId))

    token_expires_date = whoop_athlete.expires_at

    if token_expires_date is None or token_expires_date < datetime.now():
        getAndInsertNewToken(whoop_athlete.whoopAthleteId, whoop_athlete.username, whoop_athlete.password)


def getAndInsertNewToken(whoopAthleteId, whoopUsername, whoopPassword):
    response = requests.post(token_url, json=getTokenAuthJson(whoopUsername, whoopPassword))

    if response.status_code == 403:
        raise Exception("Error getting new token for athlete {}. Probably they changed their password or username.".format(whoopAthleteId))

    if response.status_code != 200:
        raise Exception("Error getting new token for athlete {}. Status code was: {}".format(whoopAthleteId, response.status_code))

    r_json = response.json()
    new_auth_token = r_json.get("access_token")
    new_expires_at = datetime.now() + timedelta(seconds=r_json.get("expires_in")) - timedelta(seconds=offset)  # Subtracting offset from the date

    whoop_athlete = WhoopAthlete.query.filter_by(whoopAthleteId=whoopAthleteId).first()
    whoop_athlete.authorizationToken = new_auth_token
    whoop_athlete.expires_at = new_expires_at
    db.session.commit()


def getInfoForNewAthlete(username, password):
    response = requests.post(token_url, json=getTokenAuthJson(username, password))

    if response.status_code == 403:
        raise ValueError("Athlete not found. Incorrect username or password value for athlete.")

    if response.status_code != 200:
        raise exceptions.BaseHTTPError("Error getting information for athlete with username {}. Status code was {}".format(username, response.status_code))

    r_json = response.json()
    athlete_info = {
        'whoopAthleteId': r_json.get('user').get('id'),
        'firstName': r_json.get('user').get('firstName'),
        'lastName': r_json.get('user').get('lastName'),
        'token': r_json.get('access_token'),
        'expiresAt': datetime.now() + timedelta(seconds=r_json.get('expires_in')) - timedelta(seconds=offset)
    }

    return athlete_info 


def getTokenAuthJson(username, password):
    return {
       "grant_type":  "password", 
       "username": username,
       "password": password
    }



