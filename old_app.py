# Instructions: Run script in Python 3 with 1st arg - destination directory, and 2nd arg source directory
# e.g. python3 convert_recursive_dir_doc_to_pdf.py dest_folder/ source_folder/

from werkzeug.utils import secure_filename
from config import config
from flask import Flask, render_template, request, jsonify, send_from_directory
from PyPDF2 import PdfFileMerger, PdfFileReader
import sys
import subprocess
import re
import os

app = Flask(__name__, static_url_path='')


### Flask app functionality ###
@app.route('/')
def home_page():
    """ Render the main app page """
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """ Accept a file for uploading and converting into pdf from word """
    upload_id = str(uuid4())
    source = save_to(os.path.join(config['uploads_dir'], 'source', upload_id), request.files['file'])

    try:
        result = convert_to(os.path.join(config['uploads_dir'], 'pdf', upload_id), source, timeout=15)
    except LibreOfficeError:
        raise InternalServerErrorError({'message': 'Error when converting file to PDF'})
    except TimeoutExpired:
        raise InternalServerErrorError({'message': 'Timeout when converting file to PDF'})

    return jsonify({'result': {'source': uploads_url(source), 'pdf': uploads_url(result)}})


@app.route('uploads/<path:path>', methods=['GET'])
def serve_uploads(path):
    return send_from_directory(config['uploads_dir'], path)


@app.errorhandler(500)
def handle_500_error():
    return InternalServerErrorError().to_response()


@app.errorhandler(RestAPIError)
def handle_rest_api_error(error):
    return error.to_response()


class RestAPIError(Exception):
    def __init__(self, status_code=500, payload=None):
        self.status_code = status_code
        self.payload = payload

    def to_response(self):
        return jsonify({'error': self.payload}), self.status_code


class BadRequestError(RestAPIError):
    def __init__(self, payload=None):
        super().__init__(400, payload)


class InternalServerErrorError(RestAPIError):
    def __init__(self, payload=None):
        super().__init__(500, payload)


### Functions for dealing with word to pdf conversions using Libreoffice ###
def convert_to(dest_folder, source_file, timeout=None):
    args = [libreoffice_exec(), '--headless', '--convert-to', 'pdf', '--outdir', dest_folder, source_file]

    # run subprocess to convert document to pdf using libreoffice
    process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    filename = re.search('-> (.*?) using filter', process.stdout.decode())

    if filename is None:
        raise LibreOfficeError(process.stdout.decode())
    else:
        return filename.group(1)

def uploads_url(path):
    """ Return the path for the upload url. """
    return path.replace(config['uploads_dir'], '/uploads')

def save_to(folder, file):
    """ Save file to given folder location """
    os.makedirs(folder, exist_ok=True)
    save_path = os.path.join(folder, secure_filename(file.filename))
    file.save(save_path)
    return save_path


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
            #print("Converted {0} to pdf.".format(file_name))
    else:
        print("No files found in given directory: {0}".format(source_directory))


def convert_recursive_directory(dest_folder, source_directory):
    # first convert all doc / docx files in the top directory given
    convert_directory(dest_folder, source_directory)

    # now iterate through each folder and convert all files within
    folder_list = [x for x in os.listdir(source_directory) if (x.find(".DS") == -1 and x.find(".doc")== -1)]
    for folder in folder_list:
        dest = '/'.join([dest_folder, folder])
        source = '/'.join([source_directory, folder])
        os.mkdir(dest)
        convert_directory(dest, source)
        print("Successfully converted folder {0} to pdf.".format(folder))


def combine_pdf_directory(target_directory):
    folder_list = [x for x in os.listdir(target_directory) if (x.find(".DS") == -1 and 
                    x.find(".doc")== -1 and x.find(".pdf") == -1)]
    for folder in folder_list:
        current_folder = '/'.join([target_directory, folder])
        filenames = [x for x in os.listdir(current_folder) if x.endswith(".pdf")]
        # create pdf merger object and iterate through cwd files
        merger = PdfFileMerger()

        filenames.sort()

        print("Converting files in folder {}".format(folder))
        print("List of files: {}".format(filenames))

        for filename in filenames:
            # only append file if its a pdf
            if filename.endswith(".pdf"):

                current_file = '/'.join([current_folder, filename])

                # append pdf to our merge object
                merger.append(PdfFileReader(file(current_file, 'rb')))

        pdf_name = "_".join([folder, "combined.pdf"])

        # write our final pdf with the appended pdf files
        merger.write(target_directory + "/" + pdf_name)

        print("Successfully converted folder {} to a single pdf.".format(folder))


def combine_pdf_conversions(target_directory, ordering_list):
    merger = PdfFileMerger()
    for document in AESO_ORDERING:
        current_file = '/'.join([target_directory, document])
        # append pdf to our merge object
        merger.append(PdfFileReader(file(current_file, 'rb')))
    pdf_name = "47_AESOs_Combined.pdf"
    # write our final pdf with the appended pdf files
    merger.write(target_directory + "/" + pdf_name)


if __name__ == '__main__':
    # ensure we tell the server to use threaded to handle multiple requests 
    # TO-DO: integrate gunicorn into the app
    # remember to turn off debug mode in production
    app.run(debug=True, host='0.0.0.0', threaded=True)