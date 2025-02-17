function initMap() {
    const mapDiv = document.getElementById("map");
    if (mapDiv) {
      const map = new google.maps.Map(mapDiv, {
        center: { lat: 53.3484, lng: -6.2539 },
        zoom: 14,
      });
    }
  }