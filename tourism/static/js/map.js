// Map functionality for Mathura Darshan

class MapManager {
    constructor(elementId) {
        this.map = null;
        this.elementId = elementId;
        this.markers = [];
        this.directionsService = null;
        this.directionsRenderer = null;
    }

    initialize(center = { lat: 27.5891, lng: 77.7064 }) {
        this.map = new google.maps.Map(document.getElementById(this.elementId), {
            zoom: 13,
            center: center,
            mapTypeControl: true,
            fullscreenControl: true,
            streetViewControl: true,
            zoomControl: true,
            mapTypeId: google.maps.MapTypeId.ROADMAP
        });

        this.directionsService = new google.maps.DirectionsService();
        this.directionsRenderer = new google.maps.DirectionsRenderer({
            map: this.map,
            suppressMarkers: false,
            polylineOptions: {
                strokeColor: '#007bff',
                strokeWeight: 4
            }
        });

        return this.map;
    }

    addMarker(lat, lng, title = 'Location', icon = null) {
        const marker = new google.maps.Marker({
            position: { lat, lng },
            map: this.map,
            title: title,
            icon: icon
        });

        this.markers.push(marker);
        return marker;
    }

    addUserMarker(lat, lng) {
        return this.addMarker(lat, lng, 'Your Location', 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png');
    }

    clearMarkers() {
        this.markers.forEach(marker => marker.setMap(null));
        this.markers = [];
    }

    fitBounds() {
        if (this.markers.length === 0) return;

        const bounds = new google.maps.LatLngBounds();
        this.markers.forEach(marker => bounds.extend(marker.getPosition()));
        this.map.fitBounds(bounds);
    }

    getRoute(origin, destination, travelMode = 'DRIVING') {
        return new Promise((resolve, reject) => {
            this.directionsService.route(
                {
                    origin: origin,
                    destination: destination,
                    travelMode: google.maps.TravelMode[travelMode]
                },
                (result, status) => {
                    if (status === google.maps.DirectionsStatus.OK) {
                        this.directionsRenderer.setDirections(result);
                        resolve(result);
                    } else {
                        reject(status);
                    }
                }
            );
        });
    }

    setCenter(lat, lng) {
        this.map.setCenter({ lat, lng });
    }

    setZoom(zoom) {
        this.map.setZoom(zoom);
    }
}

// Export
window.MapManager = MapManager;
