/* Class based structuring taken from this documentation https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes */
import { getRouteData } from './routes.js';

export class Marker {
    constructor(id, name, position, map, locationWindow, windowContent, setIsWindowOpen, AdvancedMarkerElement, availabilityData) {
        this.id = id;
        this.name = name;
        this.position = position;
        this.map = map;
        this.locationWindow = locationWindow;
        this.windowContent = windowContent;
        this.setIsWindowOpen = setIsWindowOpen;
        this.availableBikes = null;
        this.availableParking = null;
        this.marker = null;
        this.addMarker(AdvancedMarkerElement, availabilityData);
    }

    async addMarker(AdvancedMarkerElement, availabilityData) {
        const marker = new AdvancedMarkerElement({
            map: this.map,
            position: this.position,
            content: this._getDefaultMarkerIcon(),
            title: this.name,
        });
        this.marker = marker;
        this.updateMarkerData(availabilityData);
        this._addInfoWindow(this.map);
        this._addStationPanel()
        this._addResponsiveClick();
    }

    _addInfoWindow(map) {
        const infoWindow = new google.maps.InfoWindow();

        this.marker.addEventListener('mouseover', async () => {
            map.setOptions({ draggableCursor: 'pointer' });

            this.marker.content.style.transition = "transform 0.1s ease";
            this.marker.content.style.transform = "scale(1.15)";
            
            const infoWindowContentString = `
                <div id='content'>
                    <h1>${this.name}</h1>
                        <ul>
                            <li>Available Bikes:${this.availableBikes}</li>
                            <li>Parking Stations:${this.availableParking}</li>
                        </ul>
                </div>`;

            infoWindow.setContent(infoWindowContentString);
            infoWindow.open({
              anchor: this.marker,
              map: map
            });
        });

        this.marker.addEventListener('mouseout', () => {
            map.setOptions({ draggableCursor: 'grab' });

            this.marker.content.style.transition = "transform 0.1s ease";
            this.marker.content.style.transform = "scale(1)";
            
            infoWindow.close();
        });
    }

    _addResponsiveClick() {
        this.marker.addEventListener('mousedown', () => {
            this.marker.content.style.transition = "transform 0.1s ease";
            this.marker.content.style.transform = "scale(0.85)";
        });
    
        this.marker.addEventListener('mouseup', () => {
            this.marker.content.style.transition = "transform 0.1s ease";
            this.marker.content.style.transform = "scale(1.15)";
        });
    }

    _getDefaultMarkerIcon(svgColor) {
        const markerIcon = new DOMParser().parseFromString(
            `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 38 38" width="38" height="38">
                <path id="background" d="M19,1 C12,1 7,6 7,13 C7,22 19,37 19,37 C19,37 31,22 31,13 C31,6 26,1 19,1 Z" fill="${(typeof svgColor !== 'undefined' && svgColor) || 'white'}" stroke="black" stroke-width="1"/>
                <g id="separateur-titre" transform="translate(8.7,9) scale(0.55)"><path d="M29.85,7.78a7.23,7.23,0,0,0,-2.29,0.38l-2,-6A2.73,2.73,0,0,0,22.93,0.32H21.22a1.05,1.05,0,0,0,0,2.1h1.71a0.66,0.66,0,0,1,0.61,0.44l0.29,0.88H15l-0.14,-0.43l0.47,-0.06a0.84,0.84,0,0,0,0.73,-0.82V2.35a1.16,1.16,0,0,0,-1,-1.17L12.11,0.9a1.18,1.18,0,0,0,-1.28,1.31l0.1,0.85a0.73,0.73,0,0,0,0.27,0.49a0.75,0.75,0,0,0,0.54,0.15l1,-0.13l0.32,1L10.81,8.32a6.92,6.92,0,0,0,-2.7,-0.54a7.11,7.11,0,1,0,7,8.16h3a1.08,1.08,0,0,0,0.81,-0.37L25.3,8l0.38,1.1a7.1,7.1,0,1,0,4.17,-1.36ZM13.93,7.19l2.2,6.65h-1a7.11,7.11,0,0,0,-2.51,-4.45Zm-2.41,4A5,5,0,0,1,13,13.84H10ZM8.11,19.9a5,5,0,0,1,0,-10a5.08,5.08,0,0,1,1.61,0.27l-2.51,4.2a1.05,1.05,0,0,0,0.9,1.59H13A5,5,0,0,1,8.11,19.9Zm10,-6.65L15.7,5.84h8.71Zm11.7,6.65a5,5,0,0,1,-3.45,-8.64a12.08,12.08,0,0,0,2.69,4.36a1.07,1.07,0,0,0,0.76,0.32a1.05,1.05,0,0,0,0.75,-1.78a9.8,9.8,0,0,1,-2.23,-3.64l-0.13,-0.37a5,5,0,1,1,1.61,9.75Z"/></g>
            </svg>`,
            'image/svg+xml'
        ).documentElement;
    
        return markerIcon
    }

