from flask import Flask, render_template, url_for, jsonify, request
from flask_cors import CORS
import sqlalchemy as sqla
from sqlalchemy import create_engine, text
import traceback
import glob
import os
from pprint import pprint
import simplejson as json
import requests
import time
from IPython.display import display
import traceback
import datetime
import time
import os
import pymysql

#Database access and connection_string
USER = "denissemenov"
PASSWORD = "897641579123"
PORT = "3306"
DB = "dbbikes"
URI = "127.0.0.1"
connection_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB)

#Start of Flask backend running code
app = Flask(__name__, template_folder="templates")
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/map")
def map_page():
    return render_template("map.html")

@app.route('/api/stations', methods=['GET'])
def get_stations():
    engine = create_engine(connection_string, echo = True)

    with engine.connect() as connection:
        result = connection.execute(sqla.text("SELECT number, name, lat, lng FROM station"))
        stations = [dict(row) for row in result.mappings()]

    return jsonify(stations)

@app.route('/api/availability', methods=['GET'])
def get_availability():
    engine = create_engine(connection_string, echo = True)

    with engine.connect() as connection:
        result = connection.execute(sqla.text("SELECT a.number, s.bikestands, a.available_bike_stands, a.available_bikes, a.last_update FROM station s, availability a JOIN (SELECT number, MAX(last_update) AS max_last_update FROM availability GROUP BY number) AS latest ON a.number = latest.number AND a.last_update = latest.max_last_update ORDER BY a.number;"))
        availability = [dict(row) for row in result.mappings()]

    return jsonify(availability)

@app.route('/api/routes', methods=['POST'])
def get_route():
    body = request.json
    origin_lat = body["origin"]["lat"]
    origin_lng = body["origin"]["lng"]
    dest_lat = body["destination"]["lat"]
    dest_lng = body["destination"]["lng"]

    routes_body = {
        "origin":{
            "location":{
                "latLng":{
                    "latitude": origin_lat,
                    "longitude": origin_lng
                }
            }
        },
        "destination":{
            "location":{
                "latLng":{
                    "latitude": dest_lat,
                    "longitude": dest_lng
                }
            }
        },
        "travelMode": "2",
        "routingPreference": "ROUTING_PREFERENCE_UNSPECIFIED",
    }

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": "AIzaSyAFdzfzeBk3A8ASwoklDgw2HG4n6ewF4Iw",
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
    }

    try:
        r = requests.post(url, json=routes_body, headers=headers)
        print("Google Routes response:", r.text)
        data = r.json()
        return jsonify(data)
    except Exception as e:
        print("Routes error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/weather', methods=['POST'])
def get_weather():
    data = request.get_json()
    lat = data.get('lat', '54.7211')
    long = data.get('lng', '-8.7237')
    time = data.get('time', '2025-03-31T22:00:00Z') 

    query = f'http://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat={lat};long={long};from={time};to={time}'
    
    response = requests.get(query)
    return response.text

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)