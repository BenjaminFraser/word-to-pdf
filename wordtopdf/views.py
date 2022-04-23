#!/usr/bin/env python

from flask import Flask, render_template, flash, request, \
        url_for, redirect, jsonify, send_from_directory
from flask_bootstrap import Bootstrap
from flask_login import current_user, login_user, logout_user, login_required
from io import open
import os
from PyPDF2 import PdfFileMerger, PdfFileReader
import re
import shutil
import subprocess
import sys
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import zipfile

from wordtopdf import app
from wordtopdf import conversions
from wordtopdf import combinations
from wordtopdf import db
from wordtopdf.forms import LoginForm
from wordtopdf.models import User, Upload

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
    return render_template('index.html', files=files)


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
@login_required
def upload_file():
    """ Upload a given zipped file - ## TO-DO: this function needs splitting into multiple functions """
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

            try: 
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
                final_name = combinations.combine_conversions(dest_folder, ordered_pdf_conversions, filename)

                # delete the source and destination folders, and original zip file
                shutil.rmtree(source_folder)
                shutil.rmtree(dest_folder)
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # update the database with the file and the user who uploaded
                uploaded = Upload(filename=final_name, user_id=current_user.id)
                db.session.add(uploaded)
                db.session.commit()

            except Exception as e:
                e_type, e_object, e_tb = sys.exc_info()
                fname = os.path.split(e_tb.tb_frame.f_code.co_filename)[1]
                print(e_type, fname, e_tb.tb_lineno)

            return redirect(url_for('upload_file',
                                    filename=filename))
    return redirect(url_for('home_page'))


@app.route("/download/<path:path>")
@login_required
def download_file(path): 
    """ Download the chosen pdf file. """
    # Warning - the file for send_from_directory needs to be an absolute path
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=path, as_attachment=True)


@app.route("/delete/<path:path>", methods=['GET', 'POST'])
@login_required
def delete_file(path):
    """ Delete the selected file, removing it physically and updating the database accordingly """
    chosen_file = Upload.query.filter_by(filename=path).first()
    uploaded_files = list_conversions()
    if chosen_file is None or current_user.is_anonymous or chosen_file.filename not in uploaded_files:
        flash("Oops - either the file does not exist, or you do not have permission for this action.")
        return redirect(url_for('home_page'))

    try:
        # remove the chosen file physically from the file system
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], chosen_file.filename))

        # remove the chosen file from the database
        db.session.delete(chosen_file)
        db.session.commit()
        flash("File successfully deleted.")

    except Exception as e:
        e_type, e_object, e_tb = sys.exc_info()
        fname = os.path.split(e_tb.tb_frame.f_code.co_filename)[1]
        print(e_type, fname, e_tb.tb_lineno)
    
    return redirect(url_for('home_page'))


@app.route("/login", methods=['GET', 'POST'])
def login_page(): 
    """ Display a page for user login to the application. """
    # if current user is already authenticated, load home page
    
    users = User.query.all()

    for user in users:
        print(user.username)

    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        ### functionality for a user to log into the application
        user = User.query.filter_by(username=form.username.data).first()
        print(user)
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password, please try again.")
            return redirect(url_for('login_page'))
        login_user(user, remember=form.remember_me.data)
        # navigate to next page parameter, as given by flask-login @login_required
        next_page = request.args.get('next')
        # parse next page using werkzeugs url parse
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home_page')
        flash("Welcome back {0}".format(form.username.data))
        return redirect(url_for('home_page'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("Successfully logged out.")
    return redirect(url_for('home_page'))