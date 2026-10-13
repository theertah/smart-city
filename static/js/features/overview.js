window.FeatureOverview = {
    load: function() {
        var trafficRequest = fetch("/api/traffic").then(r=>r.json()).then(function(data){
            if (window.CityTrafficMap) window.CityTrafficMap.update(data);
            return data;
        });
        Promise.all([fetch("/api/alerts").then(r=>r.json()), trafficRequest,
                     fetch("/api/environment").then(r=>r.json()), fetch("/api/waste").then(r=>r.json())]).then(function(res){
            var alerts=res[0], traffic=res[1], env=res[2], waste=res[3];
            var alertsEl = document.getElementById("alerts");
            if (alertsEl) {
                alertsEl.innerHTML = alerts.length ? alerts.slice(0,6).map(function(a){
                    return '<div class="alert '+(a.severity==="critical"?"critical":"")+'"><strong>'+a.title+'</strong><div>'+a.detail+'</div></div>';
                }).join("") : '<div class="alert">No active alerts — all systems nominal.</div>';
            }

            var zoneTableBody = document.querySelector("#zoneTable tbody");
            if (zoneTableBody) {
                var rows = traffic.map(function(t){
                    var e = env.find(x=>x.zone===t.zone) || {};
                    var w = waste.find(x=>x.zone===t.zone) || {};
                    return '<tr><td>'+window.CityUtils.areaLabel(t)+'</td><td>'+window.CityUtils.fmt(t.congestion_level)+'%</td><td>'+window.CityUtils.fmt(e.air_quality)+'</td><td>'+window.CityUtils.fmt(w.fill_percentage)+'%</td></tr>';
                }).join("");
                zoneTableBody.innerHTML = rows;
            }
        }).catch(function(){
            var status = document.getElementById("trafficMapStatus");
            if(status) status.textContent = "Unable to load traffic readings. Retrying shortly.";
        });
    }
};
