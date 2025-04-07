from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlalchemy as sqla
from sqlalchemy import create_engine, text
import joblib
import numpy as np
import pandas as pd
import os
import traceback
import requests

# Database connection details
USER = "denissemenov"
PASSWORD = "897641579123"
PORT = "3306"
DB = "dbbikes"
URI = "127.0.0.1"
connection_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB)

# Flask App initialization
app = Flask(__name__, template_folder="templates")
CORS(app)

# Load the trained model at app startup
model = joblib.load('linear_regression_bikes_model.pkl')

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/explore")
def explore():
    return render_template("explore.html")

@app.route("/plans")
def plans():
    return render_template("plans.html")

@app.route("/ride")
def ride():
    return render_template("ride.html")

@app.route("/journeyplan")
def journeyplan():
    return render_template("journeyplan.html")

@app.route('/api/stations', methods=['GET'])
def get_stations():
    engine = create_engine(connection_string, echo=True)
    with engine.connect() as connection:
        result = connection.execute(sqla.text("SELECT number, name, lat, lng FROM station"))
        stations = [dict(row) for row in result.mappings()]
    return jsonify(stations)

@app.route('/api/availability', methods=['GET'])
def get_availability():
    engine = create_engine(connection_string, echo=True)
    with engine.connect() as connection:
        result = connection.execute(sqla.text("SELECT a.number, s.bikestands, a.available_bike_stands, a.available_bikes, a.last_update FROM station s, availability a JOIN (SELECT number, MAX(last_update) AS max_last_update FROM availability GROUP BY number) AS latest ON a.number = latest.number AND a.last_update = latest.max_last_update ORDER BY a.number;"))
        availability = [dict(row) for row in result.mappings()]
    return jsonify(availability)

# New prediction endpoint
@app.route('/api/predict_availability', methods=['POST'])
def predict_availability():
    try:
        data = request.get_json()
        station_id = int(data['station_id'])
        datetime_str = data['datetime']  # format: 'YYYY-MM-DD HH:MM:SS'

        pred_time = pd.to_datetime(datetime_str)
        hour = pred_time.hour
        dow = pred_time.dayofweek

        # Fetch latest availability from DB as lag feature
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            query = text("SELECT available_bikes FROM availability WHERE number = :station_id ORDER BY last_update DESC LIMIT 1")
            result = connection.execute(query, {"station_id": station_id}).fetchone()
            lag1 = result[0] if result else 10  # fallback value if unavailable

        # Generate model features
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)

        features = np.array([[lag1, hour_sin, hour_cos]])
        predicted_bikes = model.predict(features)[0]

        return jsonify({
            'station_id': station_id,
            'datetime': datetime_str,
            'predicted_bikes_available': int(round(predicted_bikes))
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Weather and routes endpoints (existing code, unchanged)
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
