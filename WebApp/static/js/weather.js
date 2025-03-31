export async function getWeatherData(latitude, longitude) {
    const currentTime = new Date();
    const rawTimeQuery = currentTime.toISOString();

    const slicedTimeQuery = rawTimeQuery.slice(0,13);
    const timeQuery = slicedTimeQuery + ':00:00Z';
    
    console.log('Time query:', timeQuery)
    try {
        const weatherResponse = await fetch('/api/weather', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                lat: latitude,
                lng: longitude,
                time: timeQuery
            })
        })

        const weatherResponseText = await weatherResponse.text();

        const parser = new DOMParser();
        const weatherData = parser.parseFromString(weatherResponseText, 'application/xml');

        /* TESTING FOR WEATHER DATA */
        console.log(weatherData);
        
        const weatherDataBody = weatherData.querySelector('weatherdata product time location');
        const temperatureDOM = weatherDataBody.querySelector('temperature');
        const humidityDOM = weatherDataBody.querySelector('humidity');

        const temperature = temperatureDOM.getAttribute('value');
        const humidity = humidityDOM.getAttribute('value');

        console.log(temperature);
        console.log(humidity);

        const weatherReport = { temperature, humidity }

        return weatherReport
    } catch (error) {
        console.error('Weather Data failed:', error);
    }
}
