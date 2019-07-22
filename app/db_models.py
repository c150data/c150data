"""
Models class that defines the database objects that we use in the application. 
"""
from app import db, login_manager, ACCESS, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from sqlalchemy import Column, Float, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship


# LUKAS: What is this and should it be in this file? It doesn't seem to fit with the rest of what is going on
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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


class AuthToken(db.Model):
    __tablename__ = 'authtoken'

    id = Column(Integer, primary_key=True, autoincrement=True)
    access_token = Column(String(1000), nullable=False)
    token_type = Column(String(100), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    refresh_token = Column(String(1000), nullable=False)
    scope = Column(String(500), nullable=False)

    def __repr__(self):
        return "AuthToken('{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.id,
            self.access_token,
            self.token_type,
            self.expires_at,
            self.refresh_token,
            self.scope
        )


class Athlete(db.Model):
    __tablename__ = 'athletes'

    id = Column(Integer, primary_key=True,
                autoincrement=True, unique=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=True)
    is_active = Column(Boolean, nullable=False)
    workouts = relationship("Workout", backref="athletes")
    last_updated_workouts = Column(DateTime, nullable=True)

    def __repr__(self):
        return "Athlete('{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.id,
            self.name,
            self.email,
            self.is_active,
            self.workouts,
            self.last_updated_workouts
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
                        '{}', '{}', '{}')""".format(
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
            self.velocityPlanned
        )
