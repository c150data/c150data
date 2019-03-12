from authlib.client import OAuth2Session, OAuthClient

from flask import Flask, request, render_template, redirect, session, url_for
from flask.json import jsonify
import os, requests, datetime, MySQLdb

app = Flask(__name__)

app.secret_key = os.urandom(24)
client_id = 'columbiac150'
client_secret = 'kzSN7CYgZYUMzb8DfhEqRnqrHAqiAEUHOgSAJo8'
scope = ["coach:athletes", "workouts:read"]
redirect_uri = "https://localhost:5000"
authorization_base_url = 'https://oauth.sandbox.trainingpeaks.com/OAuth/Authorize'
token_url = 'https://oauth.sandbox.trainingpeaks.com/oauth/token'
api_base_url = 'https://api.sandbox.trainingpeaks.com'
db_host = "mysql.c150data.com"
db_name = "c150db"
db_user = "lwtpoodles150"
db_passwd = "Columbia150"


def connectToDB():
    return MySQLdb.connect(host=db_host, user=db_user, passwd=db_passwd,
            db=db_name)


@app.route("/db/insert")
def executeTokenInsert(access_token, token_type, expires_in, refresh_token,
        scope):
    expires_at_date = datetime.datetime.now() + datetime.timedelta(hours=1)
    expires_at_date = expires_at_date.replace(microsecond=0)
    statement = "INSERT INTO `access_token` (`access_token`, `token_type`,`expires_at`, `refresh_token`, `scope`) VALUES ('{}', '{}', '{}', '{}','{}');".format(
            access_token, token_type, expires_at_date, refresh_token, scope)
    print(statement)

    conn = connectToDB()
    cursor = conn.cursor()
    try:
        cursor.execute(statement)
        conn.commit()
        print("Inserted access token with statement %s", statement)
    except MySQLdb.IntegrityError:
        print("Failed to insert values")
    finally:
        conn.close()


def getToken():
    ensureToken()
    conn = connectToDB()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT access_token FROM access_token")
        access_token = cursor.fetchone()[0]
    except MySQLdb.IntegrityError:
        print("Failed to fetch access_token")
    finally:
        conn.close()

    return access_token




def getHeaders():
    token = getToken()
    return {'host': 'api.sandbox.trainingpeaks.com', 'content-type':
            'application/json', 'Authorization': 'Bearer ' + token}


def ensureToken():
    token_needs_refresh = False # TODO: Refresh token stuff
    if token_needs_refresh:
        oauth_session = OAuth2Session(client_id, client_secret,
                redirect_uri=redirect_uri, scope=scope)
        authorization_response = input(str("authorization_response: "))
        token = oauth_session.fetch_access_token(token_url,
                authorization_response=authorization_response)
        executeTokenInsert(access_token=token['access_token'],token_type=token['token_type'],expires_in=token['expires_in'],refresh_token=token['refresh_token'],scope=token['scope'])


def getAthleteId():
    r = requests.get('https://api.sandbox.trainingpeaks.com/v1/athlete/profile',
            headers=getHeaders())
    print(r)
    id = (r.json())["Id"]
    print(id)
    return id


def getHoursForAthlete(id, start_date, end_date):
    api_url = api_base_url + '/v1/workouts/{}/{}/{}'.format(id, start_date, end_date)

    response = requests.get(api_url, headers=getHeaders())

    json_response = response.json()
    sum_hours = 0
    for workout in json_response:
        total_time = workout['TotalTime']
        print("time: ", total_time)
        if type(total_time) is float:
            sum_hours += float(total_time)
    return sum_hours


@app.route("/athletes")
def getAllAthletes():
    ensureToken()
    r = requests.get('https://api.sandbox.trainingpeaks.com/v1/coach/athletes',
                      headers=getHeaders())
    athletes = list()
    r_json = r.json()
    for athlete in r_json:
        hours = getHoursForAthlete(athlete['Id'], '2019-02-01', '2019-03-10')    
        athletes.append("{} {}: {}".format(athlete['FirstName'],
                                           athlete['LastName'], hours))

    print(athletes)
    return render_template("index.html", len=len(athletes), athletes=athletes)



@app.route("/hours")
def getHoursThisWeek():
    ensureToken()
    id = getAthleteId()

    start_date = '2019-03-03'
    end_date = '2019-03-10'

    api_url = api_base_url + '/v1/workouts/{}/{}/{}'.format(id, start_date, end_date)
    response = requests.get(api_url, headers=getHeaders())

    json_response = response.json()
    sum_hours = 0
    count = 1
    for workout in json_response:
        total_time = workout['TotalTime']
        print("time: ", total_time)
        if type(total_time) is float:
            sum_hours += float(total_time)
        count += 1

    print("count", count)

    return render_template("index.html", last_weeks_hours=sum_hours)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/authorize")
def user_authorization():
    oauth_session = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri,
            scope=scope)
    authorization_url, state = oauth_session.create_authorization_url(authorization_base_url)
    print(authorization_url)
    return redirect(authorization_url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc', debug=True)
