import { getWeatherData } from './weather.js';
import { drawTripRoute } from './trip-router.js';

// Panel Switching Functions 

export function openQuickTrip() {
  document.getElementById("quick-trip-panel").style.display = "block";
  document.getElementById("plan-ahead-panel").style.display = "none";
}

export function openPlanAhead() {
  document.getElementById("quick-trip-panel").style.display = "none";
  document.getElementById("plan-ahead-panel").style.display = "block";
}

export async function startQuickTrip() {
  const startId = document.getElementById("quick-start-station").value;
  const destId = document.getElementById("quick-destination-station").value;
  const datetime = document.getElementById("quick-datetime").value;
  const [date, time] = datetime.split("T");

  const destUrl = `/api/availability/prediction?station_id=${destId}&date=${date}&time=${time}:00`;
  const dest = await fetch(destUrl).then(res => res.json());

  const stations = await fetch('/api/stations').then(res => res.json());
  const startStation = stations.find(s => s.number == startId);
  const destStation = stations.find(s => s.number == destId);
  if (startStation && destStation) {
    await drawTripRoute(
      { lat: startStation.lat, lng: startStation.lng },
      { lat: destStation.lat, lng: destStation.lng },
      window.map
    );
  }

  let output = `
    <h4>Arrival (Predicted Status)</h4>
    <p><b>Predicted Bikes:</b> ${dest.predicted_available_bikes}</p>
    <p><b>Predicted Parking:</b> ${dest.predicted_available_docks}</p>
  `;

  if (dest.weather_available) {
    output += `
      <p><b>Temperature:</b> ${Math.round(dest.weather.temperature)}°C</p>
      <p><b>Precipitation:</b> ${Math.round(dest.weather.precipitation)}%</p>
    `;
  }

  document.getElementById("quick-result").innerHTML = output;
}

async function updateLiveStartInfo() {
  const startId = document.getElementById("quick-start-station").value;
  const startData = await fetch('/api/availability').then(res => res.json());
  const start = startData.find(s => s.number == startId);

  const bikes = start?.available_bikes ?? "N/A";
  const docks = start?.available_bike_stands ?? "N/A";
  const lat = start?.lat;
  const lng = start?.lng;
  const name = start?.name ?? "Selected Station";

  const weather = await getWeatherData(lat, lng);
  const currentTemp = weather?.temperature ?? "Unknown";
  const windSpeed = weather?.windSpeed ?? "Unknown";
  const windDirection = weather?.windDirection ?? "Unknown";
  const humidity = weather?.humidity ?? "Unknown";

  const startHtml = `
    <h4>Departure (Live Status)</h4>
    <p><b>Available Bikes:</b> ${bikes}</p>
    <p><b>Available Parking:</b> ${docks}</p>
    <p><b>Temperature:</b> ${currentTemp}°C</p>
    <p><b>Humidity:</b> ${humidity}%</p>
    <p><b>Wind Direction:</b> ${windDirection}</p>
    <p><b>Wind Speed:</b> ${windSpeed}</p>
    <hr>
  `;

  document.getElementById("quick-live-result").innerHTML = startHtml;
}

export async function predictPlannedTrip() {
  const sId = document.getElementById("plan-start-station").value;
  const sDt = document.getElementById("plan-start-time").value;
  const dId = document.getElementById("plan-destination-station").value;
  const dDt = document.getElementById("plan-destination-time").value;

  const format = dt => {
    const [date, time] = dt.split("T");
    return { date, time: time + ":00" };
  };

  const { date: sDate, time: sTime } = format(sDt);
  const { date: dDate, time: dTime } = format(dDt);

  const sUrl = `/api/availability/prediction?station_id=${sId}&date=${sDate}&time=${sTime}`;
  const dUrl = `/api/availability/prediction?station_id=${dId}&date=${dDate}&time=${dTime}`;

  const [start, dest] = await Promise.all([
    fetch(sUrl).then(res => res.json()),
    fetch(dUrl).then(res => res.json())
  ]);

  const stations = await fetch('/api/stations').then(res => res.json());
  const startStation = stations.find(s => s.number == sId);
  const destStation = stations.find(s => s.number == dId);
  if (startStation && destStation) {
    await drawTripRoute(
      { lat: startStation.lat, lng: startStation.lng },
      { lat: destStation.lat, lng: destStation.lng },
      window.map
    );
  }

  const startHtml = `
    <h4>Departure (Predicted Status)</h4>
    <p><b>Predicted Bikes:</b> ${start.predicted_available_bikes}</p>
    <p><b>Predicted Parking:</b> ${start.predicted_available_docks}</p>
    ${start.weather_available ? `
      <p><b>Temperature:</b> ${Math.round(start.weather.temperature)}°C</p>
      <p><b>Precipitation:</b> ${Math.round(start.weather.precipitation)}%</p>
    ` : ""}
  `;

  const destHtml = `
    <h4>Arrival (Predicted Status)</h4>
    <p><b>Predicted Bikes:</b> ${dest.predicted_available_bikes}</p>
    <p><b>Predicted Parking:</b> ${dest.predicted_available_docks}</p>
    ${dest.weather_available ? `
      <p><b>Temperature:</b> ${Math.round(dest.weather.temperature)}°C</p>
      <p><b>Precipitation:</b> ${Math.round(dest.weather.precipitation)}%</p>
    ` : ""}
  `;

  document.getElementById("plan-start-result").innerHTML = startHtml;
  document.getElementById("plan-destination-result").innerHTML = destHtml;
}

document.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const mode = params.get("mode");

  if (mode === "quick") openQuickTrip();
  else if (mode === "plan") openPlanAhead();
  else {
    document.getElementById("quick-trip-panel").style.display = "none";
    document.getElementById("plan-ahead-panel").style.display = "none";
  }

  const quickBtn = document.getElementById("quick-predict-button");
  if (quickBtn) quickBtn.addEventListener("click", startQuickTrip);

  const planBtn = document.getElementById("plan-predict-button");
  if (planBtn) planBtn.addEventListener("click", predictPlannedTrip);

  const startSelect = document.getElementById("quick-start-station");
  if (startSelect) {
    startSelect.addEventListener("change", updateLiveStartInfo);
  }
});
