"""
Models class that defines the database objects that we use in the application.
"""
from app import db, ACCESS, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship





class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(20), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(60), nullable=False)  # will hash later
    access = Column(String(10), nullable=False, default=ACCESS['user'])

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def is_admin(self):
        return self.access == ACCESS['admin']

    def allowed(self, access_level):
        return self.access >= access_level

    def __repr__(self):
        return "User('{}','{}')".format(self.username, self.email)


class PrescribedTrainingDay(db.Model):
    __tablename__ = 'prescribed_training_days'

    id = Column(Integer, primary_key=True)
    day = Column(Date, nullable=False)
    total_minutes = Column(Integer, nullable=False)
    num_lifts = Column(Integer, nullable=False)
    num_regan = Column(Integer, nullable=False)
    zone_1_time = Column(Integer, nullable=False)
    zone_2_time = Column(Integer, nullable=False)
    zone_3_time = Column(Integer, nullable=False)
    zone_4_time = Column(Integer, nullable=False)
    zone_5_time = Column(Integer, nullable=False)

    def __repr__(self):
        return "PrescribedTrainingDay('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.id,
            self.day,
            self.total_hours,
            self.num_lifts,
            self.num_regan,
            self.zone_1_time,
            self.zone_2_time,
            self.zone_3_time,
            self.zone_4_time,
            self.zone_5_time
        )


class AuthToken(db.Model):
    __tablename__ = 'authtoken'

    id = Column(Integer, primary_key=True, autoincrement=True)
    access_token = Column(String(1000), nullable=False)
    token_type = Column(String(100), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    refresh_token = Column(String(1000), nullable=False)
    scope = Column(String(500), nullable=False)
    server = Column(String(100), nullable=False)

    def __repr__(self):
        return "AuthToken('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.id,
            self.access_token,
            self.token_type,
            self.expires_at,
            self.refresh_token,
            self.scope,
            self.server
        )


class Athlete(db.Model):
    __tablename__ = 'athletes'

    id = Column(Integer, primary_key=True,
                autoincrement=True, unique=True)
    whoopAthleteId = Column(Integer, nullable=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    is_active = Column(Boolean, nullable=False)
    workouts = relationship("Workout", backref="athletes")
    last_updated_workouts = Column(DateTime, nullable=True)

    def __repr__(self):
        return "Athlete('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.id,
            self.whoopAthleteId,
            self.name,
            self.email,
            self.is_active,
            self.workouts,
            self.last_updated_workouts
        )

class WhoopAthlete(db.Model):
    __tablename__ = 'whoop_athletes'

    whoopAthleteId = Column(Integer, primary_key=True)
    firstName = Column(String(200), nullable=False)
    lastName = Column(String(200), nullable=False)
    username = Column(String(200), nullable=False)
    password = Column(String(60), nullable=False) # TODO hash this
    authorizationToken = Column(String(1000), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    last_updated_data = Column(DateTime, nullable=True)

    def __repr__(self):
        return "WhoopAthlete('{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.whoopAthleteId, 
            self.username,
            self.password,
            self.authorizationToken,
            self.expires_at,
            self.last_updated_data
        )

class WhoopDay(db.Model):
    __tablename__ = 'whoop_days'

    whoopDayId = Column(Integer, primary_key=True)
    whoopAthleteId = Column(Integer, nullable=False)
    day = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    last_updated_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return "WhoopDay('{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.whoopDayId,
            self.whoopAthleteId, 
            self.day,
            self.start_time,
            self.end_time,
            self.last_updated_at
        )


class WhoopStrain(db.Model):
    __tablename__ = 'whoop_strain'

    whoopDayId = Column(Integer, primary_key=True)
    averageHeartRate = Column(Integer)
    kilojoules = Column(Float)
    maxHeartRate = Column(Integer)
    score = Column(Float)

    def __repr__(self):
        return "WhoopStrain('{}', '{}', '{}', '{}', '{}')".format(
            self.whoopDayId,
            self.averageHeartRate,
            self.kilojoules, 
            self.maxHeartRate, 
            self.score
        )


class WhoopWorkout(db.Model):
    __tablename__ = 'whoop_workouts'

    workoutId = Column(Integer, primary_key=True)
    whoopDayId = Column(Integer, nullable=False)
    startTime = Column(DateTime, nullable=False)
    endTime = Column(DateTime, nullable=False)
    kilojoules = Column(Float)
    averageHeartRate = Column(Integer)
    maxHeartRate = Column(Integer)
    sportId = Column(Integer)
    timeZoneOffset = Column(String(100))

    def __repr__(self):
        return "WhoopWorkout('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.workoutId,
            self.whoopDayId,
            self.startTime,
            self.endTime, 
            self.kilojoules,
            self.averageHeartRate, 
            self.maxHeartRate, 
            self.sportId,
            self.timeZoneOffset
        )

class WhoopHeartRate(db.Model):
    __tablename__ = 'whoop_heart_rate'

    whoopAthleteId = Column(Integer, primary_key=True)
    time = Column(DateTime, primary_key=True)
    data = Column(Integer, nullable=False)

    def __repr__(self):
        return "WhoopHeartRate('{}', '{}', '{}')".format(
            self.whoopAthleteId,
            self.time, 
            self.data
        )


