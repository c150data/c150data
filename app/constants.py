api_base_url = 'https://api.sandbox.trainingpeaks.com'

COACH_ATHLETES_URL = '{}/v1/coach/athletes'.format(api_base_url)


def WORKOUTS_FOR_ATHLETE_START_END(athlete_id, start, end):
    return '{}/v1/workouts/{}/{}/{}'.format(api_base_url, athlete_id, start, end)
