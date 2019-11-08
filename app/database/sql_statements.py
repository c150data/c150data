"""
Module that contains constant SQL expressions that are commonly used by this application.
Some of them take parameters that can be formatted into the SQL statement.
"""
from datetime import datetime
from app import log


def getAllHoursSQL(start_date, end_date):
    start_date_f = datetime.strptime(
        start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    end_date_f = datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    statement = """
                SELECT
                    athletes.name as name,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' THEN workouts.totalTime ELSE 0 END), 2) as hours,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' THEN workouts.hrZone1Time ELSE 0 END), 2) as hrZone1,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' THEN workouts.hrZone2Time ELSE 0 END), 2) as hrZone2,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' THEN workouts.hrZone3Time ELSE 0 END), 2) as hrZone3,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' THEN workouts.hrZone4Time ELSE 0 END), 2) as hrZone4,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' THEN workouts.hrZone5Time ELSE 0 END), 2) as hrZone5,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' THEN workouts.powerZone1Time ELSE 0 END), 2) as powerZone1,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' THEN workouts.powerZone2Time ELSE 0 END), 2) as powerZone2,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' THEN workouts.powerZone3Time ELSE 0 END), 2) as powerZone3,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' THEN workouts.powerZone4Time ELSE 0 END), 2) as powerZone4,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' THEN workouts.powerZone5Time ELSE 0 END), 2) as powerZone5,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' AND workouts.isTeamLift == True THEN 1 ELSE 0 END), 2) as numLifts,
                    ROUND(SUM(CASE WHEN workouts.workoutDay >= '{start}'
                        AND workouts.workoutDay <= '{end}' AND workouts.isTeamCore == True THEN 1 ELSE 0 END), 2) as numRegan
                FROM athletes
                    INNER JOIN workouts ON athletes.id = workouts.athleteId
                GROUP BY athletes.id
                ORDER BY hours desc""".format(start=start_date_f, end=end_date_f)
    return statement


def getPrescribedDataSQL(start_date, end_date):
    start_date_f = datetime.strptime(
        start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    end_date_f = datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    statement = """
                SELECT
                    ROUND(SUM(CASE WHEN prescribed_training_days.day >= '{start}'
                        AND prescribed_training_days.day <= '{end}' THEN prescribed_training_days.total_minutes ELSE 0 END), 2) as minutes_prescribed,
                    ROUND(SUM(CASE WHEN prescribed_training_days.day >= '{start}'
                        AND prescribed_training_days.day <= '{end}' THEN prescribed_training_days.num_lifts ELSE 0 END), 2) as lifts_prescribed,
                    ROUND(SUM(CASE WHEN prescribed_training_days.day >= '{start}'
                        AND prescribed_training_days.day <= '{end}' THEN prescribed_training_days.num_regan ELSE 0 END), 2) as regan_prescribed,
                    ROUND(SUM(CASE WHEN prescribed_training_days.day >= '{start}'
                        AND prescribed_training_days.day <= '{end}' THEN prescribed_training_days.zone_1_time ELSE 0 END), 2) as zone_1_time,
                    ROUND(SUM(CASE WHEN prescribed_training_days.day >= '{start}'
                        AND prescribed_training_days.day <= '{end}' THEN prescribed_training_days.zone_2_time ELSE 0 END), 2) as zone_2_time,
                    ROUND(SUM(CASE WHEN prescribed_training_days.day >= '{start}'
                        AND prescribed_training_days.day <= '{end}' THEN prescribed_training_days.zone_3_time ELSE 0 END), 2) as zone_3_time,
                    ROUND(SUM(CASE WHEN prescribed_training_days.day >= '{start}'
                        AND prescribed_training_days.day <= '{end}' THEN prescribed_training_days.zone_4_time ELSE 0 END), 2) as zone_4_time,
                    ROUND(SUM(CASE WHEN prescribed_training_days.day >= '{start}'
                        AND prescribed_training_days.day <= '{end}' THEN prescribed_training_days.zone_5_time ELSE 0 END), 2) as zone_5_time
                FROM prescribed_training_days
                """.format(start=start_date_f, end=end_date_f)
    return statement



def getOldestLastWorkoutTimeSQL():
    return "SELECT last_updated_workouts from athletes where is_active = True order by last_updated_workouts asc limit 1;"


def getAllActiveAthletesSQL():
    return "SELECT * FROM athletes where is_active = True;"

def getAllWhoopAthletesSQL():
    return "SELECT * FROM whoop_athletes"

def getAuthorizationTokenSQL(whoopAthleteId):
    return "SELECT authorizationToken FROM whoop_athletes WHERE whoopAthleteId = {}".format(whoopAthleteId)

def getAthleteNameFromId(id):
    if type(id) is not int:
        id = int(id)
    return "SELECT name FROM athletes where id={}".format(id)
