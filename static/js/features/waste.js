window.FeatureWaste = {
    load: function() {
        fetch("/api/waste").then(r=>r.json()).then(function(data){
            var el = document.querySelector("#wasteTable tbody");
            if(el) el.innerHTML = data.map(function(w){
                return '<tr><td>'+window.CityUtils.areaLabel(w)+'</td><td>'+window.CityUtils.fmt(w.fill_percentage)+'%</td><td>'+window.CityUtils.fmt(w.predicted_fill_5h)+'%</td><td>'+w.forecast_model+'</td></tr>';
            }).join("");
        });
    }
};
