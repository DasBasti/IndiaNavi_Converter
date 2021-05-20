import gpxpy
import gpxpy.gpx
import download
import sys

zoom=16
gpx_data = open(sys.argv[1], 'r')
jobfolder = sys.argv[1].rsplit(".")[0]

gpx = gpxpy.parse(gpx_data)

lat=[90,-90]
lon=[180,-180]

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            if(point.latitude < lat[0]): lat[0] = point.latitude
            if(point.latitude > lat[1]): lat[1] = point.latitude
            if(point.longitude < lon[0]): lon[0] = point.longitude
            if(point.longitude > lon[1]): lon[1] = point.longitude
            
print('Box at ({0},{1}) -> ({2},{3})'.format(lat[0], lon[0], lat[1], lon[1]))
download.get_map(lon, lat, [16], jobfolder)
