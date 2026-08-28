```javascript
const descriptionInput = document.getElementById("description");
const generateButton = document.getElementById("generateButton");
const themeToggle = document.getElementById("themeToggle");
const statusText = document.getElementById("status");
const diagramCanvas = document.getElementById("diagramCanvas");


// ------------------------------
// Theme
// ------------------------------

function loadTheme() {
    const savedTheme = localStorage.getItem("rbgraph-theme");

    if (savedTheme) {
        document.documentElement.dataset.theme = savedTheme;
        return;
    }

    const prefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)"
    ).matches;

    document.documentElement.dataset.theme =
        prefersDark ? "dark" : "light";
}


function toggleTheme() {
    const currentTheme =
        document.documentElement.dataset.theme;

    const newTheme =
        currentTheme === "dark" ? "light" : "dark";

    document.documentElement.dataset.theme = newTheme;

    localStorage.setItem(
        "rbgraph-theme",
        newTheme
    );
}


// ------------------------------
// Generate
// ------------------------------

function generateDiagram() {
    const description =
        descriptionInput.value.trim();

    if (!description) {
        statusText.textContent =
            "Please describe your system first.";

        return;
    }

    statusText.textContent =
        "Description received.";

    diagramCanvas.innerHTML = `
        <div>
            <strong>RBGraph received:</strong>
            <p>${escapeHtml(description)}</p>
        </div>
    `;
}


// ------------------------------
// Security helper
// ------------------------------

function escapeHtml(value) {
    const div = document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}


// ------------------------------
// Events
// ------------------------------

themeToggle.addEventListener(
    "click",
    toggleTheme
);

generateButton.addEventListener(
    "click",
    generateDiagram
);


// ------------------------------
// Initialize
// ------------------------------

loadTheme();
