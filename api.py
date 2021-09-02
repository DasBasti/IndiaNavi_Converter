import gpx_converter
from os import path
from flask import Flask, jsonify, flash, request, redirect, make_response, url_for
from werkzeug.utils import secure_filename
import hashlib
import json
import requests
from PIL import Image, ImageFilter
from io import BytesIO
import pal
import epd5in65f

UPLOAD_FOLDER = './gpx'
ALLOWED_EXTENSIONS = {'gpx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['APPLICATION_ROOT'] = "/navi/api"


epd = epd5in65f.EPD()

@app.route('/')
def index():
    return jsonify(version='1.0', text='IndiaNavi API V1.0')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/gpx', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        gpx_converter.url_base = url_for('index')
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
            data = json.dumps(gpx_converter.convert(filename, file))
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

@app.route('/tile/<z>/<x>/<y>.<ext>', methods=['GET'])
def convert_tile(z,x,y,ext):
    url = "https://platinenmacher.tech/navi/tiles/{z}/{x}/{y}.png".format(z=z, x=x, y=y)
    print("GET:", url)
    req = requests.get(url)
    t = Image.open(BytesIO(req.content))
    out = t.convert("RGB").filter(ImageFilter.EDGE_ENHANCE)

    out_pixel = out.load()

    for px in range(t.size[0]):
        for py in range(t.size[1]):
            out_pixel[px, py] = pal.map_color(out_pixel[px, py], px, py)

    print("Response for", ext)
    if ext == 'png':
        img = BytesIO()
        out.save(img, format='png')
        response = make_response(img.getvalue())
        response.headers.set('Content-Type', 'image/png')
        response.headers.set(
            'Content-Disposition', 'attachment', filename="{}.png".format(y))
        return response
    if ext == 'raw':
        response = make_response(bytearray(epd.getbuffer(out)))
        response.headers.set('Content-Type', 'application/x-binary')
        response.headers.set(
            'Content-Disposition', 'attachment', filename="{}.raw".format(y))
        return response

"""
    out.save(job.get("img_folder") +
             job.get("img_file").replace(".png", "_dt.png"))

    # lz4 compress raw image
    z = open((job.get("lz4_folder")+job.get("img_file")
              ).split(".")[0]+".lz4", "w+b")
    z.write(lz4.frame.compress(bytearray(epd.getbuffer(out))))
    z.close()

    r = open((job.get("job_folder")+job.get("img_file")
              ).split(".")[0]+".raw", "w+b")
    r.write(bytearray(epd.getbuffer(out)))
    r.close()
    return("{0} -> {1}".format(url, job.get("img_folder")+job.get("img_file")))

"""


if __name__ == "__main__":
    app.run(debug = True)