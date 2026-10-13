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
