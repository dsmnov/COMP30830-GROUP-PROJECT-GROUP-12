export async function getRouteData() {
    let availData;

    try {
      const availResponse = await fetch('/api/routes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          origin: { lat: 53.349562, lng: -6.278198 },
          destination: { lat: 53.336597, lng: -6.248109 }
        })
      });

      availData = await availResponse.json();
      console.log('Route Data aquired:', availData);
    } catch (error) {
      console.error('Route Data failed:', error);
    }

    const encodedPolylineString = availData.routes[0].polyline.encodedPolyline
    const decodedPath = google.maps.geometry.encoding.decodePath(encodedPolylineString);

    const routePolyline = new google.maps.Polyline({
        path: decodedPath,
        strokeColor: "#FF0000",
        strokeWeight: 4,
    });
      
    routePolyline.setMap(map);      
}
