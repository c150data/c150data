"""
Module that contains constant SQL expressions that are commonly used by this application.
Some of them take parameters that can be formatted into the SQL statement.
"""
from datetime import datetime


def getAllHoursSQL(start_date, end_date):
    start_date_f = datetime.strptime(
        start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    end_date_f = datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    statement = """SELECT athletes.name,
                   SUM(CASE WHEN workouts.startTime >= '{}'
                   AND workouts.startTime <= '{}' THEN workouts.totalTime ELSE 0 END) as hours
                   FROM athletes
                   INNER JOIN workouts ON athletes.id = workouts.athleteId
                   GROUP BY athletes.id;
                """.format(start_date_f, end_date_f)
    return statement


def getOldestLastWorkoutTimeSQL():
    return "SELECT last_updated_workouts from athletes where is_active = True order by last_updated_workouts asc limit 1;"


def getAllActiveAthletesSQL():
    return "SELECT * FROM athletes where is_active = True;"
