'use strict';

let currentInfoWindow = null;

async function initMap() {
    let coords = { lat: 41.6357653112787, lng: -88.5356838 }; //default coordinates

    const queryParams = new URLSearchParams(window.location.search);
    const latParam = queryParams.get('lat');
    const lngParam = queryParams.get('lng');

    if (latParam !== null && lngParam !== null) {
        const lat = parseFloat(latParam);
        const lng = parseFloat(lngParam);

        if (!isNaN(lat) && !isNaN(lng)) {
            coords = { lat: lat, lng: lng };
        } else {
            console.error('Invalid lat or lng parameters');
        }
    }

    const basicMap = new google.maps.Map(document.querySelector('#map'), {
        center: coords,
        zoom: latParam !== null && lngParam !== null ? 15 : 3,
    });

    let markers = [];

    const locationsData = await fetch('/map-data').then(response => response.json());
    for (const location of locationsData) {
        const { marker, infoWindow } = await createMarker(location, basicMap);
        markers.push({ marker, infoWindow });
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const userLocation = { lat: position.coords.latitude, lng: position.coords.longitude };
                await updateStructureList(markers, userLocation, 80.4672, basicMap);

                new google.maps.Marker({
                    position: userLocation,
                    map: basicMap,
                    icon: {
                        url: '/static/img/current-location.svg',
                        scaledSize: new google.maps.Size(30, 30)
                    },
                    title: 'Your Location'
                });
            },
            (error) => {
                console.error('Geolocation error:', error);
            }
        );
    } else {
        console.error('Geolocation is not supported by this browser.');
    }
}

async function createMarker(location, map) {
    console.log(location);

    const address = await reverseGeocode({ lat: location.lat, lng: location.lng });
    const infoWindowContent = `
        <div id='content'>
            <img src="${location.img_path}" alt="thumbnail" style="width:100%; height:auto;">
            <h5>${location.structure_name}</h5>
            <p>${address}</p>
        </div>`;

    const marker = new google.maps.Marker({
        title: location.structure_name,
        position: { lat: location.lat, lng: location.lng },
        map: map,
        icon: {
            url: '/static/img/marker.svg',
            scaledSize: new google.maps.Size(30, 30),
        },
    });

    const infoWindow = new google.maps.InfoWindow({
        content: infoWindowContent,
        maxWidth: 200
    });

    marker.addListener('click', () => {
        if (currentInfoWindow) {
            currentInfoWindow.close();
        }
        currentInfoWindow = infoWindow;
        infoWindow.open(map, marker);
    });

    return { marker, infoWindow };
}

async function reverseGeocode(latlng) {
    const geocoder = new google.maps.Geocoder();
    try {
        const response = await geocoder.geocode({ location: latlng });
        if (response.results[0]) {
            return response.results[0].formatted_address;
        } else {
            return 'No address found';
        }
    } catch (error) {
        console.error('Geocoder failed due to: ' + error);
        return 'Address unavailable';
    }
}

async function updateStructureList(markers, userLocation, radius, basicMap) {
    const listElement = document.getElementById('structuresList');
    listElement.innerHTML = '';

    for (const item of markers) {
        const distance = getDistanceFromLatLonInMiles(userLocation, item.marker.getPosition().toJSON());
        if (distance <= radius) {
            const address = await reverseGeocode(item.marker.getPosition());

            const listItem = document.createElement('li');
            listItem.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-start');

            const headingContainer = document.createElement('div');
            headingContainer.classList.add('ms-2', 'me-auto');

            const mainHeading = document.createElement('div');
            mainHeading.classList.add('fw-bold');
            mainHeading.textContent = item.marker.title;
            headingContainer.appendChild(mainHeading);

            const subHeading = document.createElement('div');
            subHeading.textContent = address;
            headingContainer.appendChild(subHeading);

            listItem.appendChild(headingContainer);

            const badge = document.createElement('span');
            badge.classList.add('badge', 'rounded-pill');
            badge.textContent = distance.toFixed(2) + ' miles';
            listItem.appendChild(badge);

            listElement.appendChild(listItem);

            listItem.addEventListener('click', () => {
                document.querySelectorAll('.list-group-item').forEach(e => {
                    e.classList.remove('active-list-group-item');
                });

                listItem.classList.add('active-list-group-item');

                basicMap.setCenter(item.marker.getPosition());
                basicMap.setZoom(15);

                if (currentInfoWindow) {
                    currentInfoWindow.close();
                }

                item.infoWindow.open(basicMap, item.marker);
                currentInfoWindow = item.infoWindow;
            });
        }
    }
}

function getDistanceFromLatLonInMiles(center, point) {
    const earthRadiusMiles = 3958.8;
    const dLat = deg2rad(point.lat - center.lat);
    const dLng = deg2rad(point.lng - center.lng);
    const a = Math.sin(dLat / 2) * Math.sin(dLng / 2) +
        Math.cos(deg2rad(center.lat)) * Math.cos(deg2rad(point.lat)) *
        Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return earthRadiusMiles * c;
}

function deg2rad(deg) {
    return deg * (Math.PI / 180);
}