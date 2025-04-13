let tripRoutePolyline = null;

export async function drawTripRoute(origin, destination, map) {
  if (tripRoutePolyline) {
    tripRoutePolyline.setMap(null); // Remove previous
  }

  try {
    const response = await fetch("/api/routes", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ origin, destination })
    });

    const data = await response.json();
    const encodedPolyline = data.routes[0].polyline.encodedPolyline;
    const decodedPath = google.maps.geometry.encoding.decodePath(encodedPolyline);

    tripRoutePolyline = new google.maps.Polyline({
      path: decodedPath,
      strokeColor: "#ff3333",
      strokeWeight: 4
    });

    tripRoutePolyline.setMap(map);
  } catch (error) {
    console.error("Error drawing trip route:", error);
  }
}
