const logs =
    JSON.parse(
        localStorage.getItem(
            "logs"
        )
    ) || [];

const container =
    document.getElementById(
        "logs"
    );

logs.forEach(log => {

    container.innerHTML += `
        <div class="log">
            ${log}
        </div>
    `;

});