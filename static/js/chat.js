const button =
    document.getElementById(
        "send-btn"
    );

button.addEventListener(
    "click",
    sendMessage
);

async function sendMessage() {

    const input =
        document.getElementById(
            "message"
        );

    const message =
        input.value;

    if (!message) {
        return;
    }

    const box =
        document.getElementById(
            "chat-box"
        );

    box.innerHTML += `
        <div class="user">
            ${message}
        </div>
    `;

    const response =
        await fetch(
            "/chat",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    query: message
                })
            }
        );

    const data =
        await response.json();

    box.innerHTML += `
        <div class="bot">
            ${data.response}
        </div>
    `;

    input.value = "";

    localStorage.setItem(
        "logs",
        JSON.stringify(
            data.logs
        )
    );
}