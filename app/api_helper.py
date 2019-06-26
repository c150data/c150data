import requests

def makeCall(url):
    headers = getAPIRequestHeaders()
    if headers is None:
        return None
    return requests.get(url, headers=getAPIRequestHeaders)