    _updateMarkerIcon() {
        const occupancy = this.availableBikes / (this.availableBikes + this.availableParking);
        let hue;
        let svgColor;

        if (occupancy >= 0.80) {
            hue = occupancy * 220;
        } else if (occupancy <= 0.15) {
            hue = occupancy * 90;
        } else {
            hue = occupancy * 160;
        }

        if (isNaN(occupancy)) {
            svgColor = `hsl(0, 100%, 100%)`;
        }
        else {
            svgColor = `hsl(${hue}, 80%, 70%)`;
        }
        
        const pinSvg = this._getDefaultMarkerIcon(svgColor);
        this.marker.content = pinSvg.cloneNode(true);
    }

    async updateMarkerData(availabilityData) {
        const liveData = availabilityData.find(station => station.number == this.id)
        this.availableBikes = liveData.available_bikes;
        this.availableParking = liveData.available_bike_stands;
        this._updateMarkerIcon()
        console.log('Marker Data Updated')
    }

    _addStationPanel() {
        const originMarker = this;

        this.marker.addEventListener('click', (e) => {
            windowContent.innerHTML = `
                <h2>${this.name}</h2>
                <p>Available Bikes: ${this.availableBikes}</p>
                <p>Available Bike Stands: ${this.availableParking}</p>    
                <h3>Plan a Journey</h3>
                    <label class = 'stationSearch'>
                        <input type = 'text' required id = 'stationInput' autocomplete = 'off' />
                        <span class = 'placeholder'>Select Destination</span>
                        <span id = 'errorMessage1'></span>
                        <span id = 'errorMessage2'></span>
                        <ul class = 'dropdown' id = 'stationDropdown'>
                    </label>`;
        
            this.locationWindow.style.display = 'block';
            this.setIsWindowOpen(true);
            e.stopPropagation();
        
            /* Searchable Select code taken from https://www.youtube.com/watch?v=lcXjEqGXv14&ab_channel=MazenSalah */
            const input = this.windowContent.querySelector('#stationInput');
            const dropdown = this.windowContent.querySelector('#stationDropdown');
        
            function createDropdown(originMarker, filterText = '') {
                dropdown.innerHTML = '';


                const filteredMarkers = markers.filter(m =>
                    m.name.toLowerCase().includes(filterText.toLowerCase())
                );

                if (!filteredMarkers.length) {
                    dropdown.style.display = 'none';
                    return;
                }


                filteredMarkers.forEach(station => {
                    const li = document.createElement('li');
                    li.textContent = station.name;
                    li.dataset.lat = station.position.lat;
                    li.dataset.lng = station.position.lng;
                    li.dataset.number = station.id;

                    li.addEventListener('mousedown', (e) => {
                        e.preventDefault();
                        e.stopPropagation();

                        input.value = station.name;
                        dropdown.style.display = 'none';

                        const destinationCoordinates = {
                            lat: parseFloat(li.dataset.lat),
                            lng: parseFloat(li.dataset.lng)
                        };

                        getRouteData(originMarker.position, destinationCoordinates, originMarker.map);

                        const destinationData = markers.find(m => m.id == parseInt(li.dataset.number));

                        if (destinationData.availableParking < 3) {
                            document.getElementById('errorMessage1').textContent = 'Warning: Destination has Low Parking Availability!';
                        }

                        if (originMarker.availableBikes < 3) {
                            document.getElementById('errorMessage2').textContent = 'Warning: Origin has Low Bike Availability!';
                        }
                    });

                    dropdown.appendChild(li);
                });

                dropdown.style.display = 'block';
            }
        
            input.addEventListener('focus', () => {
                createDropdown(originMarker, '');
            });
        
            input.addEventListener('input', () => {
                createDropdown(originMarker, input.value.toLowerCase());
            });
        
            document.addEventListener('click', (event) => {
                if (!document.querySelector('.stationSearch')?.contains(event.target)) {
                    dropdown.style.display = 'none';
                }
            });
        });
    }
}