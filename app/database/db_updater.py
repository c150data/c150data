"""
This module handles the updating of the database. In order to keep the data in the database up to date,
we need to periodically call the TP API, checking what has changed since the last time we updated. We then
need to update the database according to that the API response. The later part of this process is the job
of this module.
"""
from app.database import db_functions
from app.database.db_models import Workout
from app.api import api_requester
from app.api.utils import getWorkoutObjectFromJSON
from app import log


def processWorkoutUpdateJSON(workout_update_json):
    """
    Takes an API response workout update response from TP in json format,
    and makes the respective changes in the database

    Arguments:
        workout_update_json {JSON} --  JSON object with two arrays, one (Deleted) contains the ids of all
        of the workouts that have been deleted. The other (Modified) contains all of the workout information
        for workouts that have been modified.

    Returns:
        Tuple -- Number of workouts deleted, number of workouts modified
    """
    numDeleted, numModified = 0, 0
    deleted_workouts = workout_update_json['Deleted']
    if deleted_workouts is not None and len(deleted_workouts) > 0:
        numDeleted = processDeletedWorkouts(deleted_workouts)
    modified_workouts = workout_update_json['Modified']
    if modified_workouts is not None and len(modified_workouts) > 0:
        numModified = processModifiedWorkouts(modified_workouts)
    return numDeleted, numModified


def processDeletedWorkouts(deleted_workouts):
    """
    Handles deleting workouts by workout id

    Arguments:
        deleted_workouts {List of JSON} -- List of JSON workout objects to delete

    Returns:
        int -- number of workouts deleted
    """
    workoutsToDelete = list()
    for workout_id in deleted_workouts:
        workout = Workout.query.filter_by(id=workout_id)
        workoutsToDelete.append(workout)
    db_functions.dbDelete(workoutsToDelete)
    return len(workoutsToDelete)


def processModifiedWorkouts(modified_workouts):
    """
    Handles "modified" workouts. What this actually does is take every modified workouts, deletes the existing workout (if it exists)
    with that id in the database, then inserts a brand new one based on the json

    Arguments:
        modified_workouts {List of JSON} -- List of JSON workout objects to modify

    Returns:
        int -- number of workouts modified
    """
    workoutsToInsert = list()
    for modified_workout in modified_workouts:
        workoutsToInsert.append(updateWorkout(modified_workout))
    db_functions.dbInsert(workoutsToInsert)
    return len(workoutsToInsert)


def updateWorkout(workout_json):
    """
    Checks if a workout already exists in the database. If it doesn't exist, just returns the
    database Workout object to insert. If it does exist, it first deletes the existing Workout object.

    Arguments:
        workout_json {JSON} -- Workout to insert JSON
    """
    zones_json = api_requester.getZonesForWorkout(workout_json['AthleteId'], workout_json['Id']).json()
    if Workout.query.filter_by(id=workout_json['Id']) is None:
        # Workout does not exist in DB
        return getWorkoutObjectFromJSON(workout_json, zones_json)
    else:
        # Workout already exists in db, need to first delete existing then return new one to insert
        Workout.query.filter_by(id=workout_json['Id']).delete()
        return getWorkoutObjectFromJSON(workout_json, zones_json)
