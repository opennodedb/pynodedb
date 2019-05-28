var map;

function initMap()
{
    showDefaultMap();
}

function drawMap(centre)
{
    var url = new URL(window.location);
    var params = url.searchParams;
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
    var pinColor;

    // Get nodes via API
    $.post(
        '/api/nodes/all',
        function (response) {
            if (response.status == 'OK') {
                nodes = response.data.nodes;

                $.each(nodes, function(i, node) {
                    if (node.status_id > 1 && node.status_id < 6) {
                        switch(node.status_id) {
                            case 0:
                            case 5:
                                pinColor = 'black';
                                break;
                            case 1:
                                pinColor = 'grey';
                                break;
                            case 2:
                                pinColor = 'yellow';
                                break;
                            case 3:
                                pinColor = 'orange';
                                break;
                            case 4:
                                pinColor = '#0f0';
                                break;
                            case 4:
                                pinColor = 'red';
                                break;
                        }

                        var pinLatLng = new google.maps.LatLng(node.lat, node.lng);
                        var pin = new Marker({
                            position: pinLatLng,
                            map: map,
                            title: node.name,
                            icon: {
                                path: MAP_PIN,
                                fillColor: pinColor,
                                fillOpacity: 0.8,
                                strokeColor: 'black',
                                strokeWeight: 0.5,
                                scale: 0.5,
                            },
                        });
                    }
                });
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