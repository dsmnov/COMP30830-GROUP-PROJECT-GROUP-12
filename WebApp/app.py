from flask import Flask, render_template, url_for, jsonify, request, redirect, send_from_directory
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
from datetime import datetime
import pymysql
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET

# Login Functionality imports along flask SQLite imports - SQLite is only used for the login system.
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, Regexp
from flask_bcrypt import Bcrypt

# Machine learning Imports
import numpy as np
import pandas as pd
import pickle


# Database access and connection_string for Station and Availability
USER = "denissemenov"
PASSWORD = "897641579123"
PORT = "3306"
DB = "dbbikes"
URI = "127.0.0.1"
connection_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB)

# Instace folder directory for the SQLite database
instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')

# Start of Flask backend running code
app = Flask(__name__, template_folder="templates", instance_relative_config=True, instance_path=instance_path)
CORS(app)


# Webpage routing section
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

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("user-system/dashboard.html")


# Main Station and Availability API endpoints
@app.route('/api/stations', methods=['GET'])
def get_stations():
    engine = create_engine(connection_string, echo = True)

    with engine.connect() as connection:
        result = connection.execute(sqla.text("SELECT number, name, lat, lng FROM station ORDER BY station.number;"))
        stations = [dict(row) for row in result.mappings()]

    return jsonify(stations)

@app.route('/api/availability', methods=['GET'])
def get_availability():
    engine = create_engine(connection_string, echo = True)

    with engine.connect() as connection:
        query = sqla.text("""
            SELECT
                s.number,
                s.bikestands,
                a.available_bike_stands,
                a.available_bikes,
                a.last_update
            FROM station s
            JOIN (
                SELECT 
                    number, 
                    MAX(last_update) AS max_last_update
                FROM availability
                GROUP BY number
            ) AS latest ON s.number = latest.number
            JOIN availability a 
                ON s.number = a.number
                AND a.last_update = latest.max_last_update
            ORDER BY s.number;
        """)
        result = connection.execute(query)
        availability = [dict(row) for row in result.mappings()]

    return jsonify(availability)

# API routes endpoint
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
        data = r.json()
        return jsonify(data)
    except Exception as e:
        print('Routes error:', e)
        return jsonify({'error': str(e)}), 500

# Met eireann endpoint for dublin, based on station coordinates for more precise data
@app.route('/api/weather', methods=['POST'])
def get_weather():
    data = request.get_json()
    lat = data.get('lat', '54.7211')
    long = data.get('lng', '-8.7237')
    time = data.get('time', '2025-03-31T22:00:00Z') 

    query = f'http://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast?lat={lat};long={long};from={time};to={time}'
    
    response = requests.get(query)
    return response.text

@app.route('/api/weather/icon', methods=['POST'])
def get_weather_icon():
# Older implementation I used however I found a better one on the website to use down below
#    query = 'https://www.met.ie/Open_Data/xml/obs_present.xml'
#    response = requests.get(query)
#
#    root = ET.fromstring(response.text)
#    for station in root.findall('station'):
#        if station.attrib.get('name', '').lower() == 'dublin':
#            icon_data = root.find('symbol')
#            icon_name = icon_data.text.strip()
#            return icon_name
#   return '01d' # Testing code
    query = 'https://prodapi.metweb.ie/observations/Dublin/today'
    response = requests.get(query)

    data = response.json()
    current_report = data[-1]
    icon = current_report.get('symbol')

    return str(icon)


# Logic taken from https://www.youtube.com/watch?v=71EU8gnZqZQ&t=4s and https://flask-login.readthedocs.io/en/latest/

# SQLite connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'samplekey'

# SQLAlchemy and password hashing connections to the database
users_db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Login manager from flask documentation
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home'

# Loads user from the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# User Class and defines details for database
class User(users_db.Model, UserMixin):
    id = users_db.Column(users_db.Integer, primary_key=True)
    username = users_db.Column(users_db.String(20), nullable=False, unique=True)
    password = users_db.Column(users_db.String(256), nullable=False)

# Create the database file if none present
if not os.path.exists('users.db'):
    with app.app_context():
        users_db.create_all()

# Method of registration using flask form
class RegisterUser(FlaskForm):
    username = StringField(validators = [
                            InputRequired(), 
                            Length(min = 4, max = 20)],
                            render_kw = {'placeholder': 'Username'}
                            )
    
    password = PasswordField(validators = [
                            InputRequired(), 
                            Length(min = 4, max = 20),
                            # Ensuring password requirements are met, 1 caps, 1 number, 1 special character
                            Regexp(
                                r'^(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).+$',
                                message='Password must contain at least one uppercase letter, one special character and one digit.'
                            )],
                            render_kw = {'placeholder': 'Password'}
                            )

    submit = SubmitField('Register')

    # Checks no duplicates of users
    def validate_username(self, username):
        existing_username = User.query.filter_by(username = username.data).first()

        if existing_username:
            raise ValidationError('Error: Username is already in use. Please enter a different Username.')

