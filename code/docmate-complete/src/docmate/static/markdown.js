// A tiny, safe Markdown renderer: enough for chat answers.
// Everything is escaped first, so the model can never inject HTML into the page.

const escape = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

function inline(text) {
  return escape(text)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\[(\d+)\]/g, '<sup class="cite">[$1]</sup>');
}

function codeBlock(part) {
  const lines = part.split("\n");
  lines.shift(); // the language name after ```
  const code = escape(lines.join("\n").replace(/\n$/, ""));
  return `<pre><button class="copy">Copy</button><code>${code}</code></pre>`;
}

function blocks(part) {
  let html = "";
  let list = null; // "ul" or "ol" while we are inside a list
  for (const line of part.split("\n")) {
    const bullet = line.match(/^\s*[-*] (.*)/);
    const numbered = line.match(/^\s*\d+\. (.*)/);
    const kind = bullet ? "ul" : numbered ? "ol" : null;
    if (list && kind !== list) { html += `</${list}>`; list = null; }
    if (kind) {
      if (!list) { html += `<${kind}>`; list = kind; }
      html += `<li>${inline((bullet || numbered)[1])}</li>`;
    } else if (/^\s*[=-]{3,}\s*$/.test(line)) {
      // a line of === or --- underlines a heading, or is a divider: show a line
      html += "<hr>";
    } else if (line.startsWith("#")) {
      html += `<p><strong>${inline(line.replace(/^#+\s*/, ""))}</strong></p>`;
    } else if (line.trim()) {
      html += `<p>${inline(line)}</p>`;
    }
  }
  return list ? html + `</${list}>` : html;
}

export function renderMarkdown(text) {
  // Split on ``` : even parts are normal text, odd parts are code blocks.
  return text.split("```").map((part, i) => (i % 2 ? codeBlock(part) : blocks(part))).join("");
}
