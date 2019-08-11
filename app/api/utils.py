from app.database.db_models import Athlete, Workout
from app.database.db_functions import dbSelect
from app.database.sql_statements import getAthleteNameFromId
from app import log
from dateutil import parser

"""
Handles mapping involving Athlete object
"""


class InvalidZoneAthletes:
    wrongNumHrZones = dict()
    wrongNumPowerZones = dict()
    reverseHrZones = dict()
    reversePowerZones = dict()

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
    workoutType = workout_json.get('WorkoutType', None)
    hrZones, powerZones = getTimeInZones(athleteName, workoutType, zones_json)

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


def getTimeInZones(athlete_name, workout_type, zones_obj):
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
                if athlete_name not in InvalidZoneAthletes.wrongNumHrZones:
                    InvalidZoneAthletes.wrongNumHrZones[athlete_name] = dict()
                InvalidZoneAthletes.wrongNumHrZones[athlete_name][workout_type] = "Wrong number of HR zones: {}".format(len(timeInHrZones))
            # The first zone (0) should be the EASY zone. The 5th zone (4) should be the HARD zone. If that's not the case, set isReverse to True
            hrZonesReverse = isReverse(timeInHrZones)

            # We are going to track their zones EVEN if they don't have the right number. This code contains
            # failsafes for if they have less than 5 zones.
            zone1 = timeInHrZones.get('0', None)
            zone1Time = zone1.get('Seconds')/60 if zone1 is not None else None
            zone2 = timeInHrZones.get('1', None)
            zone2Time = zone2.get('Seconds')/60 if zone2 is not None else None
            zone3 = timeInHrZones.get('2', None)
            zone3Time = zone3.get('Seconds')/60 if zone3 is not None else None
            zone4 = timeInHrZones.get('3', None)
            zone4Time = zone4.get('Seconds')/60 if zone4 is not None else None
            zone5 = timeInHrZones.get('4', None)
            zone5Time = zone5.get('Seconds')/60 if zone5 is not None else None

            hrZonesList = [
                zone1Time,
                zone2Time,
                zone3Time,
                zone4Time,
                zone5Time
            ]
            if hrZonesReverse:
                if athlete_name not in InvalidZoneAthletes.reverseHrZones:
                    InvalidZoneAthletes.reverseHrZones[athlete_name] = dict()
                InvalidZoneAthletes.reverseHrZones[athlete_name][workout_type] = "HR zones reversed"
                hrZonesList.reverse()

    # Do power zones
    powerZones = zones_obj.get('TimeInPowerZones', None)
    if powerZones is not None:
        timeInPowerZones = powerZones.get('TimeInZones')
        if timeInPowerZones is not None:
            if len(timeInPowerZones) != 5:
                if athlete_name not in InvalidZoneAthletes.wrongNumPowerZones:
                    InvalidZoneAthletes.wrongNumPowerZones[athlete_name] = dict()
                InvalidZoneAthletes.wrongNumPowerZones[athlete_name][workout_type] = "Wrong number of power zones: {}".format(len(timeInPowerZones))
            # The first zone (0) should be the EASY zone. The 5th zone (4) should be the HARD zone. If that's not the case, set isReverse to True
            powerZonesReverse = isReverse(timeInPowerZones)

            # We are going to track their zones EVEN if they don't have the right number. This code contains
            # failsafes for if they have less than 5 zones.
            zone1 = timeInPowerZones.get('0', None)
            zone1Time = zone1.get('Seconds')/60 if zone1 is not None else None
            zone2 = timeInPowerZones.get('1', None)
            zone2Time = zone2.get('Seconds')/60 if zone2 is not None else None
            zone3 = timeInPowerZones.get('2', None)
            zone3Time = zone3.get('Seconds')/60 if zone3 is not None else None
            zone4 = timeInPowerZones.get('3', None)
            zone4Time = zone4.get('Seconds')/60 if zone4 is not None else None
            zone5 = timeInPowerZones.get('4', None)
            zone5Time = zone5.get('Seconds')/60 if zone5 is not None else None

            powerZonesList = [
                zone1Time,
                zone2Time,
                zone3Time,
                zone4Time,
                zone5Time
            ]
            if powerZonesReverse:
                if athlete_name not in InvalidZoneAthletes.reversePowerZones:
                    InvalidZoneAthletes.reversePowerZones[athlete_name] = dict()
                InvalidZoneAthletes.reversePowerZones[athlete_name][workout_type] = "Power zones reversed"
                powerZonesList.reverse()

    return (hrZonesList, powerZonesList)


def isReverse(zones):
    isReverse = False
    zone1 = zones.get('0', None)
    zone5 = zones.get('4', None)
    if zone1 is None or zone5 is None:
        return False
    minFirstZone = zone1.get("Minimum")
    minFifthZone = zone5.get("Minimum")
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
