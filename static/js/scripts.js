
function sendMessage() {
    var input = document.getElementById("chatbot-input").value;
    fetch("/chatbot", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({ "message": input })
    }).then(response => response.json()).then(data => {
        var messages = document.getElementById("chatbot-messages");
        messages.innerHTML += "<p><strong>You:</strong> " + input + "</p>";
        messages.innerHTML += "<p><strong>Chatbot:</strong> " + data.response + "</p>";
        document.getElementById("chatbot-input").value = "";
    });
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function sendMessage() {
    var input = document.getElementById("chatbot-input").value;
    fetch("/chatbot", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({ "message": input })
    }).then(response => response.json()).then(data => {
        var messages = document.getElementById("chatbot-messages");
        messages.innerHTML += "<p><strong>You:</strong> " + input + "</p>";
        messages.innerHTML += "<p><strong>Chatbot:</strong> " + data.response + "</p>";
        document.getElementById("chatbot-input").value = "";
    });
}