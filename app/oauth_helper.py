from authlib.client import OAuth2Session

client_id = 'columbiac150'
# TODO move this somewhere else out of version control
client_secret = 'kzSN7CYgZYUMzb8DfhEqRnqrHAqiAEUHOgSAJo8'
coach_scope = ["coach:athletes", "workouts:read"]
redirect_uri = "https://localhost:5000"
authorization_base_url = 'https://oauth.sandbox.trainingpeaks.com/OAuth/Authorize'
token_base_url = 'https://oauth.sandbox.trainingpeaks.com/oauth/token'


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


def getAuthorizationUrl():
    session = getOAuthSessionForAuthorization()
    # Returns a tuple of authorization_url and state, just returning the url
    return session.create_authorization_url(authorization_base_url)[0]


def getOAuthSessionForAuthorization():
    return OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri,
                         scope=coach_scope)
