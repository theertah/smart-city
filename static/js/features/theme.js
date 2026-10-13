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
