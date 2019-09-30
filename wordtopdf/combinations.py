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


def combine_directory(target_directory):
    """ Combine all pdf documents each folder in the given directory """
    folder_list = [x for x in os.listdir(target_directory) if (x.find(".DS") == -1 and 
                    x.find(".doc")== -1 and x.find(".pdf") == -1)]
    for folder in folder_list:
        current_folder = '/'.join([target_directory, folder])
        filenames = [x for x in os.listdir(current_folder) if x.endswith(".pdf")]
        # create pdf merger object and iterate through cwd files
        merger = PdfFileMerger()

        print("Converting files in folder {}".format(folder))
        print("List of files: {}".format(filenames))

        filenames.sort()
        
        for filename in filenames:
            # only append file if its a pdf
            if filename.endswith(".pdf"):

                current_file = '/'.join([current_folder, filename])

                # append pdf to our merge object
                f = open(current_file, 'rb')
                merger.append(PdfFileReader(f))

        pdf_name = "_".join([folder, "combined.pdf"])

        # write our final pdf with the appended pdf files
        merger.write(target_directory + "/" + pdf_name)

        print("Successfully converted folder {} to a single pdf.".format(folder))

    # return sorted list of filenames for producing the ordered final document
    combined_files = ["_".join([x, "combined.pdf"]) for x in folder_list]
    combined_files.sort()

    return combined_files


def combine_conversions(target_directory, ordering_list, file_name):
    """ Combines all pdf combinations using the given directory and ordering """
    merger = PdfFileMerger()
    for document in ordering_list:
        current_file = '/'.join([target_directory, document])

        # append pdf to our merge object
        f = open(current_file, 'rb')
        merger.append(PdfFileReader(f))
    name = file_name.replace(".zip", "")
    pdf_name = str(name) + "_Combined.pdf"

    # write our final pdf with the appended pdf files
    merger.write(app.config['UPLOAD_FOLDER'] + "/" + pdf_name)
    
    return pdf_name
