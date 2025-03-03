let map;
let markers = [];
let availData = [];

async function initMap() {
  const position = { lat: 53.3484, lng: -6.2539 };

  const { Map } = await google.maps.importLibrary("maps");
  
  map = new Map(document.getElementById("map"), {
    zoom: 14,
    center: position,
    mapId: "dbbikes_map",
  });

  await refreshAvailabilityData();
  initializeStations();
}

async function initializeStations() {
  try {
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    const response = await fetch("http://127.0.0.1:5000/api/stations");
    const data = await response.json();

    const parser = new DOMParser();
    const pinSvgString = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 38 38" width="38" height="38"><path id="background" d="M19,1 C12,1 7,6 7,13 C7,22 19,37 19,37 C19,37 31,22 31,13 C31,6 26,1 19,1 Z" fill="white" stroke="black" stroke-width="1"/><g id="separateur-titre" transform="translate(8.7,9) scale(0.55)"><path d="M29.85,7.78a7.23,7.23,0,0,0,-2.29,0.38l-2,-6A2.73,2.73,0,0,0,22.93,0.32H21.22a1.05,1.05,0,0,0,0,2.1h1.71a0.66,0.66,0,0,1,0.61,0.44l0.29,0.88H15l-0.14,-0.43l0.47,-0.06a0.84,0.84,0,0,0,0.73,-0.82V2.35a1.16,1.16,0,0,0,-1,-1.17L12.11,0.9a1.18,1.18,0,0,0,-1.28,1.31l0.1,0.85a0.73,0.73,0,0,0,0.27,0.49a0.75,0.75,0,0,0,0.54,0.15l1,-0.13l0.32,1L10.81,8.32a6.92,6.92,0,0,0,-2.7,-0.54a7.11,7.11,0,1,0,7,8.16h3a1.08,1.08,0,0,0,0.81,-0.37L25.3,8l0.38,1.1a7.1,7.1,0,1,0,4.17,-1.36ZM13.93,7.19l2.2,6.65h-1a7.11,7.11,0,0,0,-2.51,-4.45Zm-2.41,4A5,5,0,0,1,13,13.84H10ZM8.11,19.9a5,5,0,0,1,0,-10a5.08,5.08,0,0,1,1.61,0.27l-2.51,4.2a1.05,1.05,0,0,0,0.9,1.59H13A5,5,0,0,1,8.11,19.9Zm10,-6.65L15.7,5.84h8.71Zm11.7,6.65a5,5,0,0,1,-3.45,-8.64a12.08,12.08,0,0,0,2.69,4.36a1.07,1.07,0,0,0,0.76,0.32a1.05,1.05,0,0,0,0.75,-1.78a9.8,9.8,0,0,1,-2.23,-3.64l-0.13,-0.37a5,5,0,1,1,1.61,9.75Z"/></g></svg>`;
    const pinSvgDoc = parser.parseFromString(pinSvgString, "image/svg+xml");
    const pinSvg = document.importNode(pinSvgDoc.documentElement, true);

    data.forEach(station => {
      const coordinates = { lat: station.lat, lng: station.lng };
      const title = station.name;

      const marker = new AdvancedMarkerElement({
        map: map,
        position: coordinates,
        content: pinSvg.cloneNode(true),
        title: title,
      });

      marker.stationId = station.number;

      function createInfoWindowContent(title, availableBikes, parkingStations) {
        return `
          <div id="content">
            <h1>${title}</h1>
            <ul>
              <li>Available Bikes: ${availableBikes}</li>
              <li>Parking Stations: ${parkingStations}</li>
            </ul>
          </div>`;
      }

      const infoWindow = new google.maps.InfoWindow();

      marker.addEventListener("mouseover", async () => {
        const stationData = availData.find(data => data.number === marker.stationId);
        const availableBikes = stationData.available_bikes;
        const parkingStations = stationData.available_bike_stands;
        
        infoWindow.setContent(createInfoWindowContent(title, availableBikes, parkingStations));
        infoWindow.open({
          anchor: marker,
          map: map
        });
      });

      marker.addEventListener("mouseout", () => {
          infoWindow.close();
      });

      markers.push(marker);
    });
    updateMarkersIcons()
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

async function refreshAvailabilityData() {
  try {
    const availResponse = await fetch("http://127.0.0.1:5000/api/availability");
    availData = await availResponse.json();
    console.log("Availability data updated:", availData);
    updateMarkersIcons()
  } catch (error) {
    console.error("Error fetching availability data:", error);
  }
}

async function updateMarkersIcons() {
  const parser = new DOMParser();
  markers.forEach(marker => {
    const stationData = availData.find(data => data.number === marker.stationId);
    const occupancy = stationData.available_bikes / stationData.bikestands;

    const hue = occupancy * 162;
    const saturation = 70;
    const lightness = 60;
    const svgColor = `hsl(${hue}, ${saturation}%, ${lightness}%)`;

    const pinSvgString = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 38 38" width="38" height="38"><path id="background" d="M19,1 C12,1 7,6 7,13 C7,22 19,37 19,37 C19,37 31,22 31,13 C31,6 26,1 19,1 Z" fill="${svgColor}" stroke="black" stroke-width="1"/><g id="separateur-titre" transform="translate(8.7,9) scale(0.55)"><path d="M29.85,7.78a7.23,7.23,0,0,0,-2.29,0.38l-2,-6A2.73,2.73,0,0,0,22.93,0.32H21.22a1.05,1.05,0,0,0,0,2.1h1.71a0.66,0.66,0,0,1,0.61,0.44l0.29,0.88H15l-0.14,-0.43l0.47,-0.06a0.84,0.84,0,0,0,0.73,-0.82V2.35a1.16,1.16,0,0,0,-1,-1.17L12.11,0.9a1.18,1.18,0,0,0,-1.28,1.31l0.1,0.85a0.73,0.73,0,0,0,0.27,0.49a0.75,0.75,0,0,0,0.54,0.15l1,-0.13l0.32,1L10.81,8.32a6.92,6.92,0,0,0,-2.7,-0.54a7.11,7.11,0,1,0,7,8.16h3a1.08,1.08,0,0,0,0.81,-0.37L25.3,8l0.38,1.1a7.1,7.1,0,1,0,4.17,-1.36ZM13.93,7.19l2.2,6.65h-1a7.11,7.11,0,0,0,-2.51,-4.45Zm-2.41,4A5,5,0,0,1,13,13.84H10ZM8.11,19.9a5,5,0,0,1,0,-10a5.08,5.08,0,0,1,1.61,0.27l-2.51,4.2a1.05,1.05,0,0,0,0.9,1.59H13A5,5,0,0,1,8.11,19.9Zm10,-6.65L15.7,5.84h8.71Zm11.7,6.65a5,5,0,0,1,-3.45,-8.64a12.08,12.08,0,0,0,2.69,4.36a1.07,1.07,0,0,0,0.76,0.32a1.05,1.05,0,0,0,0.75,-1.78a9.8,9.8,0,0,1,-2.23,-3.64l-0.13,-0.37a5,5,0,1,1,1.61,9.75Z"/></g></svg>`;

    const pinSvgDoc = parser.parseFromString(pinSvgString, "image/svg+xml");
    const pinSvg = document.importNode(pinSvgDoc.documentElement, true);

    marker.content = pinSvg.cloneNode(true);
    console.log("Marker Icons updated")
  });
}

async function startApp() {
  initMap();
  setInterval(refreshAvailabilityData, 60000);
}

startApp();