var map;

function initMap()
{
    showDefaultMap();
}

function drawMap(centre)
{
    map = new google.maps.Map(
        document.getElementById('map'), {
            zoom: 13,
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