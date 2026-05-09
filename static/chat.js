(() => {
  const messagesEl = document.getElementById("messages");
  const composer = document.getElementById("composer");
  const input = document.getElementById("input");
  const sendBtn = document.getElementById("send");

  if (!messagesEl || !composer || !input || !sendBtn) return;

  const placeholder = messagesEl.querySelector(".bubble.placeholder");

  function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function addBubble(role, text) {
    const div = document.createElement("div");
    div.className = "bubble " + role;
    div.textContent = text;
    messagesEl.appendChild(div);
    scrollToBottom();
    return div;
  }

  async function send(message) {
    if (placeholder) placeholder.remove();
    addBubble("user", message);
    const assistantBubble = addBubble("assistant", "");
    let started = false;
    sendBtn.disabled = true;
    input.disabled = true;

    try {
      const res = await fetch("/chat/send", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      if (!res.ok || !res.body) {
        assistantBubble.classList.add("error");
        assistantBubble.textContent = "Request failed (HTTP " + res.status + ").";
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let acc = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";
        for (const rawLine of lines) {
          const line = rawLine.trimEnd();
          if (!line.startsWith("data:")) continue;
          const payload = line.slice(5).trim();
          if (payload === "[DONE]") return;
          try {
            const event = JSON.parse(payload);
            if (event.type === "delta" && typeof event.text === "string") {
              acc += event.text;
              assistantBubble.textContent = acc;
              started = true;
              scrollToBottom();
            } else if (event.type === "error") {
              assistantBubble.classList.add("error");
              assistantBubble.textContent = event.message || "Unknown error.";
              return;
            }
          } catch (_) {
            // ignore malformed frame
          }
        }
      }

      if (!started) {
        assistantBubble.classList.add("error");
        assistantBubble.textContent = "No response received.";
      }
    } catch (err) {
      assistantBubble.classList.add("error");
      assistantBubble.textContent = "Network error: " + (err?.message || err);
    } finally {
      sendBtn.disabled = false;
      input.disabled = false;
      input.focus();
    }
  }

  composer.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    send(text);
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      composer.requestSubmit();
    }
  });

  input.focus();
})();
