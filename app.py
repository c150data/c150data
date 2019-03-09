from requests_oauthlib import OAuth2Session

from flask import Flask, request, render_template, redirect, session, url_for
from flask.json import jsonify
import os
from flask_session.__init__ import Session

app = Flask(__name__)
app.secret_key = os.urandom(24)
global authorization_url

client_id = 'columbiac150'
client_secret = 'kzSN7CYgZYUMzb8DfhEqRnqrHAqiAEUHOgSAJo8'
scope = "athlete:profile"
redirect_uri = "https://localhost:5000"
authorization_base_url = 'https://oauth.sandbox.trainingpeaks.com/OAuth/Authorize'
token_url = 'https://oauth.sandbox.trainingpeaks.com/oauth/token'
authorization_url = ""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/authorize")
def user_authorization():
    global authorization_url
    oauth_session = OAuth2Session(client_id)
    authorization_url, state = oauth_session.authorization_url(authorization_base_url)
    session["oauth-state"] = state
    return redirect(authorization_url)


@app.route("/token")
def callback():
    global authorization_url
    #TODO: Use state for CSRF
    oauth_session = OAuth2Session(client_id, state=session["oauth-state"])
    #Problem here with authorization response
    #We need to figure out how to get code from user_authorization method to 
    #authorization_response in this method
    token = oauth_session.fetch_token(token_url,
             client_secret=client_secret,
             code=authorization_url)
    #When this works, the below statement should print the profile of the
    #athlete who gave permisisons in the previous method
    session["oauth-state"] = token 
    print(oauth_session.get("https://api.sandbox.trainingpeaks.com/v1/athlete/profile"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", ssl_context='adhoc', debug=True)
