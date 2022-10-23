from webservice import download

zoom = 16


gps1 = [49.655037613307485, 8.565055542401264]
gps2 = [49.655037613307485, 8.565055542401264]

lat = [gps1[0], gps2[0]]
lon = [gps1[1], gps2[1]]


print('Box at ({0},{1}) -> ({2},{3})'.format(lat[0], lon[0], lat[1], lon[1]))
download.get_map(lon, lat, [16], "job")
print('Check: http://platinenmacher.tech/navi/index.html?lat1={0}&lon1={1}&lat2={2}&lon2={3}'.format(
    lat[0], lon[0], lat[1], lon[1]))
