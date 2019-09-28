#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template
from wordtopdf import app, db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404_error.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500_error.html'), 500