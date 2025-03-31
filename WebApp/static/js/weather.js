export async function getWeatherData(latitude, longitude) {
    const currentTime = new Date();
    const timeQuery = currentTime.toISOString();

    try {
        const weatherResponse = await fetch('/api/weather', {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                lat: latitude,
                lng: longitude
            })
        })
            .then()
                

        
    } catch (error) {
        console.error('Weather Data failed:', error);
    }
}
