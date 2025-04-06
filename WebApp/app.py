from flask import Flask, render_template, url_for, jsonify, request, redirect
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
import joblib
import numpy as np

# Login Functionality imports along flask SQLite imports - SQLite is only used for the login system.
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, Regexp
from flask_bcrypt import Bcrypt

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

# Load ML models
regression_model = joblib.load("WebApp/regression_model.pkl")
classification_model = joblib.load("WebApp/classification_model.pkl")
forecast_model = joblib.load("WebApp/forecast_model.pkl")

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

# Logic taken from https://www.youtube.com/watch?v=71EU8gnZqZQ&t=4s and https://flask-login.readthedocs.io/en/latest/

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'samplekey'

users_db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(users_db.Model, UserMixin):
    id = users_db.Column(users_db.Integer, primary_key=True)
    username = users_db.Column(users_db.String(20), nullable=False, unique=True)
    password = users_db.Column(users_db.String(256), nullable=False)

if not os.path.exists('users.db'):
    with app.app_context():
        users_db.create_all()

class RegisterUser(FlaskForm):
    username = StringField(validators = [
                            InputRequired(), 
                            Length(min = 4, max = 20)],
                            render_kw = {'placeholder': 'Username'}
                            )
    
    password = PasswordField(validators = [
                            InputRequired(), 
                            Length(min = 4, max = 20),
                            Regexp(
                                r'^(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).+$',
                                message='Password must contain at least one uppercase letter, one special character and one digit.'
                            )],
                            render_kw = {'placeholder': 'Password'}
                            )

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_username = User.query.filter_by(username = username.data).first()

        if existing_username:
            raise ValidationError('Error: Username is already in use. Please enter a different Username.')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginUser()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return render_template('login_success.html', username=form.username.data)

    return render_template('login_account.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterUser()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username = form.username.data, password = hashed_password)

        users_db.session.add(new_user)
        users_db.session.commit()

        return render_template('registration_success.html', username=form.username.data)

    return render_template('register_account.html', form=form)

@app.route('/predict', methods=['POST'])
def predict_bikes():
    data = request.json
    features = np.array([[
        data['station_id'], data['hour'], data['day'], data['month'], data['year'],
        data['max_temp'], data['min_temp'], data['max_humidity'], data['min_humidity'],
        data['max_pressure'], data['min_pressure']
    ]])
    prediction = regression_model.predict(features)
    return jsonify({'predicted_bikes': int(prediction[0])})

@app.route('/classify', methods=['POST'])
def classify_bike_availability():
    data = request.json
    features = np.array([[
        data['station_id'], data['hour'], data['day'], data['month'], data['year'],
        data['max_temp'], data['min_temp'], data['max_humidity'], data['min_humidity'],
        data['max_pressure'], data['min_pressure']
    ]])
    prediction = classification_model.predict(features)
    return jsonify({'bike_available': bool(prediction[0])})

@app.route('/forecast', methods=['POST'])
def forecast_bikes():
    # Assume forecast model was trained on hourly data for station 32
    forecast = forecast_model.predict(forecast_model.fh)
    forecast_list = forecast.tolist()
    return jsonify({'forecast': forecast_list})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
