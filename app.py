from requests_oauthlib import OAuth2Session

from flask import Flask, request, render_template, redirect, session, url_for
from flask.json import jsonify
import os

app = Flask(__name__)

client_id = 'columbiac150'
client_secret = 'kzSN7CYgZYUMzb8DfhEqRnqrHAqiAEUHOgSAJo8'
scope = "athlete:profile"
redirect_uri = "https://localhost:5000"
authorization_base_url = 'https://oauth.sandbox.trainingpeaks.com/OAuth/Authorize'
token_url = 'https://oauth.sandbox.trainingpeaks.com/oauth/token'


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/authorize")
def user_authorization():
    oauth_session = OAuth2Session(client_id, redirect_uri=redirect_uri,
                                  scope=scope)
    authorization_url, state = oauth_session.authorization_url(authorization_base_url)
    return redirect(authorization_url)


@app.route("/token")
def callback():
    #TODO: Use state for CSRF
    oauth_session = OAuth2Session(client_id)
    #Problem here with authorization response
    #We need to figure out how to get code from user_authorization method to 
    #authorization_response in this method
    token = oauth_session.fetch_token(token_url,
             client_secret=client_secret,
             authorization_response=???)
    #When this works, the below statement should print the profile of the
    #athlete who gave permisisons in the previous method
    print(oauth_session.get("https://api.sandbox.trainingpeaks.com/v1/athlete/profile"))


if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(host="0.0.0.0", ssl_context='adhoc', debug=True)
