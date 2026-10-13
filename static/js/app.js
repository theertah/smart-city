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
