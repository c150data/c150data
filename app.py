from authlib.client import OAuth2Session

from flask import Flask, request, render_template, redirect, url_for
from operator import itemgetter
import os
import requests
import helpers
import pymysql


app = Flask(__name__)
app.secret_key = os.urandom(24)
global authorization_url

app.secret_key = os.urandom(24)
client_id = 'columbiac150'
client_secret = 'kzSN7CYgZYUMzb8DfhEqRnqrHAqiAEUHOgSAJo8'
coach_scope = ["coach:athletes", "workouts:read"]
redirect_uri = "https://localhost:5000"
authorization_base_url = 'https://oauth.sandbox.trainingpeaks.com/OAuth/Authorize'
token_base_url = 'https://oauth.sandbox.trainingpeaks.com/oauth/token'


@app.route("/", methods=['GET'])
def index():
    return redirect(url_for('about'))

@app.route("/about", methods=['GET', 'POST'])
def about():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        print("Start date: ", start_date)
        print("End date: ", end_date)
        len, athletes = helpers.getAllAthletes(start_date, end_date)
        return render_template("index.html", len=len, athletes=athletes)
    else:
        return render_template("index.html")


@app.route("/hours", methods=['GET', 'POST'])
def hours():
    if request.method == 'POST':
        #TODO
        return render_template("hours.html") #add parameters to fill results table
    else:
        return render_template("hours.html")


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        #TODO
        return render_template("contact.html") #add parameters to fill results table
    else:
        return render_template("contact.html")


@app.route("/authorize")
def user_authorization():
    oauth_session = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri,
                                  scope=coach_scope)
    authorization_url, state = oauth_session.create_authorization_url(authorization_base_url)
    print(authorization_url)
    return redirect(authorization_url)


@app.route("/insertNewToken")
def insertNewToken():
    oauth_session = OAuth2Session(client_id, client_secret,
                                  redirect_uri=redirect_uri, scope=coach_scope)
    authorization_response = input(str("authorization_response: "))
    token = oauth_session.fetch_access_token(token_base_url,
                                             authorization_response=authorization_response)
    print("Got a new token: ", token)
    print("Inserting token...")
    helpers.executeTokenInsert(token)
    return render_template("index.html")


@app.route("/getData")
def getData():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    len, athletes = helpers.getAllAthletes(start_date, end_date)
    return render_template("data.html", len=len, athletes=athletes)


if __name__ == "__main__":
    app.run(host="localhost", ssl_context='adhoc', debug=True)
