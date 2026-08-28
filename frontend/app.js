let currentDiagram = null;
let currentSvg = "";
let zoom = 1;
let activeTheme = localStorage.getItem("rbgraph-theme") || "system";

const elements = {
  name: document.getElementById("diagramName"),
  type: document.getElementById("diagramType"),
  prompt: document.getElementById("promptInput"),
  generate: document.getElementById("generateButton"),
  command: document.getElementById("commandInput"),
  sendCommand: document.getElementById("commandButton"),
  theme: document.getElementById("themeToggle"),
  status: document.getElementById("connectionStatus"),
  stage: document.getElementById("diagramStage"),
  chat: document.getElementById("chatMessages"),
  meta: document.getElementById("diagramMeta"),
  validation: document.getElementById("validationStatus"),
  save: document.getElementById("saveButton"),
  copy: document.getElementById("copyPng"),
  export: document.getElementById("exportButton"),
  format: document.getElementById("exportFormat"),
  scale: document.getElementById("exportScale"),
  history: document.getElementById("historyList"),
  refreshHistory: document.getElementById("refreshHistory"),
  zoomOut: document.getElementById("zoomOut"),
  zoomIn: document.getElementById("zoomIn"),
  zoomReset: document.getElementById("zoomReset")
};

function setTheme(theme) {
  activeTheme = theme;
  localStorage.setItem("rbgraph-theme", theme);
  const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  document.documentElement.dataset.theme = theme === "system" ? (systemDark ? "dark" : "light") : theme;
  elements.theme.textContent = document.documentElement.dataset.theme === "dark" ? "☀" : "☾";
}

function cycleTheme() {
  setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
}

function setStatus(text, state = "ready") {
  elements.status.textContent = text;
  elements.status.dataset.state = state;
}

function addMessage(text, role = "assistant") {
  const message = document.createElement("div");
  message.className = `chat-message ${role}`;
  message.innerHTML = text;
  elements.chat.appendChild(message);
  elements.chat.scrollTop = elements.chat.scrollHeight;
}

function setLoading(loading) {
  elements.generate.disabled = loading;
  elements.sendCommand.disabled = loading;
  elements.generate.querySelector("span").textContent = loading ? "Working…" : "Generate";
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {"Content-Type": "application/json"},
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(data.detail) ? data.detail.join(" ") : (data.detail || "Request failed.");
    throw new Error(detail);
  }
  return data;
}

async function generateDiagram() {
  const description = elements.prompt.value.trim();
  if (!description) {
    addMessage("Describe the system first.");
    return;
  }

  setLoading(true);
  setStatus("Generating", "busy");
  try {
    const data = await requestJson("/api/diagrams/generate", {
      method: "POST",
      body: JSON.stringify({
        description,
        name: elements.name.value.trim() || "Untitled Diagram",
        diagram_type: elements.type.value
      })
    });
    currentDiagram = data.diagram;
    currentSvg = data.svg;
    zoom = 1;
    renderSvg();
    addMessage(escapeText(description), "user");
    addMessage(`Generated <strong>${escapeText(currentDiagram.name)}</strong> as ${escapeText(labelForType(currentDiagram.diagram_type))}.`);
    setStatus("Ready");
    elements.validation.textContent = "Diagram validated · SVG validated";
  } catch (error) {
    setStatus("Error", "error");
    elements.validation.textContent = error.message;
    addMessage(escapeText(error.message));
  } finally {
    setLoading(false);
  }
}

async function sendCommand() {
  const command = elements.command.value.trim();
  if (!command) return;
  if (!currentDiagram) {
    addMessage("Generate a diagram first.");
    return;
  }

  elements.command.value = "";
  addMessage(escapeText(command), "user");
  setStatus("Updating", "busy");

  try {
    const data = await requestJson("/api/diagrams/command", {
      method: "POST",
      body: JSON.stringify({diagram: currentDiagram, command})
    });
    currentDiagram = data.diagram;
    currentSvg = data.svg;
    renderSvg();
    addMessage(escapeText(data.message));
    elements.validation.textContent = "Diagram validated · SVG validated";
    setStatus("Ready");
  } catch (error) {
    addMessage(escapeText(error.message));
    setStatus("Error", "error");
    elements.validation.textContent = error.message;
  }
}

function renderSvg() {
  elements.stage.innerHTML = currentSvg;
  const svg = elements.stage.querySelector("svg");
  if (!svg) return;
  svg.style.transform = `scale(${zoom})`;
  elements.meta.textContent = `${currentDiagram.name} · ${labelForType(currentDiagram.diagram_type)} · ${currentDiagram.nodes.length} nodes · ${currentDiagram.edges.length} connections`;
  elements.zoomReset.textContent = `${Math.round(zoom * 100)}%`;
}

