from gpx_converter import convert
from os import path
from flask import Flask, jsonify, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import hashlib
import json

UPLOAD_FOLDER = './gpx'
ALLOWED_EXTENSIONS = {'gpx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return jsonify(version='1.0', text='IndiaNavi API V1.0')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/gpx', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        device_hash = hashlib.sha1(
            request.form['device-id'].encode()).hexdigest()
        print(device_hash)
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            data = json.dumps(convert(filename, file))
            with open(app.config['UPLOAD_FOLDER']+"/"+device_hash+".track", "w") as f:
                f.write(data)
            return device_hash
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
      <input type=text name="device-id" value="1234567890">
    </form>
    '''
