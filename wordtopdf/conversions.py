#!/usr/bin/env python

from PyPDF2 import PdfFileMerger, PdfFileReader
import sys
import subprocess
import shutil
import re
import os
import zipfile

from wordtopdf import app


def libreoffice_exec():
    # libreoffice 
    if sys.platform == 'darwin':
        return '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    return 'libreoffice'

class LibreOfficeError(Exception):
    def __init__(self, output):
        self.output = output

def convert_directory(dest_folder, source_directory):
    file_list = [x for x in os.listdir(source_directory) if (x.endswith('.doc') or x.endswith('.docx'))]
    if len(file_list) > 0:
        print("Converting docs in directory {0} to pdf to destination {1}".format(source_directory, dest_folder))
        for file_name in file_list:
            convert_to(dest_folder, '/'.join([source_directory, file_name]), timeout=20)
    else:
        print("No files found in given directory: {0}".format(source_directory))


def convert_recursive_directory(dest_folder, source_directory):
    # first convert all doc / docx files in the top directory given
    convert_directory(dest_folder, source_directory)

    # now iterate through each folder and convert all files within
    folder_list = [x for x in os.listdir(source_directory) if (x.find(".DS") == -1 and 
                                                                x.find(".doc")== -1 and x.find("MACOSX") == -1)]
    for folder in folder_list:
        dest = '/'.join([dest_folder, folder])
        source = '/'.join([source_directory, folder])
        os.makedirs(dest, exist_ok=True)
        convert_directory(dest, source)
        print("Successfully converted folder {0} to pdf.".format(folder))


def convert_to(dest_folder, source_file, timeout=None):
    """ Function for converting word to pdf using Libreoffice """
    args = [libreoffice_exec(), '--headless', '--convert-to', 'pdf', '--outdir', dest_folder, source_file]

    # run subprocess to convert document to pdf using libreoffice
    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    filename = re.search('-> (.*?) using filter', process.stdout.decode())

    if filename is None:
        raise LibreOfficeError(process.stdout.decode())
    else:
        return filename.group(1)