function escapeText(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  }[char]));
}

function labelForType(type) {
  return {
    architecture: "Architecture",
    workflow: "Workflow",
    sequence: "Sequence",
    data_flow: "Data flow",
    lifecycle: "Lifecycle"
  }[type] || type;
}

async function saveCurrentDiagram() {
  if (!currentDiagram) {
    addMessage("Generate a diagram first.");
    return;
  }
  try {
    const data = await requestJson("/api/diagrams", {
      method: "POST",
      body: JSON.stringify(currentDiagram)
    });
    addMessage(`Saved diagram #${data.id}.`);
    await loadHistory();
  } catch (error) {
    addMessage(escapeText(error.message));
  }
}

function parseViewBox(svg) {
  const value = svg.getAttribute("viewBox");
  if (!value) throw new Error("SVG viewBox is missing.");
  const values = value.trim().split(/\s+/).map(Number);
  if (values.length !== 4 || values.some(Number.isNaN) || values[2] <= 0 || values[3] <= 0) throw new Error("SVG viewBox is invalid.");
  return {x: values[0], y: values[1], width: values[2], height: values[3]};
}

async function svgToBlob() {
  const svg = elements.stage.querySelector("svg");
  if (!svg) throw new Error("There is no diagram to export.");
  return new Blob([svg.outerHTML], {type: "image/svg+xml;charset=utf-8"});
}

async function rasterizeSvg(type, scale) {
  const svg = elements.stage.querySelector("svg");
  if (!svg) throw new Error("There is no diagram to export.");

  const viewBox = parseViewBox(svg);
  const clone = svg.cloneNode(true);
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  clone.setAttribute("width", String(viewBox.width));
  clone.setAttribute("height", String(viewBox.height));

  const source = new Blob([clone.outerHTML], {type: "image/svg+xml;charset=utf-8"});
  const url = URL.createObjectURL(source);

  try {
    const image = await new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error("Could not rasterize SVG."));
      img.src = url;
    });

    const canvas = document.createElement("canvas");
    canvas.width = Math.ceil(viewBox.width * scale);
    canvas.height = Math.ceil(viewBox.height * scale);

    const context = canvas.getContext("2d");
    if (!context) throw new Error("Canvas rendering is unavailable.");
    context.imageSmoothingEnabled = true;
    context.imageSmoothingQuality = "high";
    context.drawImage(image, 0, 0, canvas.width, canvas.height);

    const mime = {png: "image/png", jpeg: "image/jpeg", webp: "image/webp"}[type];
    return await new Promise((resolve, reject) => {
      canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error("The browser could not create the image.")), mime, type === "jpeg" ? 0.96 : 0.98);
    });
  } finally {
    URL.revokeObjectURL(url);
  }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function fileBase() {
  return (currentDiagram?.name || "rbgraph-diagram").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "") || "rbgraph-diagram";
}

function validateStandaloneHtml(html) {
  const parser = new DOMParser();
  const documentNode = parser.parseFromString(html, "text/html");
  if (!documentNode.documentElement || !documentNode.head || !documentNode.body) throw new Error("Standalone HTML structure is invalid.");
  if (documentNode.querySelector("parsererror")) throw new Error("Standalone HTML could not be parsed.");
  const svg = documentNode.querySelector("svg");
  if (!svg) throw new Error("Standalone HTML is missing the SVG diagram.");
  if (!svg.getAttribute("viewBox")) throw new Error("Standalone SVG is missing its viewBox.");
  if (documentNode.querySelector("link[href],img[src],iframe[src],object[data],script[src]")) throw new Error("Standalone export contains an external dependency.");
  return html;
}

