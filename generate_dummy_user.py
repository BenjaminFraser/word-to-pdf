#!/usr/bin/env python

from config import Config
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin
from flask import session as login_session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler
import string
import sys
import subprocess
import shutil
import random
import os
from werkzeug.security import generate_password_hash, check_password_hash
from wordtopdf import views, conversions, combinations, models, errors

from wordtopdf.models import User, Upload


app = Flask(__name__)
bootstrap = Bootstrap(app)
login = LoginManager(app)

# import config and create db and migrate instances
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# generate a dummy user and add to local db just for development purposes
dummy_user = User(id=11, username="dummy", email="dummy@hotmail.com", 
				  password_hash=generate_password_hash("dummy"))
db.session.add(dummy_user)
db.session.commit()