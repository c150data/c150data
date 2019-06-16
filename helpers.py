"""
Helper methods for the c150.data data retrieval process
"""

import MySQLdb
import datetime
import requests
import operator
from authlib.client import OAuth2Session

api_base_url = 'https://api.sandbox.trainingpeaks.com'

db_host = "mysql.c150data.com"
db_name = "c150db"
db_user = "lwtpoodles150"
db_passwd = "Columbia150"

grant_type = "refresh_token"
client_id = 'columbiac150'
client_secret = 'kzSN7CYgZYUMzb8DfhEqRnqrHAqiAEUHOgSAJo8'
refresh_url = "https://oauth.sandbox.trainingpeaks.com/oauth/token"
redirect_uri = "https://localhost:5000"


def connectToDB():
    return MySQLdb.connect(host=db_host, user=db_user, passwd=db_passwd,
                           db=db_name)


def deleteToken(conn=None):
    has_passed_connection = False if conn is None else True
    if has_passed_connection is False:
        conn = connectToDB()

    cursor = conn.cursor()

    cursor.execute("SELECT * from access_token")
    if cursor.rowcount == 1:
        try:
            cursor.execute("DELETE FROM access_token")
            conn.commit()
            print("Deleted expired token")
        except MySQLdb.IntegrityError:
            print("Failed to delete access token row.")
        finally:
            if has_passed_connection is False:
                conn.close()
            return 1

    return None


def executeTokenInsert(token):
    access_token = token['access_token']
    token_type = token['token_type']
    expires_in = token['expires_in']
    refresh_token = token['refresh_token']
    scope = token['scope']
    # Expires in 1 hour, I give it an extra 5 minutes as padding time
    expires_at_date = datetime.datetime.now() + datetime.timedelta(seconds=(int(expires_in)-300))
    expires_at_date = expires_at_date.replace(microsecond=0)
    insert_statement = "INSERT INTO `access_token` (`access_token`, `token_type`,`expires_at`, `refresh_token`, `scope`) VALUES ('{}', '{}', '{}', '{}','{}');".format(
            access_token, token_type, expires_at_date, refresh_token, scope)
    select_statement = "SELECT * FROM access_token"
    conn = connectToDB()
    cursor = conn.cursor()
    try:
        cursor.execute(select_statement)
        if cursor.rowcount > 0:
            deleteToken(conn)
        cursor.execute(insert_statement)
        conn.commit()
        print("Inserted access token with statement", insert_statement)
    except MySQLdb.IntegrityError:
        print("Failed to insert values")
    finally:
        conn.close()


def refreshTokenIfNeeded():
    conn = connectToDB()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM access_token")
    if cursor.rowcount != 1:
        print("Error: more than one token in access_token table") 
        return None 

    row = cursor.fetchone()
    refresh_date = row[2]

    needsRefreshing = True if refresh_date < datetime.datetime.now() else False

    # update if necessary
    if needsRefreshing:
        print("Refreshing token...")
        refresh_token = row[3]
        oauth_session = OAuth2Session(client_id, client_secret, refresh_token=refresh_token)
        body = "grant_type=refresh_token"
        updated_token = oauth_session.refresh_token(refresh_url,
                                                    refresh_token=refresh_token,
                                                    body=body)
        deleteToken()
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
        cursor.execute("SELECT * FROM access_token")
        num_rows = cursor.rowcount
        if num_rows == 0:
            print("Error: An access token does not exist")
        elif num_rows == 1:
            token = cursor.fetchone()
            return token
        else:
            print("There are multiple access keys in the database. This is not allowed")
    except MySQLdb.IntegrityError:
        print("Failed to fetch access_token")
    finally:
        conn.close()


def getHeaders():
    access_token = getToken()[0]
    return {'host': 'api.sandbox.trainingpeaks.com','content-type':
            'application/json', 'Authorization': 'Bearer ' + access_token}




def getAthleteId():
    r = requests.get('https://api.sandbox.trainingpeaks.com/v1/athlete/profile',
                     headers=getHeaders())
    id = (r.json())["Id"]
    return id


def getHoursForAthlete(id, start_date, end_date):
    print("Getting hours for athlete {}...".format(id))
    api_url = api_base_url + '/v1/workouts/{}/{}/{}'.format(id, start_date, end_date)
    response = requests.get(api_url, headers=getHeaders())

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
    r_json = r.json()
    # convert inputted dates from MM/DD/YYYY to YYYY-MM-DD
    dStart = datetime.datetime.strptime(start_date, '%m/%d/%Y')
    dEnd = datetime.datetime.strptime(end_date, '%m/%d/%Y')
    start_date_f = dStart.strftime('%Y-%m-%d')
    end_date_f = dEnd.strftime('%Y-%m-%d')
    for athlete in r_json:
        # date formatted YYYY-MM-DD
        hours = getHoursForAthlete(athlete['Id'],
                                           start_date_f, end_date_f)
        rounded_hours = round(hours, 2)
        athlete_info = {
            "name": "{} {}".format(athlete["FirstName"], athlete["LastName"]),
            "hours": hours,
            "rounded_hours": rounded_hours
        }
        athletes.append(athlete_info)

    # sort list of athletes based on number of hours
    sorted_athletes = sorted(athletes, key=operator.itemgetter('hours'), reverse=True)
    print(sorted_athletes)

    return (len(athletes), sorted_athletes)
