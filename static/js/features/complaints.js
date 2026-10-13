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
