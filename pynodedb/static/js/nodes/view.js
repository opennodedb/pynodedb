function initMap()
{
    lat = parseFloat($('#node_lat').text());
    lng = parseFloat($('#node_lng').text());

    var pin = { lat: lat, lng: lng };
    var map = new google.maps.Map(
        document.getElementById('map'), {
            zoom: 13,
            center: pin,
            disableDefaultUI: true,
            zoomControl: true,
            mapTypeControl: true,
            mapTypeControlOptions: {
                style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
            },
            gestureHandling: 'none',
            draggableCursor: 'pointer',
        }
    );
    var marker = new google.maps.Marker({ position: pin, map: map });


    var url = new URL(window.location.href);
    url.pathname = '/map';
    url.searchParams.set('lat', lat);
    url.searchParams.set('lng', lng);

    map.addListener('click', function () {
        window.location.href = url;
    });

    marker.addListener('click', function () {
        window.location.href = url;
    });
};