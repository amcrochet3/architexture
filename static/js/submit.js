'use strict';

let mapInitialized = false;
let selectedLocation = null;

document.addEventListener('change', function (event) {
    if (event.target.matches('.file-input')) {
        const filesCount = event.target.files.length;
        const textbox = event.target.previousElementSibling;

        if (filesCount === 1) {
            const fileName = event.target.value.split('\\').pop();
            textbox.textContent = fileName;
            processFile(event.target.files[0]);
        } else {
            textbox.textContent = filesCount + ' files selected';
        }
    }
});

function processFile(file) {
    if (file) {
        EXIF.getData(file, function () {
            const latArray = EXIF.getTag(this, "GPSLatitude");
            const lonArray = EXIF.getTag(this, "GPSLongitude");
            const latRef = EXIF.getTag(this, "GPSLatitudeRef");
            const lonRef = EXIF.getTag(this, "GPSLongitudeRef");

            if (latArray && lonArray && latRef && lonRef) {
                const lat = convertToDecimal(latArray, latRef);
                const lon = convertToDecimal(lonArray, lonRef);

                document.getElementById('user-lat').value = lat;
                document.getElementById('user-lng').value = lon;

                reverseGeocode(lat, lon);
            } else {
                showMapModal();
            }
        });
    }
}

function convertToDecimal(coordArray, ref) {
    const decimal = coordArray[0] + coordArray[1] / 60 + coordArray[2] / 3600;
    return ref === "S" || ref === "W" ? -decimal : decimal;
}

function initMap(location) {
    const map = new google.maps.Map(document.getElementById('map'), {
        center: location,
        zoom: 8
    });

    google.maps.event.addListener(map, 'click', function (event) {
        placeMarker(map, event.latLng);
    });
}

function placeMarker(map, location) {
    if (selectedLocation != null) {
        selectedLocation.setMap(null);
    }

    selectedLocation = new google.maps.Marker({
        position: location,
        map: map
    });

    document.getElementById('user-lat').value = location.lat(); //hidden lat field
    document.getElementById('user-lng').value = location.lng(); //hidden lng field
}

function showMapModal() {
    const modal = document.getElementById('mapModal');
    if (modal) {
        modal.style.display = 'block';
        modal.classList.add('show');

        const manualEnterButton = document.getElementById('manual-enter');
        if (manualEnterButton) {
            manualEnterButton.addEventListener('click', function () {
                modal.style.display = 'none';
            });
        }

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function (position) {
                const userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                initMap(userLocation);
            }, function () {
                console.error("Error getting the user's location");
                initMap({ lat: -34.397, lng: 150.644 }); //default coordinates
            });
        } else {
            console.error("Geolocation is not supported by this browser.");
            initMap({ lat: -34.397, lng: 150.644 }); //default coordinates
        }
    } else {
        console.error('Modal element not found');
    }
}

function reverseGeocode(lat, lon) {
    const geocoder = new google.maps.Geocoder();
    const latLng = new google.maps.LatLng(lat, lon);

    geocoder.geocode({ 'location': latLng }, function (results, status) {
        if (status === google.maps.GeocoderStatus.OK) {
            if (results[0]) {
                const addressComponents = results[0].address_components;
                addressComponents.forEach(function (component) {
                    const types = component.types;

                    if (types.includes('street_number') || types.includes('route')) {
                        const addressElement = document.getElementById('user-address');
                        if (addressElement) {
                            addressElement.value = ((addressElement.value || '') + ' ' + component.long_name).trim();
                        }
                    } else if (types.includes('locality')) {
                        const cityElement = document.getElementById('user-city');
                        if (cityElement) {
                            cityElement.value = component.long_name;
                        }
                    } else if (types.includes('administrative_area_level_1')) {
                        const stateElement = document.getElementById('user-state');
                        if (stateElement) {
                            stateElement.value = component.short_name;
                        }
                    } else if (types.includes('country')) {
                        const countryElement = document.getElementById('user-country');
                        if (countryElement) {
                            countryElement.value = component.long_name;
                        }
                    }
                });
            } else {
                console.error('No results found');
            }
        } else {
            console.error('Geocoder failed due to: ' + status);
        }
    });
}

document.getElementById('structure-submission').addEventListener('submit', function (event) {
    event.preventDefault();
    submitForm();
});

function submitForm() {
    const formData = new FormData(document.getElementById('structure-submission'));

    fetch('/submit/' + userId, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Submission successful!');

                const form = document.getElementById('structure-submission');
                form.reset();

                const fileInput = document.querySelector('.file-input');
                if (fileInput) {
                    fileInput.value = '';
                }

                window.location.reload();
            } else {
                alert('Submission failed: ' + data.error);
            }
        })
        .catch(error => {
            alert('An error occurred: ' + error.message);
        });
}
