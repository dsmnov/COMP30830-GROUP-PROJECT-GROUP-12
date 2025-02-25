let map;

async function initMap() {
  const position = { lat: 53.3484, lng: -6.2539 };

  const { Map } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

  map = new Map(document.getElementById("map"), {
    zoom: 14,
    center: position,
    mapId: "dbbikes_map",
  });

  fetch("http://127.0.0.1:5000/api/stations")
    .then(response => response.json())
    .then(data => {

      data.forEach(station => {
        const coordinates = { lat: station.lat, lng: station.lng };
        const title = station.name

        const marker = new AdvancedMarkerElement({
          map: map,
          position: coordinates,
          title: title,
        });

        const contentString = `
          <div id="content">
            <h1>${title}</h1>
            <ul>
              <li>Latitude: ${station.lat}</li>
              <li>Longitude: ${station.lng}</li>
            </ul>
          </div>`;

        const infoWindow = new google.maps.InfoWindow({
          content: contentString
        })

        marker.addEventListener("mouseover", () => {
          infoWindow.open({
              anchor: marker,
              map: map
          });
        });

        marker.addEventListener("mouseout", () => {
          infoWindow.close();
        });
      });

  })
  .catch(error => console.error("Error fetching data:", error));
}

initMap();