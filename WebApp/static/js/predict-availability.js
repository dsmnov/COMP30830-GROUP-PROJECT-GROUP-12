export async function _predict_availability() {
    // stationID value is set within markers.js journey planner code
    const stationId = document.getElementById("station_id").value;
    const date = document.getElementById("date").value;
    const time = document.getElementById("time").value;
    const resultDiv = document.getElementById("result");

    if (!stationId || !date || !time) {
        resultDiv.innerHTML = "Please fill out all fields.";
        return;
    }

    const formattedTime = time + ":00";

    // retrieve prediction from flask endpoint
    fetch(`/api/availability/prediction?station_id=${stationId}&date=${date}&time=${formattedTime}`)
        .then(response => response.json())
        .then(data => {
            if (data.predicted_available_bikes !== undefined) {
                resultDiv.innerHTML = `
                    <p><b>Predicted Bikes:</b> ${data.predicted_available_bikes}</p>
                    <p><b>Predicted Parking:</b> ${data.predicted_available_bike_stands}</p>
                    <p><b>Temperature:</b> ${data.weather.temperature}°C</p>
                    <p><b>Humidity:</b> ${data.weather.humidity}%</p>
                `;
            } else {
                resultDiv.innerHTML = "Prediction failed: " + (data.error || "Unknown error");
            }
        })
        .catch(err => {
            resultDiv.innerHTML = "Error: " + err.message;
        });
}

// Ensuring loading after content loaded
document.addEventListener('DOMContentLoaded', function() {
    const predictBtn = document.getElementById("predictButton");
    if (predictBtn) {
        predictBtn.addEventListener("click", _predict_availability);
    }
});