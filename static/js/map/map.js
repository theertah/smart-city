(function(global){
  "use strict";

  var map = null;
  var markers = {};
  var hasFitBounds = false;

  function congestionColor(level){
    if(level >= 70) return "#e15a4f";
    if(level >= 40) return "#e9ad42";
    return "#51b78b";
  }

  function init(){
    var status = document.getElementById("trafficMapStatus");
    if(!global.L){
      status.textContent = "Map tiles could not load. Use the Google Maps link for traffic.";
      return;
    }

    map = global.L.map("trafficMap").setView([12.9716,77.5946],11);
    global.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{
      maxZoom:19,
      attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  }

  function update(data){
    var status = document.getElementById("trafficMapStatus");
    if(!map) return;

    var points = [];
    data.forEach(function(reading){
      var latitude = Number(reading.latitude);
      var longitude = Number(reading.longitude);
      if(!Number.isFinite(latitude) || !Number.isFinite(longitude)) return;

      var point = [latitude,longitude];
      var congestion = Number(reading.congestion_level) || 0;
      var color = congestionColor(congestion);
      var marker = markers[reading.location_id];

      if(!marker){
        marker = global.L.circleMarker(point,{
          radius:9,
          weight:2,
          color:color,
          fillColor:color,
          fillOpacity:0.88
        }).addTo(map);
        markers[reading.location_id] = marker;
      }else{
        marker.setLatLng(point);
        marker.setStyle({color:color,fillColor:color});
      }

      var label = document.createElement("span");
      label.textContent = reading.name || reading.zone;
      marker.bindTooltip(label);

      var popup = document.createElement("div");
      var title = document.createElement("strong");
      title.textContent = (reading.name || reading.zone) + " · " + reading.zone;
      var details = document.createElement("div");
      details.textContent = "Congestion " + Math.round(congestion) + "% · " + reading.vehicle_count +
        " vehicles · " + Number(reading.average_speed).toFixed(1) + " km/h";
      popup.appendChild(title);
      popup.appendChild(details);
      marker.bindPopup(popup);
      points.push(point);
    });

    if(points.length && !hasFitBounds){
      map.fitBounds(points,{padding:[28,28],maxZoom:12});
      hasFitBounds = true;
    }
    status.textContent = points.length ? "Updated " + new Date().toLocaleTimeString() : "No traffic readings available yet.";
  }

  global.CityTrafficMap = {init:init,update:update};
})(window);