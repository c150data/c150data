from authlib.client import OAuth2Session, OAuthClient

from flask import Flask, request, render_template, redirect, session, url_for
from flask.json import jsonify
import os, requests


app = Flask(__name__)
app.secret_key = os.urandom(24)
global authorization_url

app.secret_key = os.urandom(24)
client_id = 'columbiac150'
client_secret = 'kzSN7CYgZYUMzb8DfhEqRnqrHAqiAEUHOgSAJo8'
scope = ["athlete:profile", "workouts:read"]
redirect_uri = "https://localhost:5000"
authorization_base_url = 'https://oauth.sandbox.trainingpeaks.com/OAuth/Authorize'
token_url = 'https://oauth.sandbox.trainingpeaks.com/oauth/token'
global authorization_response
authorization_response = ""


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
    
    authorization_response = input(str("authorization_response: "))

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

    print(headers)

    r = requests.get('https://api.sandbox.trainingpeaks.com/v1/athlete/profile', headers=headers)
    response_json = r.json() 
    print(response_json)
    id = response_json["Id"]
    print(id)  
    url = 'https://api.sandbox.trainingpeaks.com/v1/workouts/{}/{}/{}'.format(id,'2019-02-08', '2019-03-08')
    print(url)
    todays_workouts = requests.get(url, headers=headers)

    print(todays_workouts.json())

    #print(oauth_session.get("https://api.sandbox.trainingpeaks.com/v1/athlete/profile"))
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc', debug=True)
