#!/usr/bin/env python

from config import Config
from flask import Flask
from flask_bootstrap import Bootstrap
from flask import session as login_session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
import string
import sys
import subprocess
import shutil
import random
import os


app = Flask(__name__)
bootstrap = Bootstrap(app)

# import config and create db and migrate instances
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

### Database functionality - future functionality
# Connect to Database and create database session
#engine = create_engine('postgresql:///wordtopdf')
#Base.metadata.bind = engine

#DBSession = sessionmaker(bind=engine)
#session = DBSession()

## establish configuration settings for the application
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'difficult-to-guess'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/uploads')
app.config['ALLOWED_EXTENSIONS'] = set(['zip'])

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

from wordtopdf import views
from wordtopdf import conversions
from wordtopdf import combinations
from wordtopdf import models


# Generate a random string token for CSRF protection on selected POST views.
def generate_csrf_token():
    if '_csrf_token' not in login_session:
        csrf_token = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
        login_session['_csrf_token'] = csrf_token
    return login_session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token
