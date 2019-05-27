function initMap()
{
    url = new URL(window.location.href);
    lat = parseFloat(url.searchParams.get('lat'));
    lng = parseFloat(url.searchParams.get('lng'));

    var pin = { lat: lat, lng: lng };
    var map = new google.maps.Map(
        document.getElementById('map'), {
            zoom: 13,
            center: pin,
        }
    );
    var marker = new google.maps.Marker({ position: pin, map: map });
};