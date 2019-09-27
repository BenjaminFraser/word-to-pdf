#!/usr/bin/env python

from wordtopdf import db

class User(db.Model):
    """ SQLAlchemy User model to store registered users of the application """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    uploads = db.relationship('Upload', backref='author', lazy='dynamic')

    def __repr__(self):
        """ repr method - informs Python how to print objects of this class """
        return '<User {}>'.format(self.username)    


class Upload(db.Model):
    """ SQLAlchemy Uploads model to store details of uploaded files """
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(64), index=True, unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Upload {}>'.format(self.filename)