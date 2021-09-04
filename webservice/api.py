import gpx_converter
from flask import Flask, jsonify, flash, request, redirect, make_response, url_for
from werkzeug.utils import secure_filename
import hashlib
import requests
from PIL import Image, ImageFilter
from io import BytesIO
import pal
import epd5in65f
from threading import Thread
import redis
import json
from os import path
r = redis.Redis('localhost')

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
        gpx_converter.url_base = "https://platinenmacher.tech/indianavi"
        # check if the post request has the file part
        if 'device-id' not in request.form:
            return jsonify(error="no device-id field")
        
        device_hash = hashlib.sha1(
            request.form['device-id'].encode()).hexdigest()
        
        print("Generate job", device_hash)
        
        if 'file' not in request.files:
            return jsonify(error="No file part")
        file = request.files['file']
        
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return jsonify(error="No filename")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            result = gpx_converter.convert(filename, file)
            result['status'] = "false"
            result['id'] = device_hash
            #result['urls'] = json.dumps(result['urls'])
            #result['wps'] = json.dumps(result['wps'])
            resstr = json.dumps(result)
            print(type(resstr))
            r.hset(device_hash, "data", resstr)
            r.hset(device_hash, "files", len(result['urls']))
            r.hset(device_hash, "done", 0)
            thread = Thread(target=run_download_task, args=(device_hash,))
            thread.daemon = True
            thread.start()
            return redirect(url_for('get_status', id=device_hash))

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
    tile_file = "tiles/{z}_{x}_{y}.png".format(z=z, x=x, y=y)
    print("get file:", tile_file)
    if path.exists(tile_file):
        print("cache hit")
        out = Image.open(tile_file)
    else:
        print("cache miss")
        url = "https://platinenmacher.tech/navi/tiles/{z}/{x}/{y}.png".format(z=z, x=x, y=y)
        print("GET:", url)
        req = requests.get(url)
        if req.status_code != 200:
            return jsonify(error="error while downloading")
        t = Image.open(BytesIO(req.content))
        out = t.convert("RGB").filter(ImageFilter.EDGE_ENHANCE)

        out_pixel = out.load()

        for px in range(t.size[0]):
            for py in range(t.size[1]):
                out_pixel[px, py] = pal.map_color(out_pixel[px, py], px, py)
        
        out.save(tile_file)

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

@app.route('/status/<id>')
def get_status(id):
    job = json.loads(r.hget(id, "data"))
    files = int(r.hget(id, "files"))
    files_done = int(r.hget(id, "done"))
    if job:
        return jsonify({"status": job['status'], "files": files, "done": files_done, "url": "https://platinenmacher.tech/indianavi"+url_for('static', filename=id+".zip")})
    else:
        return jsonify(error="Can not find job "+id)

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

from os import makedirs, getcwd, path
import urllib.request
import shutil
import socket
socket.setdefaulttimeout(300)
def run_download_task(id):
    job = json.loads(r.hget(id, "data"))
    print("Starte job", id)
    for u in job['urls']:
        tile_path = "gpx/"+id+"/MAPS/"+u['name']
        makedirs(path.dirname(tile_path), exist_ok=True)
        urllib.request.urlretrieve(u['uri'], tile_path)
        r.hincrby(id, "done", 1)
    tf = getcwd()+"/gpx/"+id
    makedirs("gpx/"+id, exist_ok=True)
    with open(tf+"/TRACK", 'w') as t:
        for wp in job['wps']:
            t.write("{} {}\n".format(wp['lon'], wp['lat']))
    shutil.make_archive("static/"+id, "zip", "gpx/"+id)
    job['status'] = "true"
    r.hset(id, "status", "true")

if __name__ == "__main__":
    app.run(debug = True, threaded=True)