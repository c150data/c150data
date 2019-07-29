"""
Init module that handles initialization of the app, database, and log, among other things
"""
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

# Config.py file should be in the same directory level as this file. 
# It should have all the confidential info necessary for the application to run
app.config.from_object('config') 

# Initialize mail 
mail = Mail(app)

# Initilize database object
db = SQLAlchemy(app)

# Put the app.config varaibles within the scope of jinja
app.jinja_env.globals.update(config=app.config)

# Set up logger for the application. Import log from app to access.
formatter = logging.Formatter(
    "%(asctime)s %(levelname)8s - %(message)s (%(filename)s:%(lineno)d)", "%H:%M:%S")
streamHandler = logging.StreamHandler(sys.stderr)
streamHandler.setFormatter(formatter)
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
log.addHandler(streamHandler)


# Set up login manager
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'  # route that login_required redirects to

# Set up encryption mechanism for passwords
bcrypt = Bcrypt(app)


from app.database.db_models import User, AuthToken, Athlete, Workout

from app.users.routes import users  # position important to avoid circular importation
from app.admin.routes import admin1
from app.main.routes import main
from app.data.routes import data1
from app.errors.handlers import errors

app.register_blueprint(users)
app.register_blueprint(admin1)
app.register_blueprint(main)
app.register_blueprint(data1)
app.register_blueprint(errors)

# Workout.__table__.drop(db.engine) # Use if you want to drop the table and reset it
# Athlete.__table__.drop(db.engine) # Use if you want to drop the table and reset it
db.create_all()  # Only creates tables when they do not already exist
db.session.commit() # Commits any changes made in the above 3 lines
