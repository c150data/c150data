from flask import Flask
from operator import itemgetter
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = '772f2253fd3a4c2524a93c70aefeac2e'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' #creates local database in the same directory as app.py
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login' # route that login_required redirects to

from app import routes #position important to avoid circular importation
