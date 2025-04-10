import { Marker } from './markers.js';
import { getWeatherIcon } from './weather.js';
export let markers = [];


// Initialise Google Maps
async function initMap() {
    const position = { lat: 53.3484, lng: -6.2539 };

    const { Map } = await google.maps.importLibrary('maps');
  
    return new Map(document.getElementById('map'), {
        zoom: 14,
        center: position,
        mapId: 'dbbikes_map',
    });
}


// Retrieve Station Data from endpoint
async function getStationData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/stations');
        return await response.json();
    } catch (error) {
        console.error('Error fetching station data:', error);
    }
}


// Retrieve availability data from endpoint
async function getAvailabilityData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/availability');
        return await response.json();
    } catch (error) {
        console.error('Error fetching availability data:', error);
    }
}


// Initialise the clickable station panel element
// More effieicent to have 1 station panel element that gets updated depending on which station is clicked than each have their own
async function initializeStationPanel() {
    const locationWindow = document.getElementById('locationWindow');
    const windowContent = document.getElementById('windowContent');
    let isWindowOpen = false;
  
    document.addEventListener('click', (event) => {
        if (isWindowOpen && !locationWindow.contains(event.target)) {
            locationWindow.classList.add('closing');
            
            setTimeout(() => {
                locationWindow.classList.remove('open');
                locationWindow.classList.remove('closing');
            }, 100);

            isWindowOpen = false;
        }
    });
  
    return {locationWindow, windowContent, setIsWindowOpen(value) {isWindowOpen = value;}};
}


// Main function that makes use of the seperated modular components such as markers, prediction, weather, etc.
async function main() {
    /* 
    >First start the map
    >Then import marker librarys
    >retrieve initial data sets from endpoints
    >construct each individual marker object with the fed data
    >start refresh loops for data
    */
    const map = await initMap();
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    const stationData = await getStationData();
    let availabilityData = await getAvailabilityData();
    let weatherIcon = '01n'

    const {locationWindow, windowContent, setIsWindowOpen} = await initializeStationPanel();

    stationData.forEach(station => {
        const newMarker = new Marker(
            station.number, 
            station.name, 
            { lat: station.lat, lng: station.lng }, 
            map, 
            locationWindow, 
            windowContent, 
            setIsWindowOpen, 
            AdvancedMarkerElement, 
            availabilityData,
            weatherIcon
        );
        markers.push(newMarker);
    });

    setInterval(async () => {
        availabilityData = await getAvailabilityData();
        markers.forEach(marker => marker.updateMarkerData(availabilityData));
    }, 60000);

    weatherIcon = await getWeatherIcon();
    // Initial Trigger for WeatherData | Forcing a rate limit to the Weather API otherwise it spams the API for data on each marker
    markers.forEach(async (marker, index) => {
        setTimeout(() => {
            marker.updateWeatherData(weatherIcon);
        }, index * 100);
    });

    setInterval(async () => {
        weatherIcon = await getWeatherIcon();

        markers.forEach((marker, index) => {
            setTimeout(() => {
                marker.updateWeatherData(weatherIcon);
            }, index * 50);
        });
    }, 900000);
}

main()