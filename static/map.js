// declare variables outside of functions to be able to access them in console
// or can use debugger; to have access where it stops the code
var map, heatmapData, heatmap;

function changeMap(evt) {

  // map needs to reset to not have displays stacked
  heatmap.setMap(null);
  heatmapData = [];
  var timeIndex = $('#mapview').val();

  $.get('reports.json', {'time_index': timeIndex}, function (reports) {

    console.log(timeIndex);
    console.log(reports);

    for (var key in reports) {
      report = reports[key];

      // Add coordinate to heatmapData
      heatmapData.push({location: new google.maps.LatLng(report['lat'], report['lng']), weight: report['abs_temp']});
    }

    heatmap = new google.maps.visualization.HeatmapLayer({
      data: heatmapData,
      maxIntensity: 80,
      radius: 30,
      gradient: [
        'rgba(0, 255, 255, 0)',
        'rgba(0, 255, 255, 1)',
        'rgba(0, 191, 255, 1)',
        'rgba(0, 127, 255, 1)',
        'rgba(0, 63, 255, 1)',
        'rgba(0, 0, 255, 1)',
        'rgba(0, 0, 223, 1)',
        'rgba(0, 0, 191, 1)',
        'rgba(0, 0, 159, 1)',
        'rgba(0, 0, 127, 1)',
        'rgba(63, 0, 91, 1)',
        'rgba(127, 0, 63, 1)',
        'rgba(191, 0, 31, 1)',
        'rgba(255, 0, 0, 1)'
      ],
    });
    heatmap.setMap(map);
  });
}

function initMap() {

  heatmapData = [];

  var timeIndex = $('#mapview').val();
  console.log(timeIndex);

  $.get('/reports.json', {'time_index': timeIndex}, function (reports) {

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

  var mapStyle = [{
        'featureType': 'all',
        'elementType': 'all',
        'stylers': [{'visibility': 'off'}]
      }, {
        'featureType': 'landscape',
        'elementType': 'geometry',
        'stylers': [{'visibility': 'on'}, {'color': '#fcfcfc'}]
      }, {
        'featureType': 'water',
        'elementType': 'labels',
        'stylers': [{'visibility': 'off'}]
      }, {
        'featureType': 'water',
        'elementType': 'geometry',
        'stylers': [{'visibility': 'on'}, {'hue': '#5f94ff'}, {'lightness': 60}]
      }
  ];
}

$('#selectmap').on('click', changeMap);


    // map.data.loadGeoJson(
    // 'https://storage.googleapis.com/mapsdevsite/json/google.json');
    // }