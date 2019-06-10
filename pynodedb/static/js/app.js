// Make node icon path
function getMarkerIconByStatus(statusId, iconSize = 24, isAP = false) {
    var icon = {
        color: 'red',
        size: iconSize,
        opacity: 1,
    };

    switch (statusId) {
        case 0:
        case 5:
            icon['color'] = 'red';
            icon['opacity'] = 0.5;
            break;
        case 1:
            icon['color'] = 'white';
            icon['opacity'] = 0.8;
            break;
        case 2:
            icon['color'] = 'silver';
            icon['opacity'] = 0.8;
            break;
        case 3:
            icon['color'] = 'purple';
            icon['opacity'] = 0.8;
            break;
        case 4:
            icon['color'] = 'green';
            icon['opacity'] = 1;
            break;
        case 6:
            icon['color'] = 'red';
            icon['opacity'] = 0.8;
            break;
    }

    icon['path'] = `/static/vendor/small-n-flat/png/${icon['size']}/map-marker-${icon['color']}.png`;

    return icon;
}
