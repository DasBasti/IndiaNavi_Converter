# IndiaNavi map generator

This repository contains files for the IndiaNavi GPX -> MAP generator service.
It takes a GPX file and generates a zip archive with waypoints and map tiles.

# Components

## Webservice

Flask application with api to generate tile archives.
Archive generation is done asynchronously. 

POST a gpx FILE to `/gpx` with a `device-id` field and get an <id> as JSON.
GET `/status/<id>` to check if `status` is True.
If true the archive is downloadable from the `url` provided by the status message.