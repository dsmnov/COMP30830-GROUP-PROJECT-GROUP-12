import { Marker } from './markers.js';

export let markers = [];

async function initMap() {
    const position = { lat: 53.3484, lng: -6.2539 };

    const { Map } = await google.maps.importLibrary('maps');
  
    return new Map(document.getElementById('map'), {
        zoom: 14,
        center: position,
        mapId: 'dbbikes_map',
    });
}

async function getStationData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/stations');
        return await response.json();
    } catch (error) {
        console.error('Error fetching station data:', error);
    }
}

async function getAvailabilityData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/availability');
        return await response.json();
    } catch (error) {
        console.error('Error fetching availability data:', error);
    }
}

async function initializeStationPanel() {
    const locationWindow = document.getElementById('locationWindow');
    const windowContent = document.getElementById('windowContent');
    let isWindowOpen = false;
  
    document.addEventListener('click', (event) => {
        if (isWindowOpen && !locationWindow.contains(event.target)) {
            locationWindow.style.display = 'none';
            isWindowOpen = false;
        }
    });
  
    return {locationWindow, windowContent, setIsWindowOpen(value) {isWindowOpen = value;}};
}

async function main() {
    const map = await initMap();
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    const stationData = await getStationData();
    let availabilityData = await getAvailabilityData();

    const {locationWindow, windowContent, setIsWindowOpen} = await initializeStationPanel();

    stationData.forEach(station => {
        const newMarker = new Marker(station.number, station.name, { lat: station.lat, lng: station.lng }, map, locationWindow, windowContent, setIsWindowOpen, AdvancedMarkerElement, availabilityData);
        markers.push(newMarker);
    });

    setInterval(async () => {
        availabilityData = await getAvailabilityData();
        markers.forEach(marker => marker.updateMarkerData(availabilityData));
    }, 60000);
}

main()