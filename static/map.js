var map, heatmapData, heatmap;

function initMap() {

  heatmapData = [];

  $.get('/reports.json', function (reports) {
    var lat, lng, time, abs_temp;

    for (var key in reports) {
      report = reports[key];

      // Add coordinate to heatmapData
      heatmapData.push({location: new google.maps.LatLng(report['lat'], report['lng']), weight: report['abs_temp']});
    }
  });

  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 38.5, lng: -96},
    zoom: 4,
    mapTypeId: 'terrain',
    mapTypeControl: false,
    zoomControl: false,
    scaleControl: false,
    // styles: mapStyle
  });


  heatmap = new google.maps.visualization.HeatmapLayer({
    data: heatmapData,
    maxIntensity: 20
  });
  heatmap.setMap(map);

  // var mapStyle = [{
  //       'featureType': 'all',
  //       'elementType': 'all',
  //       'stylers': [{'visibility': 'off'}]
  //     }, {
  //       'featureType': 'landscape',
  //       'elementType': 'geometry',
  //       'stylers': [{'visibility': 'on'}, {'color': '#fcfcfc'}]
  //     }, {
  //       'featureType': 'water',
  //       'elementType': 'labels',
  //       'stylers': [{'visibility': 'off'}]
  //     }, {
  //       'featureType': 'water',
  //       'elementType': 'geometry',
  //       'stylers': [{'visibility': 'on'}, {'hue': '#5f94ff'}, {'lightness': 60}]
  //     }
  // ];
}

    
    // map.data.loadGeoJson(
    // 'https://storage.googleapis.com/mapsdevsite/json/google.json');
    // }