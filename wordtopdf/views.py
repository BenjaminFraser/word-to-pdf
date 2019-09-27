#!/usr/bin/env python

from werkzeug.utils import secure_filename
from flask import Flask, render_template, flash, request, \
        url_for, redirect, jsonify, send_from_directory
from flask_bootstrap import Bootstrap
from io import open
from PyPDF2 import PdfFileMerger, PdfFileReader
import sys
import subprocess
import shutil
import re
import os
import zipfile

from wordtopdf import app
from wordtopdf import conversions
from wordtopdf import combinations
from wordtopdf.forms import LoginForm

## Future functionality - database support
# Connect to Database and create database session
#engine = create_engine('postgresql:///wordtopdf')
#Base.metadata.bind = engine

#DBSession = sessionmaker(bind=engine)
#session = DBSession()


@app.route('/')
def home_page():
    """ Render the main app page """
    files = list_conversions()
    print(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)


@app.route("/files")
def list_conversions():
    """ List conversion files on the server. """
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if (os.path.isfile(path) and filename.find(".DS") == -1):
            files.append(filename)
    return files


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """ Upload a given zipped file """
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # create source and destination directories
            source_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'source')
            os.makedirs(source_folder, exist_ok=True)
            dest_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'destination')
            os.makedirs(dest_folder, exist_ok=True)

            # create the zip object and extract into the source folder
            zip_ref = zipfile.ZipFile(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r')
            zip_ref.extractall(source_folder)
            zip_ref.close()

            # convert source recursive directory into pdf files
            conversions.convert_recursive_directory(dest_folder, source_folder)

            # combine all pdfs into one large file
            ordered_pdf_conversions = combinations.combine_directory(dest_folder)
            combinations.combine_conversions(dest_folder, ordered_pdf_conversions, filename)

            # delete the source and destination folders, and original zip file
            shutil.rmtree(source_folder)
            shutil.rmtree(dest_folder)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return redirect(url_for('upload_file',
                                    filename=filename))
    files = list_conversions()
    return render_template('index.html', files=files)


@app.route("/download/<path:path>")
def download_file(path): 
    """ Download the chosen pdf file. """
    # Warning - the file for send_from_directory needs to be an absolute path
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=path, as_attachment=True)


@app.route("/login", methods=['GET', 'POST'])
def login_page(): 
    """ Display a page for user login to the application. """
    form = LoginForm()
    if form.validate_on_submit():
        ### functionality for a user to log into the application
        flash("Login requested for user: {0}, remember me: {1}".format(form.username.data, form.remember_me.data))
        return redirect('/')
    return render_template('login.html', title='Sign In', form=form)