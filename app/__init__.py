from flask import Flask
from operator import itemgetter
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import logging
import sys
from flask_mail import Mail

ACCESS = {
    'user': '1',
    'admin': '2'
}


app = Flask(__name__)
app.config.from_object('config')

mail = Mail(app)

db = SQLAlchemy(app)

app.jinja_env.globals.update(config=app.config)
# Set up logger for the application. Import log from app to access.
formatter = logging.Formatter(
    "%(asctime)s %(levelname)8s - %(message)s (%(filename)s:%(lineno)d)", "%H:%M:%S")
streamHandler = logging.StreamHandler(sys.stderr)
streamHandler.setFormatter(formatter)
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
log.addHandler(streamHandler)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # route that login_required redirects to

from app.models import User, AuthToken, Athlete, Workout
from app import routes  # position important to avoid circular importation
from app import admin
Workout.__table__.drop(db.engine) # Use if you want to drop the table and reset it
# Athlete.__table__.drop(db.engine) # Use if you want to drop the table and reset it
db.create_all()  # Only creates tables when they do not already exist
db.session.commit()
