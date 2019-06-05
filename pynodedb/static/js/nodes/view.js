function initMap()
{
    var node_id = jsdata.node_id;
    var lat = jsdata.lat;
    var lng = jsdata.lng;

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
    url.searchParams.set('node_id', node_id);

    map.addListener('click', function () {
        window.location.href = url;
    });

    marker.addListener('click', function () {
        window.location.href = url;
    });
};

// Make table(s) sortable
$(function() {
    $('.table-sortable').DataTable({
        paging: false,
        info: false,
        searching: false,
    });
});
