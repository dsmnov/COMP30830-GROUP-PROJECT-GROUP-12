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
    USER = "denissemenov"
    PASSWORD = "897641579123"
    PORT = "3306"
    DB = "dbbikes"
    URI = "127.0.0.1"

    connection_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB)

    engine = create_engine(connection_string, echo = True)

    with engine.connect() as connection:
        result = connection.execute(sqla.text("SELECT name, lat, lng FROM station"))
        stations = [dict(row) for row in result.mappings()]

    return jsonify(stations)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)