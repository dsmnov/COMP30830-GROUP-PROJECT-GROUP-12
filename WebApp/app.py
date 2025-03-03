from flask import Flask, render_template, url_for, jsonify
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

@app.route("/api/stations", methods=["GET"])
def get_stations():
    engine = create_engine(connection_string, echo = True)

    with engine.connect() as connection:
        result = connection.execute(sqla.text("SELECT number, name, lat, lng FROM station"))
        stations = [dict(row) for row in result.mappings()]

    return jsonify(stations)

@app.route("/api/availability", methods=["GET"])
def get_availability():
    engine = create_engine(connection_string, echo = True)

    with engine.connect() as connection:
        result = connection.execute(sqla.text("SELECT a.number, a.available_bike_stands, a.available_bikes, a.last_update FROM availability a JOIN (SELECT number, MAX(last_update) AS max_last_update FROM availability GROUP BY number) AS latest ON a.number = latest.number AND a.last_update = latest.max_last_update ORDER BY a.number;"))
        availability = [dict(row) for row in result.mappings()]

    return jsonify(availability)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)