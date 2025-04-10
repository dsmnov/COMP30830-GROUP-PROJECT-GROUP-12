// Rare global variable for the route to be set to allow for each station panel and planned journey to overwrite eachother, 
// only 1 journey will ever be displayed or worked with at a time so in this case global variable is fine
let routePolyline = null;

export async function getRouteData(origin, destination, map) {
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
