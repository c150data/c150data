from app.db_models import Workout
from dateutil import parser


def getWorkoutObjectFromJSON(workout_json):
    # Below are fields that are specified in the API but were not returned in the response...have to look into this more and maybe talk to Ben
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
        workoutFileFormats=workout_json.get('WorkoutFileFormats', None)
    )


def tryParse(str_date):
    try:
        return parser.parse(str_date)
    except:
        return None


def tryListConvert(list):
    try:
        return " ".join(list)
    except:
        return None