function standaloneHtml() {
  const svg = elements.stage.querySelector("svg");
  if (!svg) throw new Error("There is no diagram to export.");
  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${escapeText(currentDiagram.name)}</title>
<style>
:root{color-scheme:light dark}*{box-sizing:border-box}html,body{margin:0;min-height:100%;font-family:Inter,system-ui,sans-serif}body{background:#f3f6fa;color:#0f172a;display:grid;place-items:center;padding:24px}.viewer{width:min(1400px,100%);display:grid;gap:16px}.toolbar{display:flex;justify-content:space-between;align-items:center;gap:12px}.toolbar button{border:1px solid #dce4ee;border-radius:9px;padding:9px 12px;background:#fff;color:#0f172a;cursor:pointer}.frame{overflow:auto;border:1px solid #dce4ee;border-radius:18px;background:#f8fafc;padding:12px}.frame svg{display:block;width:100%;height:auto}@media(prefers-color-scheme:dark){body{background:#08111f;color:#e5edf8}.toolbar button{background:#0f1a2b;color:#e5edf8;border-color:#23344b}.frame{background:#0b1220;border-color:#23344b}}
</style>
</head>
<body>
<div class="viewer">
<div class="toolbar"><strong>${escapeText(currentDiagram.name)}</strong><button id="theme" type="button">Toggle theme</button></div>
<div class="frame">${svg.outerHTML}</div>
</div>
<script>
const button=document.getElementById("theme");
button.addEventListener("click",()=>{document.documentElement.style.colorScheme=document.documentElement.style.colorScheme==="dark"?"light":"dark";});
</script>
</body>
</html>`;
  return validateStandaloneHtml(html);
}

async function exportDiagram() {
  if (!currentDiagram) {
    addMessage("Generate a diagram first.");
    return;
  }

  const format = elements.format.value;
  const scale = Number(elements.scale.value);
  setStatus("Exporting", "busy");
  try {
    if (format === "svg") {
      const svg = await svgToBlob();
      const svgText = await svg.text();
      validateStandaloneHtml(`<!doctype html><html><head><meta charset="utf-8"></head><body>${svgText}</body></html>`);
      downloadBlob(svg, `${fileBase()}.svg`);
    } else if (format === "html") {
      downloadBlob(new Blob([standaloneHtml()], {type: "text/html;charset=utf-8"}), `${fileBase()}.html`);
    } else {
      const blob = await rasterizeSvg(format, scale);
      const extension = format === "jpeg" ? "jpg" : format;
      downloadBlob(blob, `${fileBase()}-${scale}x.${extension}`);
    }
    setStatus("Ready");
  } catch (error) {
    setStatus("Error", "error");
    addMessage(escapeText(error.message));
  }
}

async function copyPng() {
  if (!currentDiagram) {
    addMessage("Generate a diagram first.");
    return;
  }
  try {
    const blob = await rasterizeSvg("png", 4);
    if (!navigator.clipboard || !window.ClipboardItem) throw new Error("PNG clipboard support is unavailable in this browser or context.");
    await navigator.clipboard.write([new ClipboardItem({"image/png": blob})]);
    addMessage("Copied the PNG to your clipboard.");
  } catch (error) {
    addMessage(escapeText(error.message));
  }
}

async function loadHistory() {
  try {
    const data = await requestJson("/api/diagrams");
    if (!data.items.length) {
      elements.history.innerHTML = '<div class="empty-history">No saved diagrams yet.</div>';
      return;
    }
    elements.history.innerHTML = "";
    for (const item of data.items) {
      const row = document.createElement("div");
      row.className = "history-item";
      row.innerHTML = `<div class="history-main"><div class="history-name">${escapeText(item.name)}</div><div class="history-meta">${escapeText(labelForType(item.diagram_type))} · ${escapeText(item.created_at)}</div></div><button class="history-load" type="button">Open</button>`;
      row.querySelector(".history-load").addEventListener("click", () => openHistory(item.id));
      elements.history.appendChild(row);
    }
  } catch (error) {
    elements.history.innerHTML = `<div class="empty-history">${escapeText(error.message)}</div>`;
  }
}

async function openHistory(id) {
  try {
    const data = await requestJson(`/api/diagrams/${id}`);
    currentDiagram = data.diagram;
    currentSvg = data.svg;
    elements.name.value = currentDiagram.name;
    elements.type.value = currentDiagram.diagram_type;
    renderSvg();
    addMessage(`Opened <strong>${escapeText(currentDiagram.name)}</strong>.`);
  } catch (error) {
    addMessage(escapeText(error.message));
  }
}

function setZoom(value) {
  zoom = Math.min(2, Math.max(0.5, value));
  const svg = elements.stage.querySelector("svg");
  if (svg) svg.style.transform = `scale(${zoom})`;
  elements.zoomReset.textContent = `${Math.round(zoom * 100)}%`;
}

elements.theme.addEventListener("click", cycleTheme);
elements.generate.addEventListener("click", generateDiagram);
elements.sendCommand.addEventListener("click", sendCommand);
elements.command.addEventListener("keydown", event => {
  if (event.key === "Enter") {
    event.preventDefault();
    sendCommand();
  }
});
elements.save.addEventListener("click", saveCurrentDiagram);
elements.copy.addEventListener("click", copyPng);
elements.export.addEventListener("click", exportDiagram);
elements.refreshHistory.addEventListener("click", loadHistory);
elements.zoomOut.addEventListener("click", () => setZoom(zoom - 0.1));
elements.zoomIn.addEventListener("click", () => setZoom(zoom + 0.1));
elements.zoomReset.addEventListener("click", () => setZoom(1));

document.querySelectorAll(".chip").forEach(chip => {
  chip.addEventListener("click", () => {
    elements.prompt.value = chip.dataset.example || "";
    elements.prompt.focus();
  });
});

setTheme(activeTheme);
loadHistory();
