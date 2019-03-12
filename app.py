from authlib.client import OAuth2Session, OAuthClient

from flask import Flask, request, render_template, redirect, session, url_for
from flask.json import jsonify
import os, requests


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.secret_key = os.urandom(24)
client_id = 'columbiac150'
client_secret = 'kzSN7CYgZYUMzb8DfhEqRnqrHAqiAEUHOgSAJo8'
scope = ["coach:athletes", "workouts:read"]
redirect_uri = "https://localhost:5000"
authorization_base_url = 'https://oauth.sandbox.trainingpeaks.com/OAuth/Authorize'
token_url = 'https://oauth.sandbox.trainingpeaks.com/oauth/token'
id = []
all_athlete_hours = []
name = []
all_athlete_hours_name = []

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/authorize")
def user_authorization():
    global authorization_response
    oauth_session = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri,
                                  scope=scope)
    authorization_url, state = oauth_session.create_authorization_url(authorization_base_url)

    
    return redirect(authorization_url)


@app.route("/token")
def callback():
    oauth_session = OAuth2Session(client_id, client_secret,
            redirect_uri=redirect_uri, scope=scope)
  
    authorization_response =  input(str("authorization_response: "))

    token = oauth_session.fetch_access_token(token_url,
                authorization_response=authorization_response)


    oauth_client = OAuthClient(
        client_id = client_id,
        client_secret = client_secret,
        api_base_url= 'api.sandbox.trainingpeaks.com',
        access_token_url = token_url,
        authorize_url = authorization_base_url,
        client_kwargs={'scope': scope}
    )
    headers = {'host': 'api.sandbox.trainingpeaks.com', 'content-type':
            'application/json', 'Authorization': 'Bearer ' + token['access_token']}


    r = requests.get('https://api.sandbox.trainingpeaks.com/v1/coach/athletes', headers=headers)
    response_json = r.json() 
    print(response_json)
    #get all athlete ids and names
    for athlete in response_json:
        id.append(athlete['Id'])
        full_name = athlete["FirstName"]+" "+athlete["LastName"]
        name.append(full_name)
    print(id)
    #for each athlete calculate their total time for the week
    index = 0
    for i in id:
        totalTime = 0
        url = 'https://api.sandbox.trainingpeaks.com/v1/workouts/{}/{}/{}'.format(id[index],'2019-02-25', '2019-03-03')
        aw = requests.get(url, headers=headers)
        athlete_workout = aw.json()
        for workout in athlete_workout:
            if workout['TotalTime'] != None:
                totalTime += workout['TotalTime']
        name_and_hours = name[index]+": "+str(totalTime)
        all_athlete_hours.append(name_and_hours)
        index += 1
    print(all_athlete_hours)

    #orginize hours to correspond with athlete names

    #print(todays_workouts.json())

    #print(oauth_session.get("https://api.sandbox.trainingpeaks.com/v1/athlete/profile"))
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc', debug=True)
