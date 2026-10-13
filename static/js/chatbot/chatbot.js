(function(){
  "use strict";

  var form = document.getElementById("chatForm");
  var input = document.getElementById("chatInput");
  var sendButton = document.getElementById("chatSend");
  var windowElement = document.getElementById("chatWindow");
  var statusElement = document.getElementById("chatbotStatus");

  function addMessage(text, role, extraClass){
    var message = document.createElement("div");
    message.className = "chat-message " + role + (extraClass ? " " + extraClass : "");
    message.textContent = text;
    windowElement.appendChild(message);
    windowElement.scrollTop = windowElement.scrollHeight;
    return message;
  }

  async function sendMessage(event){
    event.preventDefault();
    var question = input.value.trim();
    if(!question || sendButton.disabled) return;

    var history = Array.from(windowElement.querySelectorAll(".chat-message")).map(function(message){
      return {
        role:message.classList.contains("user") ? "user" : "assistant",
        content:message.textContent.trim()
      };
    });
    addMessage(question,"user");
    input.value = "";
    sendButton.disabled = true;
    input.disabled = true;
    var pending = addMessage("Checking Bengaluru city data...","assistant","pending");

    try{
      var response = await fetch("/api/assistant",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({question:question,messages:history})
      });
      var result = await response.json();
      if(!response.ok) throw new Error(result.error || "The assistant could not answer that just now.");
      pending.textContent = result.answer || "I couldn't find an answer for that question.";
      var links = result.links || (result.maps_url ? [{label:result.maps_label,url:result.maps_url}] : []);
      links.forEach(function(item){
        var sourceUrl;
        try{ sourceUrl = new URL(item.url,window.location.href); }catch(error){ return; }
        if(sourceUrl.protocol !== "https:") return;
        var mapLink = document.createElement("a");
        mapLink.className = "chat-response-link";
        mapLink.href = sourceUrl.href;
        mapLink.target = "_blank";
        mapLink.rel = "noopener noreferrer";
        mapLink.textContent = item.label || "Open route details";
        pending.appendChild(document.createElement("br"));
        pending.appendChild(mapLink);
      });
      pending.classList.remove("pending");
    }catch(error){
      pending.textContent = error.message || "Couldn't reach the assistant. Check that the server is running and try again.";
      pending.classList.remove("pending");
    }finally{
      sendButton.disabled = false;
      input.disabled = false;
      input.focus();
    }
  }

  addMessage("Hi! Ask me about traffic, air quality, waste, alerts, or a specific Bengaluru area.","assistant");
  form.addEventListener("submit",sendMessage);

  fetch("/api/assistant/status").then(function(response){ return response.json(); }).then(function(status){
    statusElement.textContent = status.ai_enabled ? (status.search_enabled ? "AI + web search" : "AI enabled") : "Demo mode";
    statusElement.classList.toggle("offline",!status.ai_enabled);
    statusElement.title = status.ai_enabled ? "Gemini can answer open-ended questions; Google Search grounding is enabled when needed." : "Set GEMINI_API_KEY in your local .env file to enable open-ended AI answers.";
  }).catch(function(){
    statusElement.textContent = "Status unavailable";
    statusElement.classList.add("offline");
  });
})();