from authlib.client import OAuth2Session
from app import log

remote = False

# TODO move this somewhere else out of version control
client_id = 'columbiac150'
client_secret = 'kzSN7CYgZYUMzb8DfhEqRnqrHAqiAEUHOgSAJo8'
coach_scope = ["coach:athletes", "workouts:read"]
grant_type = "refresh_token"

api_base_url = 'https://api.sandbox.trainingpeaks.com'
refresh_url = "https://oauth.sandbox.trainingpeaks.com/oauth/token"
authorization_base_url = 'https://oauth.sandbox.trainingpeaks.com/OAuth/Authorize'
token_base_url = 'https://oauth.sandbox.trainingpeaks.com/oauth/token'
redirect_uri = "https://www.c150data.com/" if remote else "https://localhost:5000/"


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
