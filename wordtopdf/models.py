#!/usr/bin/env python

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from wordtopdf import db
from wordtopdf import login


class User(UserMixin, db.Model):
    """ SQLAlchemy User model to store registered users of the application. """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    uploads = db.relationship('Upload', backref='author', lazy='dynamic')

    def __repr__(self):
        """ repr method - informs Python how to print objects of this class """
        return '<User {}>'.format(self.username)    

    def set_password(self, password):
        """ Creates and uploads a password hash for the given user """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ Verifies the given password is correct for the stored password hash """
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    """ User loader function for flask-login to obtain a user id """
    return User.query.get(int(id))


class Upload(db.Model):
    """ SQLAlchemy Uploads model to store details of uploaded files """
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64), index=True, unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Upload {}>'.format(self.filename)