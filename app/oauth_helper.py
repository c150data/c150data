from authlib.client import OAuth2Session
from app import log, db_helper, app
from datetime import datetime, timedelta
from app.models import AuthToken


remote = True 

client_id = app.config['CLIENT_ID']
client_secret = app.config['CLIENT_SECRET']
coach_scope = ["coach:athletes", "workouts:read"]
grant_type = "refresh_token"

api_base_url = 'https://api.sandbox.trainingpeaks.com'
refresh_url = "https://oauth.sandbox.trainingpeaks.com/oauth/token"
authorization_base_url = 'https://oauth.sandbox.trainingpeaks.com/OAuth/Authorize'
token_base_url = 'https://oauth.sandbox.trainingpeaks.com/oauth/token'
redirect_uri = "https://www.c150data.com/" if remote else "https://localhost:5000/"

refresh_padding_time = 300


def insertNewToken(token):
    """
    Inserts token into database. This method does NOT do expiration date checking,
    that is to be done by the method's caller

    Args:
        token (dict): dict object with the following fields: access_token, token_type, expires_in, refresh_token, and scope.

    Returns:
        Boolean: True on successful insertion, False on unsuccessful insertion
    """
    access_token, token_type, expires_in, refresh_token, scope = token['access_token'], token[
        'token_type'], token['expires_in'], token['refresh_token'], token['scope']

    # Give the expires_in time an extra 5 minutes as padding time and remove microseconds
    expires_at_date = datetime.now(
    ) + timedelta(seconds=(int(expires_in)-refresh_padding_time))

    token = AuthToken(access_token=access_token, token_type=token_type,
                      expires_at=expires_at_date, refresh_token=refresh_token, scope=scope)
    return db_helper.dbInsert(token)


def refreshAuthTokenIfNeeded():
    """
    Checks if auth_token needs refreshing, and refreshes if necessary

    Returns:
        Boolean: True if successful, otherwise False
    """
    most_recent_token = AuthToken.query.order_by(AuthToken.id.desc())[0]
    if most_recent_token is not None:
        refresh_date = most_recent_token.expires_at
        if refresh_date < datetime.now():
            # Pass in the refresh_token from the most recent row
            return refreshAuthToken(most_recent_token.refresh_token)
        return True  # Returns True if token does not have to be refreshed

    return False


def refreshAuthToken(refresh_token):
    """
    Makes an API call to get a new token and inserts it into the
    Args:
        refresh_token (str): Refresh token

    Returns:
        Boolean: True if successful, False otherwise
    """
    return insertNewToken(getRefreshedToken(refresh_token))


def getValidAuthToken():
    """
    Returns a valid authtoken to be used for API calls

    Returns:
        Row: The Row object of a valid token
        None: On error
    """
    if refreshAuthTokenIfNeeded() is False:
        log.error("Did not successfully refresh authentication token.")
        return None

    return AuthToken.query.order_by(AuthToken.id.desc()).first()


def getNewAccessToken():
    """
    In order to get a new access token, the user first needs to click the authorization button. This will prompt
    them to login. After doing so, the user will be redirected back to the page with the code in the redirect URI.
    The user must copy that URI, then click the get access token button. When prompted in the console, paste the redirect
    URI to successfully get a new access token.
    """
    session = getOAuthSessionForAuthorization()
    authorization_response = input(str(
        "Authorization response from the redirect url after going through authorization: "))
    token = session.fetch_access_token(
        token_base_url, authorization_response=authorization_response)
    return token


def getRefreshedToken(refresh_token):
    log.info("Refreshing token with: {}".format(refresh_token))
    session = getOAuthSessionForRefresh(refresh_token)
    body = "grant_type=refresh_token"
    return session.refresh_token(refresh_url,
                                 refresh_token=refresh_token,
                                 body=body)


def getAuthorizationUrl():
    session = getOAuthSessionForAuthorization()
    # Returns a tuple of authorization_url and state, just returning the url
    return session.create_authorization_url(authorization_base_url)[0]


def getOAuthSessionForAuthorization():
    log.info("redirect uri: {}".format(redirect_uri))
    return OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri,
                         scope=coach_scope)


def getOAuthSessionForRefresh(refresh_token):
    return OAuth2Session(client_id, client_secret, refresh_token=refresh_token)
