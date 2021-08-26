from os import write, mkdir
import gpxpy
import gpxpy.gpx
import math

url_template = "https://platinenmacher.tech/navi/tiles/{z}/{x}/{y}.png"


def lon2tile(lon, zoom):
    return math.floor(((lon + 180) / 360) * math.pow(2, zoom))


def lat2tile(lat, zoom):
    return math.floor(((1 - math.log(math.tan((lat * math.pi) / 180) + 1 / math.cos((lat * math.pi) / 180)) / math.pi) / 2) * math.pow(2, zoom))


def get_jobs_for(lon, lat, zoom):
    # generate tile limits for area
    x = [lon2tile(lon[0], zoom), lon2tile(lon[1], zoom)]
    y = [lat2tile(lat[0], zoom), lat2tile(lat[1], zoom)]

    # switch if reversed
    if y[0] > y[1]:
        a = y[0]
        y[1] = y[0]
        y[0] = a

    if x[0] > x[1]:
        a = x[0]
        x[1] = x[0]
        x[0] = a

    # add tiles to the limits
    x[1] += 10
    x[0] -= 10
    y[1] += 10
    y[0] -= 10

    jobs = []
    for dx in range(abs(x[1]-x[0])):
        for dy in range(abs(y[1]-y[0])):
            url = url_template.format(z=zoom, x=x[0]+dx, y=y[0]+dy)
            jobs.append(url)
    return jobs


def convert(filename, data_file):
    zoom = [16, 13]
    gpx = gpxpy.parse(data_file)

    lat = [90, -90]
    lon = [180, -180]

    output = {"wps": [], "urls": []}

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if(point.latitude < lat[0]):
                    lat[0] = point.latitude
                if(point.latitude > lat[1]):
                    lat[1] = point.latitude
                if(point.longitude < lon[0]):
                    lon[0] = point.longitude
                if(point.longitude > lon[1]):
                    lon[1] = point.longitude
                output['wps'].append(
                    {"lon": point.longitude, "lat": point.latitude})

    for z in zoom:
        output['urls'] += get_jobs_for(lon, lat, z)

    return output