class Workout(db.Model):
    __tablename__ = 'workouts'

    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    athleteId = Column(Integer, ForeignKey('athletes.id'), nullable=False)
    completed = Column(Boolean, nullable=False)
    description = Column(String(10000), nullable=True)
    distance = Column(Float, nullable=True)
    distancePlanned = Column(Float, nullable=True)
    distanceCustomized = Column(Float, nullable=True)
    lastModifiedDate = Column(DateTime, nullable=True)
    preActivityComment = Column(String(10000), nullable=True)
    startTime = Column(DateTime, nullable=True)
    startTimePlanned = Column(DateTime, nullable=True)
    structure = Column(String(20000), nullable=True)
    title = Column(String(500), nullable=True)
    totalTime = Column(Float, nullable=True)
    totalTimePlanned = Column(Float, nullable=True)
    workoutDay = Column(DateTime, nullable=True)
    workoutFileFormats = Column(String(500), nullable=True)
    workoutType = Column(String(100), nullable=True)
    cadenceAverage = Column(Integer, nullable=True)
    cadenceMaximum = Column(Integer, nullable=True)
    calories = Column(Integer, nullable=True)
    caloriesPlanned = Column(Integer, nullable=True)
    elevationAverage = Column(Float, nullable=True)
    elevationGain = Column(Float, nullable=True)
    elevationGainPlanned = Column(Float, nullable=True)
    elevationLoss = Column(Float, nullable=True)
    elevationMaximum = Column(Float, nullable=True)
    elevationMinimum = Column(Float, nullable=True)
    energy = Column(Float, nullable=True)
    energyPlanned = Column(Float, nullable=True)
    feeling = Column(Integer, nullable=True)
    heartRateAverage = Column(Integer, nullable=True)
    heartRateMaximum = Column(Integer, nullable=True)
    heartRateMinimum = Column(Integer, nullable=True)
    iF = Column(Float, nullable=True)
    iFPlanned = Column(Float, nullable=True)
    normalizedPower = Column(Float, nullable=True)
    normalizedSpeed = Column(Float, nullable=True)
    powerAverage = Column(Integer, nullable=True)
    powerMaximum = Column(Integer, nullable=True)
    rpe = Column(Integer, nullable=True)
    tags = Column(String(1000), nullable=True)
    tempAvg = Column(Float, nullable=True)
    tempMax = Column(Float, nullable=True)
    tempMin = Column(Float, nullable=True)
    torqueAverage = Column(Float, nullable=True)
    torqueMaximum = Column(Float, nullable=True)
    tssActual = Column(Float, nullable=True)
    tssCalculationMethod = Column(String(100), nullable=True)
    tssPlanned = Column(Float, nullable=True)
    velocityAverage = Column(Float, nullable=True)
    velocityMaximum = Column(Float, nullable=True)
    velocityPlanned = Column(Float, nullable=True)
    hrZone1Time = Column(Float, nullable=True)
    hrZone2Time = Column(Float, nullable=True)
    hrZone3Time = Column(Float, nullable=True)
    hrZone4Time = Column(Float, nullable=True)
    hrZone5Time = Column(Float, nullable=True)
    powerZone1Time = Column(Float, nullable=True)
    powerZone2Time = Column(Float, nullable=True)
    powerZone3Time = Column(Float, nullable=True)
    powerZone4Time = Column(Float, nullable=True)
    powerZone5Time = Column(Float, nullable=True)
    isTeamLift = Column(Boolean, nullable=False)
    isTeamCore = Column(Boolean, nullable=False)


    def __repr__(self):
        return """Workout('{}', '{}', '{}', '{}', '{}',
                        '{}', '{}', '{}', '{}', '{}',
                        '{}', '{}', '{}', '{}', '{}',
                        '{}', '{}', '{}', '{}', '{}',
                        '{}', '{}', '{}', '{}', '{}'
                        '{}', '{}', '{}', '{}', '{}',
                        '{}', '{}', '{}', '{}', '{}',
                        '{}', '{}', '{}', '{}', '{}',
                        '{}', '{}', '{}', '{}', '{}',
                        '{}', '{}', '{}', '{}', '{}',
                        '{}', '{}', '{}', '{}', '{}',
                        '{}', '{}', '{}', '{}', '{}',
                        '{}', '{}', '{}', '{}', '{}')""".format(
            self.id,
            self.athleteId,
            self.completed,
            self.description,
            self.distance,
            self.distancePlanned,
            self.distanceCustomized,
            self.lastModifiedDate,
            self.preActivityComment,
            self.startTime,
            self.startTimePlanned,
            self.structure,
            self.title,
            self.totalTime,
            self.totalTimePlanned,
            self.workoutDay,
            self.workoutFileFormats,
            self.workoutType,
            self.cadenceAverage,
            self.cadenceMaximum,
            self.calories,
            self.caloriesPlanned,
            self.elevationAverage,
            self.elevationGain,
            self.elevationGainPlanned,
            self.elevationLoss,
            self.elevationMaximum,
            self.elevationMinimum,
            self.energy,
            self.energyPlanned,
            self.feeling,
            self.heartRateAverage,
            self.heartRateMaximum,
            self.heartRateMinimum,
            self.iF,
            self.iFPlanned,
            self.normalizedPower,
            self.normalizedSpeed,
            self.powerAverage,
            self.powerMaximum,
            self.rpe,
            self.tags,
            self.tempAvg,
            self.tempMax,
            self.tempMin,
            self.torqueAverage,
            self.torqueMaximum,
            self.tssActual,
            self.tssCalculationMethod,
            self.tssPlanned,
            self.velocityAverage,
            self.velocityMaximum,
            self.velocityPlanned,
            self.hrZone1Time,
            self.hrZone2Time,
            self.hrZone3Time,
            self.hrZone4Time,
            self.hrZone5Time,
            self.powerZone1Time,
            self.powerZone2Time,
            self.powerZone3Time,
            self.powerZone4Time,
            self.powerZone5Time,
            self.isTeamLift,
            self.isTeamCore
        )
