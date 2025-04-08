
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import numpy as np
import pandas as pd
import requests
import pickle

# Load the trained model
with open("bike_availability_model.pkl", "rb") as f:
    model = pickle.load(f)

# Load station coordinates
stations_df = pd.read_csv("final_merged_data.csv")[['station_id', 'lat', 'lon']].drop_duplicates()

# Replace with your actual OpenWeather API key
OPENWEATHER_API_KEY = "8d3db8ac62d93b208d6cf30ea6ef204c"

def get_weather_forecast(lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch weather data")
    data = response.json()
    forecast = data['list'][0]  # Forecast for next 3-hour slot

    return {
        "temperature": forecast['main']['temp'],
        "humidity": forecast['main']['humidity'],
        "pressure": forecast['main']['pressure']
    }

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict():
    try:
        date = request.args.get("date")
        time = request.args.get("time")
        station_id = request.args.get("station_id")

        if not date or not time or not station_id:
            return jsonify({"error": "Missing date, time, or station_id"}), 400

        dt = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        day = dt.day

        # Get station coordinates
        station = stations_df[stations_df['station_id'] == int(station_id)]
        if station.empty:
            return jsonify({"error": "Invalid station ID"}), 400

        lat = station.iloc[0]['lat']
        lon = station.iloc[0]['lon']

        # Fetch weather from OpenWeather API
        weather = get_weather_forecast(lat, lon)

        input_features = np.array([[
            int(station_id),
            hour,
            day,
            weather["temperature"],
            weather["humidity"],
            weather["pressure"]
        ]])

        prediction = model.predict(input_features)[0]

        return jsonify({
            "predicted_available_bikes": int(prediction[0]),
            "predicted_available_bike_stands": int(prediction[1]),
            "weather": weather
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    app.run(debug=True)
