from app.database.db_models import Athlete, Workout
from app.database.db_functions import dbSelect
from app.database.sql_statements import getAthleteNameFromId
from app import log
from dateutil import parser

"""
Handles mapping involving Athlete object
"""


class InvalidZoneAthletes:
    athletesWithWrongHrZones = dict()
    athletesWithWrongPowerZones = dict()


def getAthleteObjectFromJSON(athlete_json):
    """
    Converts a json object to a db.model Athlete object
    """
    return Athlete(
        id=athlete_json['Id'],
        name="{} {}".format(
            athlete_json['FirstName'], athlete_json['LastName']),
        email=athlete_json['Email'],
        is_active=True,  # Default isActive to True, can manually deactivate later
        last_updated_workouts=None)


def getWorkoutObjectFromJSON(workout_json, zones_json):
    """
    Converts a json object to a db.Model Workout object

    Returns:
        [type] -- [description]
    """

    athleteName = dbSelect(getAthleteNameFromId(workout_json['AthleteId']))[0][0]
    hrZones, powerZones = getTimeInZones(athleteName, zones_json)

    return Workout(
        id=workout_json.get('Id', None),
        athleteId=workout_json.get('AthleteId', None),
        completed=workout_json.get('Completed', None),
        distance=workout_json.get('Distance', None),
        distancePlanned=workout_json.get('DistancePlanned', None),
        distanceCustomized=workout_json.get('DistanceCustomized', None),
        lastModifiedDate=tryParse(workout_json.get('LastModifiedDate', None)),
        startTime=tryParse(workout_json.get('StartTime', None)),
        startTimePlanned=tryParse(workout_json.get('StartTimePlanned', None)),
        title=workout_json.get('Title', None),
        totalTime=workout_json.get('TotalTime', None),
        totalTimePlanned=workout_json.get('TotalTimePlanned', None),
        workoutDay=tryParse(workout_json.get('WorkoutDay', None)),
        workoutType=workout_json.get('WorkoutType', None),
        cadenceAverage=workout_json.get('CadenceAverage', None),
        cadenceMaximum=workout_json.get('CadenceMaximum', None),
        calories=workout_json.get('Calories', None),
        caloriesPlanned=workout_json.get('CaloriesPlanned', None),
        elevationAverage=workout_json.get('ElevationAverage', None),
        elevationGain=workout_json.get('ElevationGain', None),
        elevationGainPlanned=workout_json.get('ElevationGainPlanned', None),
        elevationLoss=workout_json.get('ElevationLoss', None),
        elevationMaximum=workout_json.get('ElevationMaximum', None),
        elevationMinimum=workout_json.get('ElevationMinimum', None),
        energy=workout_json.get('Energy', None),
        energyPlanned=workout_json.get('EnergyPlanned', None),
        heartRateAverage=workout_json.get('HeartRateAverage', None),
        heartRateMaximum=workout_json.get('HeartRateMaximum', None),
        heartRateMinimum=workout_json.get('HeartRateMinimum', None),
        iF=workout_json.get('IF', None),
        iFPlanned=workout_json.get('IFPlanned', None),
        normalizedPower=workout_json.get('NormalizedPower', None),
        normalizedSpeed=workout_json.get('NormalizedSpeed', None),
        powerAverage=workout_json.get('PowerAverage', None),
        powerMaximum=workout_json.get('PowerMaximum', None),
        tags=tryListConvert(workout_json.get('Tags', None)),
        tempAvg=workout_json.get('TempAvg', None),
        tempMax=workout_json.get('TempMax', None),
        tempMin=workout_json.get('TempMin', None),
        torqueAverage=workout_json.get('TorqueAverage', None),
        torqueMaximum=workout_json.get('TorqueMaximum', None),
        tssActual=workout_json.get('TssActual', None),
        tssCalculationMethod=workout_json.get('TssCalculationMethod', None),
        tssPlanned=workout_json.get('TssPlanned', None),
        velocityAverage=workout_json.get('VelocityAverage', None),
        velocityMaximum=workout_json.get('VelocityMaximum', None),
        velocityPlanned=workout_json.get('VelocityPlanned', None),
        description=workout_json.get('Description', None),
        feeling=workout_json.get('Feeling', None),
        preActivityComment=workout_json.get('PreActivityComment', None),
        rpe=workout_json.get('Rpe', None),
        structure=workout_json.get('Structure', None),
        workoutFileFormats=workout_json.get('WorkoutFileFormats', None),
        hrZone1Time=hrZones[0],
        hrZone2Time=hrZones[1],
        hrZone3Time=hrZones[2],
        hrZone4Time=hrZones[3],
        hrZone5Time=hrZones[4],
        powerZone1Time=powerZones[0],
        powerZone2Time=powerZones[1],
        powerZone3Time=powerZones[2],
        powerZone4Time=powerZones[3],
        powerZone5Time=powerZones[4]
    )


