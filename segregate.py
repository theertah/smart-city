import os
import re

base_path = r"C:\Users\theer\Downloads\smart-city-backend\smart-city-backend"
js_dir = os.path.join(base_path, "static", "js")
features_dir = os.path.join(js_dir, "features")

os.makedirs(features_dir, exist_ok=True)

with open(os.path.join(js_dir, "app.js"), "r", encoding="utf-8") as f:
    app_js_content = f.read()

# I will just write modular code instead of complex parsing

utils_js = """
window.CityUtils = {
    fmt: function(n, d) { d = d || 0; return Number(n).toFixed(d); },
    areaLabel: function(item) {
        return this.escapeHtml(item.name || item.zone) + (item.name && item.zone ? " · " + this.escapeHtml(item.zone) : "");
    },
    escapeHtml: function(value) {
        return String(value || "").replace(/[&<>"']/g, function(character) {
            return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[character];
        });
    }
};
"""

overview_js = """
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
"""

traffic_js = """
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
"""

environment_js = """
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
"""

waste_js = """
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
"""

complaints_js = """
window.FeatureComplaints = {
    updateSelection: function() {
        var checks = Array.from(document.querySelectorAll(".complaint-select"));
        var selected = checks.filter(function(check){ return check.checked; }).length;
        var button = document.getElementById("deleteSelectedComplaints");
        if (button) {
            button.disabled = selected === 0;
            button.textContent = selected ? "Delete selected ("+selected+")" : "Delete selected";
        }
        var selectAll = document.getElementById("selectAllComplaints");
        if (selectAll) {
            selectAll.checked = checks.length > 0 && selected === checks.length;
            selectAll.indeterminate = selected > 0 && selected < checks.length;
        }
    },
    load: function() {
        var self = this;
        fetch("/api/complaints").then(r=>r.json()).then(function(data){
            var complaintsTbody = document.querySelector("#complaintsTable tbody");
            if (complaintsTbody) {
                complaintsTbody.innerHTML = data.length ? data.map(function(c){
                    return '<tr><td><input class="complaint-select" type="checkbox" value="'+Number(c.id)+'" aria-label="Select complaint '+Number(c.id)+'"></td><td>'+window.CityUtils.escapeHtml(c.category)+'</td><td>'+window.CityUtils.escapeHtml(c.location_name)+' · '+window.CityUtils.escapeHtml(c.zone)+'</td><td>'+window.CityUtils.escapeHtml(c.department)+'</td><td>'+window.CityUtils.escapeHtml(c.priority_label)+'</td><td>'+window.CityUtils.escapeHtml(c.status)+'</td></tr>';
                }).join("") : '<tr><td colspan="6">No complaints yet.</td></tr>';
            }
            var selectAll = document.getElementById("selectAllComplaints");
            if (selectAll) selectAll.checked = false;
            self.updateSelection();
        }).catch(function(){
            var msg = document.getElementById("complaintMessage");
            if(msg) msg.textContent = "Unable to load complaints.";
        });
    },
    init: function() {
        var self = this;
        var select = document.getElementById("complaintZone");
        if(select) {
            fetch("/api/traffic").then(r=>r.json()).then(function(data){
                select.innerHTML = data.map(function(item){
                    return '<option value="'+window.CityUtils.escapeHtml(item.zone)+'">'+window.CityUtils.escapeHtml(item.name)+" — "+window.CityUtils.escapeHtml(item.zone)+"</option>";
                }).join("");
                if(!data.length) select.innerHTML = '<option value="">No Bengaluru areas available</option>';
            }).catch(function(){
                select.innerHTML = '<option value="">Unable to load areas</option>';
            });
        }
        
        var submitBtn = document.getElementById("submitComplaint");
        if (submitBtn) {
            submitBtn.addEventListener("click", function(){
                var text = document.getElementById("complaintText").value.trim();
                var zone = document.getElementById("complaintZone").value;
                if(!text || !zone) return;
                fetch("/api/complaints", {
                    method:"POST", headers:{"Content-Type":"application/json"},
                    body: JSON.stringify({description:text, zone:zone})
                }).then(r=>{
                    if(!r.ok) throw new Error("Unable to submit complaint.");
                    return r.json();
                }).then(function(){
                    document.getElementById("complaintText").value = "";
                    document.getElementById("complaintMessage").textContent = "Complaint submitted.";
                    self.load();
                }).catch(function(error){
                    document.getElementById("complaintMessage").textContent = error.message;
                });
            });
        }

        var selectAllComplaints = document.getElementById("selectAllComplaints");
        if (selectAllComplaints) {
            selectAllComplaints.addEventListener("change",function(){
                document.querySelectorAll(".complaint-select").forEach(function(check){ check.checked = this.checked; }, this);
                self.updateSelection();
            });
        }
        
        var complaintsTbody = document.querySelector("#complaintsTable tbody");
        if (complaintsTbody) {
            complaintsTbody.addEventListener("change",function(event){
                if(event.target.matches(".complaint-select")) self.updateSelection();
            });
        }
        
        var deleteBtn = document.getElementById("deleteSelectedComplaints");
        if (deleteBtn) {
            deleteBtn.addEventListener("click",function(){
                var ids = Array.from(document.querySelectorAll(".complaint-select:checked")).map(function(check){ return Number(check.value); });
                if(!ids.length || !window.confirm("Delete "+ids.length+" selected complaint(s)? This cannot be undone.")) return;
                this.disabled = true;
                fetch("/api/complaints",{
                    method:"DELETE",headers:{"Content-Type":"application/json"},body:JSON.stringify({ids:ids})
                }).then(function(response){
                    return response.json().then(function(data){
                        if(!response.ok) throw new Error(data.error || "Unable to delete complaints.");
                        return data;
                    });
                }).then(function(result){
                    document.getElementById("complaintMessage").textContent = "Deleted "+result.deleted+" complaint(s).";
                    self.load();
                    deleteBtn.disabled = false;
                }).catch(function(error){
                    document.getElementById("complaintMessage").textContent = error.message;
                    self.updateSelection();
                    deleteBtn.disabled = false;
                });
            });
        }
    }
};
"""

