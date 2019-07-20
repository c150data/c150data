"""
Handles OAuth2 with TrainingPeaks. Most of this focuses on the
getting/updating of access tokens, which allows our application
to make API requests to TrainingPeaks.
"""
from authlib.client import OAuth2Session
from app import log, app
from app.database import db_functions
from app.db_models import AuthToken
from datetime import datetime, timedelta

remote = app.config['IS_REMOTE']
client_id = app.config['CLIENT_ID']
client_secret = app.config['CLIENT_SECRET']
coach_scope = ["coach:athletes", "workouts:read"]
grant_type = "refresh_token"

# These URLs will need to change when we are using TrainingPeaks production service
api_base_url = 'https://api.sandbox.trainingpeaks.com'
refresh_url = "https://oauth.sandbox.trainingpeaks.com/oauth/token"
authorization_base_url = 'https://oauth.sandbox.trainingpeaks.com/OAuth/Authorize'
token_base_url = 'https://oauth.sandbox.trainingpeaks.com/oauth/token'
redirect_uri = "https://www.c150data.com/admin" if remote else "https://localhost:5000/admin"

refresh_padding_time = 300


def getValidAuthToken():
    """
    Returns a valid authtoken to be used for API calls

    Returns:
        Row: The Row object of a valid token
    """
    refreshAuthTokenIfNeeded()
    return AuthToken.query.order_by(AuthToken.id.desc()).first()


def refreshAuthTokenIfNeeded():
    """
    Checks if auth_token needs refreshing, and refreshes if necessary
    """
    most_recent_token = AuthToken.query.order_by(AuthToken.id.desc())[0]

    if most_recent_token is None or most_recent_token.refresh_token is None:
        raise Exception("Error while getting refresh token from database.")

    refresh_date = most_recent_token.expires_at
    if refresh_date < datetime.now():
        refreshAndInsertToken(most_recent_token.refresh_token)


def insertNewToken(token):
    """
    Inserts token into database. This method does NOT do expiration date checking,
    that is to be done by the method's caller

    Args:
        token (dict): dict object with the following fields: access_token, token_type, expires_in, refresh_token, and scope.
    """
    access_token, token_type, expires_in, refresh_token, scope = token['access_token'], token[
        'token_type'], token['expires_in'], token['refresh_token'], token['scope']

    # Give the expires_in time an extra 5 minutes as padding time and remove microseconds
    expires_at_date = datetime.now(
    ) + timedelta(seconds=(int(expires_in)-refresh_padding_time))

    token = AuthToken(access_token=access_token, token_type=token_type,
                      expires_at=expires_at_date, refresh_token=refresh_token, scope=scope)

    if token is None:
        raise Exception("Error while creating authlib AuthToken.")

    db_functions.dbInsert(token)


def refreshAndInsertToken(refresh_token):
    """
    Makes a call to TP to get a new token given a refresh token
    and inserts the returned new token into the database

    Args:
        refresh_token (str): Refresh token
    ""
    """
    newToken = getNewTokenWithRefreshToken(refresh_token)
    if newToken is None:
        raise Exception(
            "Was not able to get a new token with the refresh token.")
    insertNewToken(newToken)


def getNewAccessToken():
    """
    In order to get a new access token, the user first needs to click the authorization button. This will prompt
    them to login. After doing so, the user will be redirected back to the page with the code in the redirect URI.
    The user must copy that URI, then click the get access token button. When prompted in the console, paste the redirect
    URI to successfully get a new access token.

    Note: this is clearly a gimmicky way to go about doing this. In an ideal world, we could have a method that detects the
    code in the redirect url, and automatically makes the call to fetch a new access token with that code. This function isn't
    used very much though, and will be very rarely used once we have TP production access, so it is not a priority fix for now.
    """
    session = getOAuthSessionForAuthorization()
    authorization_response = input(str(
        "Authorization response from the redirect url after going through authorization: "))
    token = session.fetch_access_token(
        token_base_url, authorization_response=authorization_response)
    return token


def getNewTokenWithRefreshToken(refresh_token):
    """
    Gets a new valid auth token from TP given a refresh_token

    Arguments:
        refresh_token {str}

    Returns:
        dict -- New token with the following fields: access_token, token_type, expires_in, refresh_token, and scope
    """
    session = getOAuthSessionForRefresh(refresh_token)
    if session is None:
        raise Exception("Was not able to get a session for refresing token.")
    body = "grant_type=refresh_token"
    try:
        session.refresh_token(refresh_url,
                              refresh_token=refresh_token,
                              body=body)
    except Exception as e:
        raise Exception("Exception occurred while getting a new token with the refresh token: {}".format(refresh_token))


def getAuthorizationUrl():
    session = getOAuthSessionForAuthorization()
    # Returns a tuple of authorization_url and state, just returning the url
    return session.create_authorization_url(authorization_base_url)[0]


def getOAuthSessionForAuthorization():
    return OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri,
                         scope=coach_scope)


def getOAuthSessionForRefresh(refresh_token):
    return OAuth2Session(client_id, client_secret, refresh_token=refresh_token)
