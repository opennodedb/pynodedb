var map;
var pins;
var lines;
var url = new URL(window.location);
var params = url.searchParams;

$('.cb-node').change(function() {
    handleNodeCheckboxes();
});

$('.cb-link').change(function() {
    handleLinkCheckboxes();
});

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
            styles: [
                {
                    featureType: 'poi',
                    stylers: [{ visibility: 'off' }]
                },
                {
                    featureType: 'transit',
                    stylers: [{ visibility: 'off' }]
                },
            ],
        }
    );

    // Handle map resize
    google.maps.event.addListener(map, 'zoom_changed', function(){
        handleZoom(map);
    });

    // Insert spacer controls to push default controls down
    var spacerDiv = $('<div>');
    var spacerElem = spacerDiv.get(0);
    spacerElem.style.display = 'block';
    spacerElem.style.height = '50px';
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(spacerElem);
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(spacerElem);

    // Insert spacer controls to push default controls down
    var nodeTypeDiv = $("div#node-types");
    var nodeTypeElem = nodeTypeDiv.get(0);
    map.controls[google.maps.ControlPosition.LEFT_BOTTOM].push(nodeTypeElem);

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
                        fontSize: 12,
                        align: 'center',
                    });

                    var marker = new google.maps.Marker({
                        position: pinLatLng,
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
                });

                handleZoom();
                handleNodeCheckboxes();
            }
        },
        'json'
    );
}

// Draw link lines
function drawLinks(map)
{
    lines = [];

    $.post(
        '/api/links/all',
        function (response) {
            if (response.status == 'OK') {
                links = response.data.links;

                $.each(links, function (i, link) {
                    var node_a = link.nodes[0];
                    var node_b = link.nodes[1];

                    // Determine line colour
                    // Default to grey
                    var lineColor = 'grey';
                    var lineOpacity = 0.5;
                    var lineWeight = 1;
                    var linkStatus = 'planned';

                    // If both nodes active, line will be blue or green
                    if (node_a.status_id == 4 && node_b.status_id == 4) {
                        // Operational Backbones are Blue
                        if (link.type == 'BB') {
                            lineColor = 'blue';
                            lineOpacity = 0.8;
                            lineWeight = 2;
                            linkStatus = 'ptp';
                        }
                        // Operational Client links are Green
                        if (link.type == 'CL') {
                            lineColor = '#0f0';
                            lineOpacity = 0.8;
                            lineWeight = 2;
                            linkStatus = 'ptmp';
                        }
                    }

                    // If one node is operational and the other is offline or faulted, use red
                    if ((node_a.status_id == 4 && node_b.status_id > 4) || (node_a.status_id > 4 && node_b.status_id == 4)) {
                        lineColor = 'red';
                        linkStatus = 'offline';
                    }

                    var line = {
                        polyline: new google.maps.Polyline({
                            path: [
                                {lat: node_a.lat, lng: node_a.lng},
                                {lat: node_b.lat, lng: node_b.lng}
                            ],
                            geodesic: true,
                            strokeColor: lineColor,
                            strokeOpacity: lineOpacity,
                            strokeWeight: lineWeight
                        }),
                        status: linkStatus,
                    }
                    lines.push(line);
                });

                handleLinkCheckboxes();
            }
        }
    );
}

// Handle map zoom event
function handleZoom() {
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

function handleNodeCheckboxes() {
    $.each($('.cb-node'), function(i, cb){
        var cbStatus = cb.id.substring(8);

        $.each(pins, function(j, pin){
            if (cbStatus == pin.node.status_id && !pin.node.has_ap) {
                if ($(cb).prop('checked')) {
                    pin.marker.setMap(map);
                }
                else {
                    pin.marker.setMap(null);
                }
            }
            else if (cbStatus == 'offline') {
                if (pin.node.status_id == 0 || pin.node.status_id == 5 || pin.node.status_id == 6) {
                    if ($(cb).prop('checked')) {
                        pin.marker.setMap(map);
                    }
                    else {
                        pin.marker.setMap(null);
                    }
                }
            }
            else if (pin.node.has_ap && pin.node.status_id == 4 && cbStatus == 'ap') {
                if ($(cb).prop('checked')) {
                    pin.marker.setMap(map);
                }
                else {
                    pin.marker.setMap(null);
                }
            }

            if (pin.node.id == params.get('node_id')) {
                pin.marker.setMap(map);
            }
        });
    });
}

function handleLinkCheckboxes() {
    $.each($('.cb-link'), function(i, cb) {
        var cbStatus = cb.id.substring(8);

        $.each(lines, function(j, line) {
            if (cbStatus == line.status) {
                if ($(cb).prop('checked')) {
                    line.polyline.setMap(map);
                }
                else {
                    line.polyline.setMap(null);
                }
            }
        });
    });
}
