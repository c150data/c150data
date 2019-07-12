api_base_url = 'https://api.sandbox.trainingpeaks.com'

COACH_ATHLETES_URL = '{}/v1/coach/athletes'.format(api_base_url)


def WORKOUTS_FOR_ATHLETE_START_END(athlete_id, start, end):
    return '{}/v1/workouts/{}/{}/{}'.format(api_base_url, athlete_id, start, end)


def WORKOUTS_CHANGED_SINCE(athlete_id, sinceDate):
    # 2017-10-01T00:00:00.00000Z
    formattedDate = sinceDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return '{}/v1/workouts/{}/changed?date={}'.format(api_base_url, athlete_id, formattedDate)