# Method of logging in user
class LoginUser(FlaskForm):
    username = StringField(validators = [
                            InputRequired(), 
                            Length(min = 4, max = 20)],
                            render_kw = {'placeholder': 'Username'}
                            )
    
    password = PasswordField(validators = [
                            InputRequired(), 
                            Length(min = 4, max = 20)],
                            render_kw = {'placeholder': 'Password'}
                            )

    submit = SubmitField('Login')

# Login endpoint and validation logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginUser()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            # Following best practice, password is always held in hased format and compared against user hashed input
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)  

    return render_template('user-system/login_account.html', form=form)

# Register endpoint
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterUser()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username = form.username.data, password = hashed_password)

        users_db.session.add(new_user)
        users_db.session.commit()
        # Redirect to login form if user registration is successful
        return render_template('user-system/login_account.html', form=form)

    return render_template('user-system/register_account.html', form=form)

# Handle logout logic
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True}), 200

@app.route('/check_login', methods=['GET', 'POST'])
def check_login():
    if current_user.is_authenticated:
        return jsonify({'loggedIn': True}), 200
    else:
        return jsonify({'loggedIn': False}), 200

# Machine Learning Data Endpoint
def construct_stations_datafile():
    engine = create_engine(connection_string, echo=True)
    with engine.connect() as connection:
        query = text("SELECT number AS station_id, lat, lng FROM station ORDER BY station.number;")
        result = connection.execute(query).mappings().all()

        stations_df = pd.DataFrame(result, columns=['station_id', 'lat', 'lng'])
        return stations_df

OPENWEATHER_API_KEY = "6bdc51a9572de4755048b6b914f96e8c"

# Weather retrieval from OPENWEATHER
from datetime import datetime, timedelta

def get_weather_forecast(lat, lng, dt_requested):
    now = datetime.now()
    forecast_limit = now + timedelta(days=5)

    if dt_requested > forecast_limit:
        raise Exception("Forecast unavailable: date exceeds 5-day limit")

    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={lat}&lon={lng}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch weather data")

    data = response.json()
    requested_timestamp = dt_requested.timestamp()

    closest = min(
        data['list'],
        key=lambda f: abs(datetime.fromtimestamp(f['dt']).timestamp() - requested_timestamp)
    )

    return {
        "temperature": round(closest['main']['temp']),
        "humidity": round(closest['main']['humidity']),
        "wind_speed": round(closest['wind']['speed'], 1),
        "precipitation": round(closest.get('pop', 0) * 100)
    }

with open("machine-learning/bike_availability_weather_model.pkl", "rb") as f:
    model = pickle.load(f)

stations_df = construct_stations_datafile()

#Prediction Endpoint
@app.route('/api/availability/prediction', methods=['GET'])
def get_availability_prediction():
    date = request.args.get("date")
    time = request.args.get("time")
    station_id = request.args.get("station_id")

    if not date or not time or not station_id:
        return jsonify({"error": "Missing date, time, or station_id"}), 400

    try:
        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        day_of_week = dt.weekday()

        station = stations_df[stations_df['station_id'] == int(station_id)]
        if station.empty:
            return jsonify({"error": "Invalid station ID"}), 400

        lat = station.iloc[0]['lat']
        lng = station.iloc[0]['lng']

        # Get weather forecast, if available
        try:
            weather = get_weather_forecast(lat, lng, dt)
            weather_available = True
            temperature = weather["temperature"]
            humidity = weather["humidity"]
            wind_speed = weather["wind_speed"]
            precipitation = weather["precipitation"]
        except Exception as e:
            print("Weather unavailable:", e)
            weather = {}
            weather_available = False
            temperature = 11
            humidity = 75
            wind_speed = 3.5
            precipitation = 30

        # Predict bikes
        input_features = np.array([[int(station_id), hour, day_of_week, temperature, humidity]])
        predicted_bikes = int(model.predict(input_features)[0])

        # Fetch station capacity
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            bike_stands = connection.execute(
                text(f"SELECT bikestands FROM station WHERE number = {station_id}")
            ).scalar()

        predicted_docks = bike_stands - predicted_bikes

        return jsonify({
            "predicted_available_bikes": predicted_bikes,
            "predicted_available_docks": predicted_docks,
            "weather": weather,
            "weather_available": weather_available
        })

    except Exception as e:
        print("Prediction error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
