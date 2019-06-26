from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)  # will hash later

    def __repr__(self):
        return "User('{}','{}')".format(self.username, self.email)


class AuthToken(db.Model):
    __tablename__ = 'authtoken'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    access_token = db.Column(db.String(1000), nullable=False)
    token_type = db.Column(db.String(100), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    refresh_token = db.Column(db.String(1000), nullable=False)
    scope = db.Column(db.String(500), nullable=False)

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

    id = db.Column(db.Integer, primary_key=True,
                   autoincrement=True, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    dob = db.Column(db.DateTime, nullable=False)
    last_updated_workouts = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return "Athlete('{}', '{}', '{}', '{}', '{}')".format(
            self.id,
            self.name,
            self.email,
            self.dob,
            self.last_updated_workouts
        )


class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    athleteId = db.Column(db.Integer, foreign_key=True)
    completed = db.Column(db.Boolean, nullable=False)
    description = db.Column(db.String(10000), nullable=True)
    distance = db.Column(db.Float, nullable=True)
    distancePlanned = db.Column(db.Float, nullable=True)
    lastModifiedDate = db.Column(db.DateTime, nullable=True)
    preActivityComment = db.Column(db.String(10000), nullable=True)
    startTime = db.Column(db.DateTime, nullable=True)
    startTimePlanned = db.Column(db.DateTime, nullable=True)
    structure = db.Column(db.String(20000), nullable=True)
    title = db.Column(db.String(500), nullable=True)
    totalTime = db.Column(db.Float, nullable=True)
    totalTimePlanned = db.Column(db.Float, nullable=True)
    workoutDay = db.Column(db.DateTime, nullable=True)
    workoutFileFormats = db.Column(db.String(500), nullable=True)
    workoutType = db.Column(db.String(100), nullable=True)
    cadenceAverage = db.Column(db.Integer, nullable=True)
    cadenceMaximum = db.Column(db.Integer, nullable=True)
    calories = db.Column(db.Integer, nullable=True)
    caloriesPlanned = db.Column(db.Integer, nullable=True)
    elevationAverage = db.Column(db.Float, nullable=True)
    elevationGain = db.Column(db.Float, nullable=True)
    elevationGainPlanned = db.Column(db.Float, nullable=True)
    elevationLoss = db.Column(db.Float, nullable=True)
    elevationMaximum = db.Column(db.Float, nullable=True)
    elevationMinimum = db.Column(db.Float, nullable=True)
    energy = db.Column(db.Float, nullable=True)
    energyPlanned = db.Column(db.Float, nullable=True)
    feeling = db.Column(db.Integer, nullable=True)
    heartRateAverage = db.Column(db.Integer, nullable=True)
    heartRateMaximum = db.Column(db.Integer, nullable=True)
    heartRateMinimum = db.Column(db.Integer, nullable=True)
    iF = db.Column(db.Float, nullable=True)
    iFPlanned = db.Column(db.Float, nullable=True)
    normalizedPower = db.Column(db.Float, nullable=True)
    normalizedSpeed = db.Column(db.Float, nullable=True)
    powerAverage = db.Column(db.Integer, nullable=True)
    powerMaximum = db.Column(db.Integer, nullable=True)
    rpe = db.Column(db.Integer, nullable=True)
    tags = db.Column(db.String(1000), nullable=True)
    tempAvg = db.Column(db.Float, nullable=True)
    tempMax = db.Column(db.Float, nullable=True)
    tempMin = db.Column(db.Float, nullable=True)
    torqueAverage = db.Column(db.Float, nullable=True)
    torqueMaixumum = db.Column(db.Float, nullable=True)
    tssActual = db.Column(db.Float, nullable=True)
    tssCalculationMethod = db.Column(db.String(100), nullable=True)
    tssPlanned = db.Column(db.Float, nullable=True)
    velocityAverage = db.Column(db.Float, nullable=True)
    velocityMaximum = db.Column(db.Float, nullable=True)
    velocityPlanned = db.Column(db.Float, nullable=True)

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
                        '{}', '{}')""".format(
            self.id,
            self.athleteId,
            self.completed,
            self.description,
            self.distance,
            self.distancePlanned,
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
            self.torqueMaixumum,
            self.tssActual,
            self.tssCalculationMethod,
            self.tssPlanned,
            self.velocityAverage,
            self.velocityMaximum,
            self.velocityPlanned
        )
