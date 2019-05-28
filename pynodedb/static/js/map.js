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