def getTimeInZones(athlete_name, zones_obj):
    hrZonesList = [None, None, None, None, None]
    powerZonesList = [None, None, None, None, None]
    invalid_zones = ([None, None, None, None, None],
                     [None, None, None, None, None])
    if zones_obj is None:
        return invalid_zones
    elif type(zones_obj) is str:
        #  This means the athlete is not a premium athlete
        return invalid_zones

    # Do HR zones
    hrZones = zones_obj.get('TimeInHeartRateZones', None)
    if hrZones is not None:
        timeInHrZones = hrZones.get('TimeInZones')
        if timeInHrZones is not None:
            if len(timeInHrZones) != 5:
                if athlete_name not in InvalidZoneAthletes.athletesWithWrongHrZones:
                    InvalidZoneAthletes.athletesWithWrongHrZones[athlete_name] = "Wrong number of HR zones: has {} zones, should have 5 zones".format(len(timeInHrZones))
            else:
                # The first zone (0) should be the EASY zone. The 5th zone (4) should be the HARD zone. If that's not the case, set isReverse to True
                hrZonesReverse = isReverse(timeInHrZones)
                hrZonesList = [
                    timeInHrZones.get('0').get('Seconds')/60,
                    timeInHrZones.get('1').get('Seconds')/60,
                    timeInHrZones.get('2').get('Seconds')/60,
                    timeInHrZones.get('3').get('Seconds')/60,
                    timeInHrZones.get('4').get('Seconds')/60,
                ]
                if hrZonesReverse:
                    InvalidZoneAthletes.athletesWithWrongHrZones[athlete_name] = "HR zones are reversed. The first zone should be Zone V (EASY), the last should be Zone I (HARD)"
                    hrZonesList.reverse()

    # Do power zones
    powerZones = zones_obj.get('TimeInPowerZones', None)
    if powerZones is not None:
        timeInPowerZones = powerZones.get('TimeInZones')
        if timeInPowerZones is not None:
            if len(timeInPowerZones) != 5:
                if athlete_name not in InvalidZoneAthletes.athletesWithWrongPowerZones:
                    InvalidZoneAthletes.athletesWithWrongPowerZones[athlete_name] = "Wrong number of power zones: has {} zones, should have 5 zones".format(len(timeInPowerZones))
            else:
                # The first zone (0) should be the EASY zone. The 5th zone (4) should be the HARD zone. If that's not the case, set isReverse to True
                powerZonesReverse = isReverse(timeInPowerZones)
                powerZonesList = [
                    timeInPowerZones.get('0'),
                    timeInPowerZones.get('1'),
                    timeInPowerZones.get('2'),
                    timeInPowerZones.get('3'),
                    timeInPowerZones.get('4'),
                ]
                if powerZonesReverse:
                    InvalidZoneAthletes.athletesWithWrongPowerZones[athlete_name] = "Power zones are reversed. The first zone should be Zone V (EASY), the last should be Zone I (HARD)"
                    powerZonesList.reverse()

    return (hrZonesList, powerZonesList)


def isReverse(zones):
    isReverse = False
    minFirstZone = zones.get('0').get("Minimum")
    minFifthZone = zones.get('4').get("Minimum")
    if minFirstZone > minFifthZone:
        isReverse = True
    return isReverse


def getZone(zones, zone_num):
    # TODO turn this into try catch block
    if zones is not None:
        timeInZones = zones.get("TimeInZones", None)
        if timeInZones is not None:
            zoneInfo = timeInZones.get('{}'.format(zone_num), None)
            if zoneInfo is not None:
                zoneSeconds = zoneInfo.get('Seconds')
                if zoneSeconds is not None:
                    return zoneSeconds/60
    return None


def tryParse(str_date):
    """
    Used to parse a date, but avoid None error. If the date is None,
    will not attempt to parse, but instead just set the variable to None
    """
    try:
        return parser.parse(str_date)
    except:
        return None


def tryListConvert(list):
    """
    Used to convert a list to a string, but if the list is None, will just
    return None to avoid None error
    """
    try:
        return " ".join(list)
    except:
        return None
