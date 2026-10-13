window.FeatureTraffic = {
    load: function() {
        fetch("/api/traffic").then(r=>r.json()).then(function(data){
            var el = document.querySelector("#trafficTable tbody");
            if(el) el.innerHTML = data.map(function(t){
                return '<tr><td>'+window.CityUtils.areaLabel(t)+'</td><td>'+t.vehicle_count+'</td><td>'+window.CityUtils.fmt(t.average_speed,1)+' km/h</td><td>'+window.CityUtils.fmt(t.congestion_level)+'%</td></tr>';
            }).join("");
        });
        fetch("/api/predictions").then(r=>r.json()).then(function(data){
            var el = document.querySelector("#predictionTable tbody");
            if(el) el.innerHTML = data.map(function(p){
                return '<tr><td>'+window.CityUtils.areaLabel(p)+'</td><td>'+window.CityUtils.fmt(p.current)+'%</td><td>'+window.CityUtils.fmt(p.prediction)+'%</td><td>'+window.CityUtils.fmt(p.confidence*100)+'%</td><td>'+p.model+'</td></tr>';
            }).join("");
        });
    }
};
