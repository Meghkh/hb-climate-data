// declare variables outside of functions to be able to access them in console
// or can use debugger; to have access where it stops the code
var map, heatmapData, heatmap;
var mvcObj;
var MIN_TEMP = -67;

function changeMap(evt) {

  //can out the rerender as part of the function, ensure that rerender is subsequent to AJAX - do that with a callback
  // changing state is still better way to do it, but this could explain seemingly inconsistent behavior (all about timing of async parts)

  // map needs to reset to not have displays stacked
  // heatmap.setMap(null);
  heatmapData = [];
  var timeIndex = $('#mapview').val();

  // AJAX call
  $.get('reports.json', {'time_index': timeIndex}, function (reports) {

    console.log(timeIndex);
    console.log(reports);

    for (var key in reports) {
      report = reports[key];

      // Add coordinate to heatmapData
      heatmapData.push({location: new google.maps.LatLng(report['lat'], report['lng']), weight: report['abs_temp'] - MIN_TEMP});
    }

    if(typeof (mvcObj)=='object') mvcObj.clear();
    mvcObj = new google.maps.MVCArray(heatmapData);
    heatmap = new google.maps.visualization.HeatmapLayer({
      data: mvcObj,
      maxIntensity: 500,
      radius: 20,
      dissipating: false,
    });
    heatmap.setMap(map);

    setGradient();
    setLegendGradient();
    setLegendLabels();

    // google.maps.event.addDomListener(window, 'load', initMap);
  });
}

function initMap() {

  heatmapData = [];
  // markerData = [];

  var timeIndex = $('#mapview').val();
  console.log(timeIndex);

  // // AJAX call
  $.get('/reports.json', {'time_index': timeIndex}, function (reports) {

    for (var key in reports) {
      report = reports[key];

      // Add coordinate to heatmapData
      heatmapData.push({location: new google.maps.LatLng(report['lat'], report['lng']), weight: report['abs_temp'] - MIN_TEMP});
      // markerData.push({position: {report['lat'], report['lng']}, });
    }
  // });

  if(typeof (mvcObj)=='object') mvcObj.clear();
  mvcObj = new google.maps.MVCArray(heatmapData);
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 0, lng: 0},
    zoom: 2,
    mapTypeId: 'terrain',
    mapTypeControl: false,
    zoomControl: true,
    scaleControl: false,
    // styles: mapStyle
  });

  // marker = new google.maps.Marker({
  //   position: myLatLng,
  //   map: map,
  //   title: 'Hello World!'
  // });

  heatmap = new google.maps.visualization.HeatmapLayer({
    data: mvcObj,
    maxIntensity: 500,
    radius: 20,
    dissipating: false,
  });
  heatmap.setMap(map);

  setGradient();
  setLegendGradient();
  setLegendLabels();

  // google.maps.event.addDomListener(window, 'load', changeMap);
});
}

function setGradient() {
  gradient = [
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
  ];
  heatmap.set('gradient', gradient);
}

function setLegendGradient() {
    var gradientCss = '(left';
    for (var i = 0; i < gradient.length; ++i) {
        gradientCss += ', ' + gradient[i];
    }
    gradientCss += ')';
    
    $('#legendGradient').css('background', '-webkit-linear-gradient' + gradientCss);
    $('#legendGradient').css('background', '-moz-linear-gradient' + gradientCss);
    $('#legendGradient').css('background', '-o-linear-gradient' + gradientCss);
    $('#legendGradient').css('background', 'linear-gradient' + gradientCss);
}

function setLegendLabels() {
    google.maps.event.addListenerOnce(map, 'tilesloaded', function() {
        var getMax = heatmap['gm_bindings_']['data'];
        if(typeof getMax !== 'undefined') {
          for(var p in getMax) {
            maxIntensity = getMax[p].Gc.j;
            break;
          }
        }
        var legendWidth = $('#legendGradient').outerWidth();
        
        for (var i = 0; i <= maxIntensity; ++i) {
            var offset = i * legendWidth / maxIntensity;
            if (i > 0 && i < maxIntensity) {
                offset -= 0.5;
            } else if (i == maxIntensity) {
                offset -= 1;
            }
            
            $('#legend').append($('<div>').css({
                'position': 'absolute',
                'left': offset + 'px',
                'top': '15px',
                'width': '1px',
                'height': '3px',
                'background': 'black'
            }));
            $('#legend').append($('<div>').css({
                'position': 'absolute',
                'left': (offset - 5) + 'px',
                'top': '18px',
                'width': '10px',
                'text-align': 'center',
                'font-size': '0.8em',
            }).html(i));
        }
    });
}

// function getDates() {
//   var sliderDates = [];
//   $.get('/dates.json', function (dates) {
//     for (var key in dates) {
//       var given_date = dates[key];
//       sliderDates.push(given_date.moyr);
//     }
//   });
// }

// do setup on document load
// http://api.jqueryui.com/slider/
$( function() {
  var select = $("#mapview");
  // var time = $("#mapview").val();
  // console.log(time);
  var slider = $("<div id='slider style='width=40em;'><div id='custom-handle' style='width:5em;' class='ui-slider-handle'></div></div>").insertAfter(select).slider({
    min: 1850,
    max: 2017,
    range: "min",
    value: select[0].selectedIndex + 1,
    slide: function(event, ui){
      select[0].selectedIndex = ui.value - 1;
      var handle = $("#custom-handle");
      handle.text(ui.value);
    }
  });


  $("#mapview").on('change', function() {
    slider.slider("value", this.selectedIndex + 1);
  });
});

//   $("#slider").slider({
//     create: function() {
//       handle.text( $( this ).slider( "value" ) );
//     },
//     slide: function( event, ui ) {
//       handle.text( ui.value );
//     }
//   });
// } );

// function createSlider(show_date) {
//   $("#slider").slider({
//     min: 1850,
//     max: 2018,
//     slide: function(event, ui){
//       $('#slider')
//     }
//   });
// }

// google.maps.event.addDomListener(window, 'load', initMap);

$('#selectmap').on('click', changeMap);


    // map.data.loadGeoJson(
    // 'https://storage.googleapis.com/mapsdevsite/json/google.json');
    // }