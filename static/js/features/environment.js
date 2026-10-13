window.FeatureEnvironment = {
    load: function() {
        fetch("/api/environment").then(r=>r.json()).then(function(data){
            var el = document.querySelector("#envTable tbody");
            if(el) el.innerHTML = data.map(function(e){
                var temperature = e.live_temperature_c == null ? "Unavailable" : window.CityUtils.fmt(e.live_temperature_c,1)+'°C';
                return '<tr><td>'+window.CityUtils.areaLabel(e)+'</td><td title="'+(e.weather_time || "")+'">'+temperature+'</td><td>'+window.CityUtils.fmt(e.humidity)+'%</td><td>'+window.CityUtils.fmt(e.air_quality)+'</td><td>'+window.CityUtils.fmt(e.noise_level)+' dB</td></tr>';
            }).join("");
        });
    }
};
