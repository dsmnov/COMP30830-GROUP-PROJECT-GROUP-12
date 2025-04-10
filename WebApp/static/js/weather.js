// Weather data retrieval

// Retrieves weather based on the markers location that called it
export async function getWeatherData(latitude, longitude) {
    // Process time to compatible api method
    const currentTime = new Date();
    const rawTimeQuery = currentTime.toISOString();

    const slicedTimeQuery = rawTimeQuery.slice(0,13);
    const timeQuery = slicedTimeQuery + ':00:00Z';
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

        //Extracting data from XML which is a bit harder than json which is why it looks like this
        const parser = new DOMParser();
        const weatherData = parser.parseFromString(weatherResponseText, 'application/xml');
        
        const weatherDataBody = weatherData.querySelector('weatherdata product time location');
        const temperatureDOM = weatherDataBody.querySelector('temperature');
        const humidityDOM = weatherDataBody.querySelector('humidity');
        const windDirectionDOM = weatherDataBody.querySelector('windDirection')
        const windSpeedDOM = weatherDataBody.querySelector('windSpeed')

        const temperature = temperatureDOM.getAttribute('value');
        const humidity = humidityDOM.getAttribute('value');
        const windDirection = windDirectionDOM.getAttribute('name');
        const windSpeed = windSpeedDOM.getAttribute('name');

        const weatherReport = { temperature, humidity, windDirection, windSpeed }

        return weatherReport
    } catch (error) {
        console.error('Weather Data failed:', error);
    }
}

// Getting the weather icon
export async function getWeatherIcon() {
    const iconResponse = await fetch('/api/weather/icon', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    const iconString = iconResponse.text()
    return iconString
}