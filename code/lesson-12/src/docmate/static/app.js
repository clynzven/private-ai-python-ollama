import { renderMarkdown } from "/markdown.js";

const $ = (id) => document.getElementById(id);
let chatId = null;
let controller = null; // lets the Stop button cancel the answer

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
  return response.json();
}

function toast(text) {
  $("toast").textContent = text;
  $("toast").hidden = false;
  setTimeout(() => ($("toast").hidden = true), 2500);
}

// ---------- sidebar
async function loadChats() {
  const chats = await api("/api/chats");
  $("chats").innerHTML = "";
  for (const chat of chats) {
    const item = document.createElement("div");
    item.className = "chat-item" + (chat.id === chatId ? " active" : "");
    item.innerHTML = `<span></span><button title="Delete">✕</button>`;
    item.querySelector("span").textContent = chat.title;
    item.onclick = () => openChat(chat.id);
    item.querySelector("button").onclick = async (event) => {
      event.stopPropagation();
      await api(`/api/chats/${chat.id}`, { method: "DELETE" });
      if (chat.id === chatId) newChat();
      loadChats();
    };
    $("chats").append(item);
  }
}

async function loadDocuments() {
  const docs = await api("/api/documents");
  $("doc-list").innerHTML = docs.map((d) => `<li></li>`).join("");
  [...$("doc-list").children].forEach((li, i) => (li.textContent = docs[i]));
}

async function loadModels() {
  const models = (await api("/api/models")).filter((m) => !m.includes("embed"));
  $("model").innerHTML = "";
  for (const m of models) $("model").add(new Option(m, m));
}

// ---------- messages
function addMessage(role, content = "", sources = []) {
  $("empty").hidden = true;
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  if (role === "user") div.textContent = content;
  else div.innerHTML = `<div class="body"></div><div class="sources"></div>`;
  $("messages").append(div);
  if (role === "assistant") {
    setAnswer(div, content);
    showSources(div, sources);
  }
  return div;
}

function setAnswer(div, text) {
  div.querySelector(".body").innerHTML = renderMarkdown(text);
}

function showSources(div, sources) {
  div.querySelector(".sources").innerHTML = "";
  for (const s of sources) {
    const chip = document.createElement("span");
    chip.className = "source";
    chip.textContent = `[${s.n}] ${s.source}`;
    div.querySelector(".sources").append(chip);
  }
}

function newChat() {
  chatId = null;
  $("messages").querySelectorAll(".msg").forEach((m) => m.remove());
  $("empty").hidden = false;
  loadChats();
}

async function openChat(id) {
  chatId = id;
  $("messages").querySelectorAll(".msg").forEach((m) => m.remove());
  for (const m of await api(`/api/chats/${id}`)) addMessage(m.role, m.content, m.sources);
  loadChats();
}

async function send(text) {
  if (chatId === null) chatId = (await api("/api/chats", { method: "POST" })).id;
  addMessage("user", text);
  const answer = addMessage("assistant");
  answer.querySelector(".body").classList.add("cursor");
  $("send").hidden = true;
  $("stop").hidden = false;
  controller = new AbortController();
  let text_so_far = "";
  try {
    const response = await fetch(`/api/chats/${chatId}/messages`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ content: text, model: $("model").value, use_docs: $("use-docs").checked }),
      signal: controller.signal,
    });
    if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
    // Read the stream line by line: every line is one JSON event.
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop(); // keep a half-received line for later
      for (const line of lines.filter(Boolean)) {
        const event = JSON.parse(line);
        if (event.type === "token") {
          text_so_far += event.text;
          setAnswer(answer, text_so_far);
          answer.scrollIntoView({ block: "end" });
        } else if (event.type === "sources") {
          showSources(answer, event.sources);
        } else if (event.type === "error") {
          toast(`DocMate could not answer: ${event.message}`);
        }
      }
    }
  } catch (error) {
    if (error.name !== "AbortError") toast(`Something went wrong: ${error.message}`);
  } finally {
    answer.querySelector(".body").classList.remove("cursor");
    $("send").hidden = false;
    $("stop").hidden = true;
    loadChats();
  }
}

// ---------- documents: button and drag-and-drop
async function upload(file) {
  const form = new FormData();
  form.append("file", file);
  try {
    const counts = await api("/api/documents", { method: "POST", body: form });
    toast(`Added ${file.name} (added ${counts.added}, updated ${counts.updated})`);
  } catch (error) {
    toast(`Could not add ${file.name}: ${error.message}`);
  }
  loadDocuments();
}

$("file").onchange = () => $("file").files[0] && upload($("file").files[0]);
document.addEventListener("dragover", (e) => { e.preventDefault(); document.body.classList.add("dragging"); });
document.addEventListener("dragleave", (e) => { if (!e.relatedTarget) document.body.classList.remove("dragging"); });
document.addEventListener("drop", (e) => {
  e.preventDefault();
  document.body.classList.remove("dragging");
  for (const file of e.dataTransfer.files) upload(file);
});

// ---------- wiring
$("ask").onsubmit = (e) => {
  e.preventDefault();
  const text = $("input").value.trim();
  if (!text || !$("stop").hidden) return; // ignore while an answer is still coming
  $("input").value = "";
  send(text);
};
$("input").onkeydown = (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("ask").requestSubmit(); }
};
$("stop").onclick = () => controller?.abort();
$("new-chat").onclick = newChat;
$("messages").onclick = (e) => {
  if (!e.target.classList.contains("copy")) return;
  navigator.clipboard.writeText(e.target.nextElementSibling.textContent);
  e.target.textContent = "Copied";
};

loadModels();
loadChats();
loadDocuments();
