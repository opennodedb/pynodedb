var map;
var pins;
var url = new URL(window.location);
var params = url.searchParams;


function initMap()
{
    showDefaultMap();
}

function drawMap(centre)
{
    var startingZoom = 11;

    if (params.get('node_id')) {
        startingZoom = 14;
    }

    map = new google.maps.Map(
        document.getElementById('map'), {
            zoom: startingZoom,
            center: centre,
            mapTypeControlOptions: {
                position: google.maps.ControlPosition.LEFT_TOP
            },
        }
    );

    // Handle map resize
    google.maps.event.addListener(map, 'zoom_changed', function(){
        handleZoom(map);
    });

    // Insert spacer controls to push default controls down
    var spacerDiv = document.createElement('div');
    spacerDiv.style.display = 'block';
    spacerDiv.style.height = '50px';
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(spacerDiv);
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(spacerDiv);

    // Draw Node Pins
    drawNodes(map);
    drawLinks(map);
}

function showDefaultMap()
{
    var url = new URL(window.location);
    var params = url.searchParams;
    var geocoder;
    var centre = new google.maps.LatLng(0, 0);

    // Get location of node in query string
    if(params.get('node_id')) {
        node_id = params.get('node_id');

        // Get requested node data
        $.post(
            '/api/node',
            {
                'node_id': node_id
            },
            function(response){
                if(response.status == 'OK'){
                    node = response.data.node;
                    centre = new google.maps.LatLng(node.lat, node.lng);
                }
                drawMap(centre);
            },
            'json'
        );
    }
    // Else return default location as defined in config
    else{
        geocoder = new google.maps.Geocoder();
        geocoder.geocode({ 'address': jsdata.defaultCentre }, function (results, status) {
            if (status == 'OK') {
                centre = results[0].geometry.location;
            }
            drawMap(centre);
        });
    }
}

// Draw Node Pins
function drawNodes(map)
{
    pins = [];

    // Get nodes via API
    $.post(
        '/api/nodes/all',
        function (response) {
            if (response.status == 'OK') {
                var nodes = response.data.nodes;

                $.each(nodes, function(i, node) {
                    if ((node.status_id > 1 && node.status_id < 6) || node.id == params.get('node_id')) {
                        // If this node is defined in address bar make it stand out
                        var color = null;
                        var opacity = null;
                        if (node.id == params.get('node_id')) {
                            color = 'yellow';
                            opacity = 1;
                        };

                        var markerIcon = getMarkerIconByStatus(node.status_id, 96, node.has_ap, color, opacity);
                        var pinLatLng = new google.maps.LatLng(node.lat, node.lng);

                        var label = new MapLabel({
                            text: node.name,
                            position: pinLatLng,
                            map: map,
                            fontSize: 12,
                            align: 'center',
                        });

                        var marker = new google.maps.Marker({
                            position: pinLatLng,
                            map: map,
                            title: node.name,
                            icon: {
                                url: markerIcon['path'],
                                scaledSize: {
                                    width: 32,
                                    height: 32,
                                },
                            },
                            opacity: markerIcon['opacity'],
                        });

                        // On click, go to Node page
                        marker.addListener('click', function() {
                            window.location.href = '/nodes/view/' + node.id;
                        });

                        pins.push({
                            marker: marker,
                            label: label,
                            node: node,
                        });
                    }
                });

                handleZoom(map);
            }
        },
        'json'
    );
}

// Draw link lines
function drawLinks(map)
{
    $.post(
        '/api/links/all',
        function (response) {
            if (response.status == 'OK') {
                links = response.data.links;

                $.each(links, function (i, link) {
                    var node_a = link.nodes[0];
                    var node_b = link.nodes[1];

                    if(node_a.status_id > 1 && node_a.status_id < 6 && node_b.status_id > 1 && node_b.status_id < 6){
                        // Determine line colour
                        // Default to grey
                        lineColor = 'grey';
                        lineOpacity = 0.5;
                        lineWeight = 1;

                        // If both nodes active, line will be blue or green
                        if (node_a.status_id == 4 && node_b.status_id == 4) {
                            // Operational Backbones are Blue
                            if (link.type == 'BB') {
                                lineColor = 'blue';
                                lineOpacity = 0.8;
                                lineWeight = 2;
                            }
                            // Operational Client links are Green
                            if (link.type == 'CL') {
                                lineColor = '#0f0';
                                lineOpacity = 0.8;
                                lineWeight = 2;
                            }
                        }

                        // If one node is operational and the other is offline or faulted, use red
                        if ((node_a.status_id == 4 && node_b.status_id > 4) || (node_a.status_id > 4 && node_b.status_id == 4)) {
                            lineColor = 'red';
                        }

                        var line = new google.maps.Polyline({
                            map: map,
                            path: [
                                {lat: node_a.lat, lng: node_a.lng},
                                {lat: node_b.lat, lng: node_b.lng}
                            ],
                            geodesic: true,
                            strokeColor: lineColor,
                            strokeOpacity: lineOpacity,
                            strokeWeight: lineWeight
                        });
                    }
                });
            }
        }
    );
}

// Handle map zoom event
function handleZoom(map) {
    var pixelSizeAtZoom0 = 1/2;
    var minPixelSize = 16;
    var maxPixelSize = 64;
    var zoom = map.getZoom();
    var relativePixelSize = Math.round(pixelSizeAtZoom0 * Math.pow(2, (zoom/2)));

    if (relativePixelSize < minPixelSize) {
        relativePixelSize = minPixelSize;
    }
    if (relativePixelSize > maxPixelSize) {
        relativePixelSize = maxPixelSize;
    }

    $.each(pins, function (i, pin) {
        pin.marker.setIcon({
            url: pin.marker.getIcon().url,
            scaledSize: {
                width: relativePixelSize,
                height: relativePixelSize,
            },
        });

        // Conditionally show and hide marker labels
        if (zoom >= 12 && pin.node.status_id == 4) {
            pin.label.set('map', map);
        }
        else if (zoom >= 14) {
            pin.label.set('map', map);
        }
        else {
            pin.label.set('map', null);
        }
    });    
}
