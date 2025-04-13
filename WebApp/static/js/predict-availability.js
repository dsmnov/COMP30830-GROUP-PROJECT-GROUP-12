/**
 * predict-availability.js
 *
 * This script handles bike availability prediction for the Journey Planner view.
 * It:
 * - Reads user input (station ID, date, and time)
 * - Sends a request to the Flask API backend
 * - Displays the predicted number of bikes and docks
 * - Optionally includes weather details if available
 *
 * This function is triggered by the "Predict" button click once the DOM has loaded.
 */

export async function predictAvailability() {
    // Grab user inputs
    const stationId = document.getElementById("station_id").value;
    const date = document.getElementById("date").value;
    const time = document.getElementById("time").value;
    const resultDiv = document.getElementById("result");
  
    // Validate input
    if (!stationId || !date || !time) {
      resultDiv.innerHTML = "Please fill out all fields.";
      return;
    }
  
    // Format time (Flask expects full HH:MM:SS format)
    const formattedTime = time + ":00";
  
    // Call Flask API to get the prediction
    fetch(`/api/availability/prediction?station_id=${stationId}&date=${date}&time=${formattedTime}`)
      .then(response => response.json())
      .then(data => {
        // Handle a successful prediction response
        if (data.predicted_available_bikes !== undefined) {
          if (data.weather_available) {
            // Show both prediction and weather
            resultDiv.innerHTML = `
              <p><b>Predicted Bikes:</b> ${data.predicted_available_bikes}</p>
              <p><b>Predicted Parking:</b> ${data.predicted_available_docks}</p>
              <p><b>Temperature:</b> ${Math.round(data.weather.temperature)}°C</p>
              <p><b>Precipitation:</b> ${Math.round(data.weather.precipitation)}%</p>
            `;
          } else {
            // Show prediction only (no weather)
            resultDiv.innerHTML = `
              <p><b>Predicted Bikes:</b> ${data.predicted_available_bikes}</p>
              <p><b>Predicted Parking:</b> ${data.predicted_available_docks}</p>
            `;
          }
        } else {
          // Handle valid API response but no prediction data
          resultDiv.innerHTML = "Prediction failed: " + (data.error || "Unknown error");
        }
      })
      .catch(err => {
        // Handle network or unexpected errors
        console.error("Prediction error:", err);
        resultDiv.innerHTML = "Error: " + err.message;
      });
  }
  
  // Attach event listener after DOM is ready
  document.addEventListener("DOMContentLoaded", function () {
    const predictBtn = document.getElementById("predictButton");
    if (predictBtn) {
      predictBtn.addEventListener("click", predictAvailability);
    }
  });
