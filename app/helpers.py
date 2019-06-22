"""
Helper methods for the c150.data data retrieval process
"""

from __future__ import print_function
import pymysql
import datetime
import requests
import operator
from authlib.client import OAuth2Session
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

api_base_url = 'https://api.sandbox.trainingpeaks.com'

# Change these values when running on remote server! These are strictly for development
# TODO create one variable that changes between prod and dev that changes all of this for you
db_host = "localhost"
db_name = "c150data"
db_user = "mamsterdam"
db_passwd = "Columbia150"
db_auth_token_table = "auth_token"

grant_type = "refresh_token"
client_id = 'columbiac150'
client_secret = 'kzSN7CYgZYUMzb8DfhEqRnqrHAqiAEUHOgSAJo8'
refresh_url = "https://oauth.sandbox.trainingpeaks.com/oauth/token"
redirect_uri = "www.c150data.com"



def EXPIRES_PADDING_TIME_SEC():
    return 300 #Edit to change padding time for refresh token


def connectToDB():
    try:
        return pymysql.connect(host=db_host, user=db_user, passwd=db_passwd, db=db_name)
    except:
        print("Connection to database failed")
        return None


"""
Method to insert the passed in token into the database. No expiration date checking needs to be
done here
Return: Boolean, True if successful, False otherwise
"""
def executeTokenInsert(token):
    access_token = token['access_token']
    token_type = token['token_type']
    expires_in = token['expires_in']
    refresh_token = token['refresh_token']
    scope = token['scope']
    # Give the expires_in time an extra 5 minutes as padding time
    expires_at_date = datetime.datetime.now() + datetime.timedelta(seconds=(int(expires_in)-EXPIRES_PADDING_TIME_SEC()))
    expires_at_date = expires_at_date.replace(microsecond=0) # Format date for insertion into DB
    insert_statement = "INSERT INTO {} (`access_token`, `token_type`,`expires_at`, `refresh_token`, `scope`) VALUES ('{}', '{}', '{}', '{}','{}');".format(
            db_auth_token_table, access_token, token_type, expires_at_date, refresh_token, scope)
    select_statement = "SELECT * FROM {} order by token_id desc".format(db_auth_token_table)
    eprint(select_statement)

    success = False 
    conn = connectToDB() 
    if conn is not None:
        try:
            cursor = conn.cursor()
            numRows = cursor.execute(insert_statement)
            if numRows != 1:
                print("Error in inserting token.")
            else:
                success=True
                conn.commit()
            print("Inserted access token with statement: ", insert_statement)
        except: # TODO check for exact error that would be thrown, maybe change how errors are handled
            print("Failed to insert token.")
        finally:
            conn.close()
    return success


def refreshTokenIfNeeded():
    conn = connectToDB()
    cursor = conn.cursor()

    select_st = "SELECT * FROM {} order by token_id desc".format(db_auth_token_table)
    eprint(select_st)
    # TODO wrap in try block
    cursor.execute(select_st)

    row = cursor.fetchone() # Fetches the most recently inserted token
    conn.close()
    refresh_date = row[3] #TODO add constants here

    needsRefreshing = True if refresh_date < datetime.datetime.now() else False

    # update if necessary
    if needsRefreshing:
        print("Refreshing token...")
        refresh_token = row[4] #TODO add constants here
        oauth_session = OAuth2Session(client_id, client_secret, refresh_token=refresh_token)
        body = "grant_type=refresh_token"
        updated_token = oauth_session.refresh_token(refresh_url,
                                                    refresh_token=refresh_token,
                                                    body=body)
        executeTokenInsert(updated_token)
        return updated_token
    else:
        # token does not need to be updated
        return 1 


def getToken():
    # Retruns None on error
    if refreshTokenIfNeeded() is None:
        print("Error: Refresh Token returned None")
        return None

    conn = connectToDB()
    cursor = conn.cursor()

    try:
        select_st = "SELECT * FROM {} order by token_id desc".format(db_auth_token_table)
        num_rows = cursor.execute(select_st)
        if num_rows == 0:
            print("Error: An access token does not exist")
        return cursor.fetchone() # The first toke will be the most recently inserted one 
    except:
        print("Failed to fetch access_token")
    finally:
        conn.close()


def getHeaders():
    access_token = getToken()[1]
    return {'host': 'api.sandbox.trainingpeaks.com','content-type':
            'application/json', 'Authorization': 'Bearer ' + access_token}



def getAthleteId():
    """
    r = requests.get('https://api.sandbox.trainingpeaks.com/v1/athlete/profile',
                     headers=getHeaders())
    id = (r.json())["Id"]
    return id
    """
    pass


def getHoursForAthlete(id, start_date, end_date, headers):
    print("Getting hours for athlete {}...".format(id))
    api_url = api_base_url + '/v1/workouts/{}/{}/{}'.format(id, start_date, end_date)
    response = requests.get(api_url, headers=headers)

    json_response = response.json()
    sum_hours = 0
    for workout in json_response:
        total_time = workout['TotalTime']
        if type(total_time) is float:
            sum_hours += float(total_time)
    return sum_hours



def getAllAthletes(start_date, end_date):
    headers = getHeaders()
    r = requests.get('https://api.sandbox.trainingpeaks.com/v1/coach/athletes',
                     headers=headers)
    athletes = list()
    req_json = r.json()
    # convert inputted dates from MM/DD/YYYY to YYYY-MM-DD
    dStart = datetime.datetime.strptime(start_date, '%m/%d/%Y')
    dEnd = datetime.datetime.strptime(end_date, '%m/%d/%Y')
    start_date_f = dStart.strftime('%Y-%m-%d')
    end_date_f = dEnd.strftime('%Y-%m-%d')
    # Create athlete object and add to list
    count = 1 
    for athlete in req_json:
        eprint("Working on Athlete #", count)
        # date formatted YYYY-MM-DD
        hours = getHoursForAthlete(athlete['Id'],
                                           start_date_f, end_date_f, headers)
        rounded_hours = round(hours, 2)
        athlete_info = {
            "name": "{} {}".format(athlete["FirstName"], athlete["LastName"]),
            "hours": hours,
            "rounded_hours": rounded_hours
        }
        athletes.append(athlete_info)
        count += 1

    # sort list of athletes based on number of hours
    sorted_athletes = sorted(athletes, key=operator.itemgetter('hours'), reverse=True)
    print(sorted_athletes)

    return (len(athletes), sorted_athletes)
