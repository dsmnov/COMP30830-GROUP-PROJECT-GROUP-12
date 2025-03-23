let routePolyline = null;

export async function getRouteData(origin, destination) {
    let availData;

    if (routePolyline) {
      routePolyline.setMap(null);
    }
    
    try {
      const availResponse = await fetch('/api/routes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ origin, destination })
      });

      availData = await availResponse.json();
      console.log('Route Data aquired:', availData);
    } catch (error) {
      console.error('Route Data failed:', error);
    }

    const encodedPolylineString = availData.routes[0].polyline.encodedPolyline
    const decodedPath = google.maps.geometry.encoding.decodePath(encodedPolylineString);

    routePolyline = new google.maps.Polyline({
        path: decodedPath,
        strokeColor: "#FF0000",
        strokeWeight: 4,
    });
      
    routePolyline.setMap(map);      
}
