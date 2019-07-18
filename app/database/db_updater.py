from app.database import db_functions
from app.db_models import Workout
from app.mappers import workout_mapper
from app import log


def processWorkoutUpdateJSON(workout_update_json):
    try:
        deleted_workouts = workout_update_json['Deleted']
        numDeleted, numModified = 0, 0
        if deleted_workouts is not None and len(deleted_workouts) > 0:
            numDeleted = processDeletedWorkouts(deleted_workouts)
        modified_workouts = workout_update_json['Modified']
        if modified_workouts is not None and len(modified_workouts) > 0:
            numModified = processModifiedWorkouts(modified_workouts)
        return numDeleted, numModified
    except Exception as e:
        log.error("Error occured while processing workout updates : {error}".format(error=e))
        return None


def processDeletedWorkouts(deleted_workouts):
    workoutsToDelete = list()
    for workout_id in deleted_workouts:
        workout = Workout.query.filter_by(id=workout_id)
        workoutsToDelete.append(workout)
    db_functions.dbDelete(workoutsToDelete)
    return len(workoutsToDelete)


def processModifiedWorkouts(modified_workouts):
    # TODO ask Ben about this. Does the modified workouts tab return the entire workout's fields or only the fields that changed??
    # Right now, this is coded such that the modified workouts json returns all of the fields in the updated workout such that the
    # old workout can be deleted and be entirely recreated from the json
    workoutsToInsert = list()
    for modified_workout in modified_workouts:
        workoutsToInsert.append(updateWorkout(modified_workout))
    db_functions.dbInsert(workoutsToInsert)
    return len(workoutsToInsert)


def updateWorkout(workout_json):
    if Workout.query.filter_by(id=workout_json['Id']) is None:
        # Workout does not exist in DB
        return workout_mapper.getWorkoutObjectFromJSON(workout_json)
    else:
        # Workout already exists in db, need to first delete existing then return new one to insert
        Workout.query.filter_by(id=workout_json['Id']).delete()
        return workout_mapper.getWorkoutObjectFromJSON(workout_json)