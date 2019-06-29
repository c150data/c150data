from app import db, log
import operator
from datetime import datetime


def getHoursForAllAthletes(start_date, end_date):
    result = db.session.execute(getAllHoursSQL(start_date, end_date))
    athleteHourList = list()
    for row in result:
        athlete_info = {
            "name": row['name'],
            "hours": row['hours'],
            "rounded_hours": round(row['hours'], 2)
        }
        athleteHourList.append(athlete_info)
    sortedAthleteHourList = sorted(athleteHourList, key=operator.itemgetter('hours'), reverse=True)
    return len(sortedAthleteHourList), sortedAthleteHourList


def getAllHoursSQL(start_date, end_date):
    start_date_f = datetime.strptime(start_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    end_date_f = datetime.strptime(end_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    statement = "SELECT athletes.name, SUM(CASE WHEN workouts.startTime >= '{}' AND workouts.startTime <= '{}' then workouts.totalTime else 0 END) as hours FROM athletes INNER JOIN workouts ON athletes.id = workouts.athleteId GROUP BY athletes.id;".format(start_date_f, end_date_f)
    log.info(statement)
    return statement
