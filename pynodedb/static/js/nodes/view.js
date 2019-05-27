function initMap()
{
    lat = parseFloat($('#node_lat').text());
    lng = parseFloat($('#node_lng').text());

    var pin = { lat: lat, lng: lng };
    var map = new google.maps.Map(
        document.getElementById('map'), { zoom: 13, center: pin });
    var marker = new google.maps.Marker({ position: pin, map: map });
};