theme_js = """
window.FeatureTheme = {
    init: function() {
        var headerDiv = document.querySelector("header > div");
        if (headerDiv) {
            var darkModeBtn = document.createElement("button");
            darkModeBtn.textContent = "Toggle Dark Mode";
            darkModeBtn.className = "header-link";
            darkModeBtn.style.marginRight = "20px";
            darkModeBtn.style.color = "var(--text)";
            darkModeBtn.style.background = "var(--bg)";
            darkModeBtn.style.border = "1px solid var(--line)";
            darkModeBtn.style.cursor = "pointer";
            darkModeBtn.style.padding = "4px 8px";
            darkModeBtn.style.borderRadius = "4px";
            
            if (localStorage.getItem("theme") === "dark") {
                document.documentElement.setAttribute("data-theme", "dark");
            }
            
            darkModeBtn.addEventListener("click", function() {
                if (document.documentElement.getAttribute("data-theme") === "dark") {
                    document.documentElement.removeAttribute("data-theme");
                    localStorage.setItem("theme", "light");
                } else {
                    document.documentElement.setAttribute("data-theme", "dark");
                    localStorage.setItem("theme", "dark");
                }
            });
            
            var clock = document.getElementById("clock");
            if(clock) {
                headerDiv.insertBefore(darkModeBtn, clock);
            } else {
                headerDiv.appendChild(darkModeBtn);
            }
        }
    }
};
"""

core_js = """
(function(){
  "use strict";

  document.querySelectorAll("nav button").forEach(function(btn){
    btn.addEventListener("click", function(){
      document.querySelectorAll("nav button").forEach(function(b){ b.classList.remove("active"); });
      document.querySelectorAll(".tab").forEach(function(t){ t.classList.remove("active"); });
      btn.classList.add("active");
      var tabEl = document.getElementById("tab-"+btn.dataset.tab);
      if(tabEl) tabEl.classList.add("active");
      loadTab(btn.dataset.tab);
    });
  });

  function loadTab(tab){
    if(tab==="overview" && window.FeatureOverview) window.FeatureOverview.load();
    else if(tab==="traffic" && window.FeatureTraffic) window.FeatureTraffic.load();
    else if(tab==="environment" && window.FeatureEnvironment) window.FeatureEnvironment.load();
    else if(tab==="waste" && window.FeatureWaste) window.FeatureWaste.load();
    else if(tab==="complaints" && window.FeatureComplaints) window.FeatureComplaints.load();
  }

  function tickClock(){ 
      var clock = document.getElementById("clock");
      if(clock) clock.textContent = new Date().toLocaleTimeString(); 
  }
  setInterval(tickClock,1000); tickClock();

  if(window.FeatureTheme) window.FeatureTheme.init();
  if(window.CityTrafficMap) window.CityTrafficMap.init();
  if(window.FeatureComplaints) window.FeatureComplaints.init();
  
  if(window.FeatureOverview) window.FeatureOverview.load();
  
  setInterval(function(){
    var active = document.querySelector("nav button.active");
    if(active) loadTab(active.dataset.tab);
  }, 6000);
})();
"""

files = {
    "utils.js": utils_js,
    "overview.js": overview_js,
    "traffic.js": traffic_js,
    "environment.js": environment_js,
    "waste.js": waste_js,
    "complaints.js": complaints_js,
    "theme.js": theme_js,
}

for filename, content in files.items():
    with open(os.path.join(features_dir, filename), "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# overwrite app.js with core_js
with open(os.path.join(js_dir, "app.js"), "w", encoding="utf-8") as f:
    f.write(core_js.strip() + "\n")

print("Segregation successful!")
