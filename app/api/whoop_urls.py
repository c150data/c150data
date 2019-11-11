
api_base_url = "https://api-7.whoop.com"
api_host = "api-7.whoop.com"

def get_api_base_url():
    return api_base_url

def get_api_host():
    return api_host

def get_whoop_token_url():
    return "{}/oauth/token".format(api_base_url)

def WHOOP_DAYS_URL(athleteId, start_date, end_date):
    start_date_f = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_date_f = end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return "{}/users/{}/cycles?start={}&end={}".format(
        api_base_url, 
        athleteId, 
        start_date_f,
        end_date_f
    )

def WHOOP_HEART_RATE_URL(athleteId, start_date, end_date):
    start_date_f = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_date_f = end_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return "{}/users/{}/metrics/heart_rate?start={}&end={}".format(
        api_base_url,
        athleteId,
        start_date_f,
        end_date_f
    )  # Possibly need to add order to this?