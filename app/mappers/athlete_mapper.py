"""
Handles mapping involving Athlete object
"""
from app.db_models import Athlete


def getAthleteObjectFromJSON(athlete_json):
    return Athlete(
        id=athlete_json['Id'],
        name="{} {}".format(
            athlete_json['FirstName'], athlete_json['LastName']),
        email=athlete_json['Email'],
        is_active=True,  # Default isActive to True, can manually deactivate later
        last_updated_workouts=None)
