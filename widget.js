(function () {
  const BACKEND_URL = "https://omni-agent-engine.onrender.com/chat"; // Yahan Step 4 ka URL paste karein

  let chatHistory = [];

  // Inject Widget Styles and HTML
  const container = document.createElement("div");
  container.innerHTML = `
    <style>
      #omni-bubble { position: fixed; bottom: 24px; right: 24px; background: #0F172A; color: #fff; width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 10px 25px rgba(0,0,0,0.3); z-index: 99999; transition: transform 0.2s; font-size: 24px; }
      #omni-bubble:hover { transform: scale(1.08); }
      #omni-box { display: none; position: fixed; bottom: 90px; right: 24px; width: 360px; height: 500px; background: #ffffff; border-radius: 16px; box-shadow: 0 12px 36px rgba(0,0,0,0.25); flex-direction: column; overflow: hidden; z-index: 99999; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; border: 1px solid #e2e8f0; }
      #omni-header { background: #0F172A; color: #fff; padding: 14px 18px; font-weight: 600; display: flex; justify-content: space-between; align-items: center; }
      #omni-logs { flex: 1; padding: 14px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; background: #F8FAFC; }
      .omni-msg { padding: 8px 12px; border-radius: 10px; font-size: 13.5px; line-height: 1.4; max-width: 80%; word-break: break-word; }
      .omni-user { align-self: flex-end; background: #2563EB; color: #fff; }
      .omni-bot { align-self: flex-start; background: #E2E8F0; color: #0F172A; }
      #omni-input-row { padding: 10px; background: #fff; border-top: 1px solid #E2E8F0; display: flex; gap: 6px; }
      #omni-input { flex: 1; padding: 8px 12px; border: 1px solid #CBD5E1; border-radius: 8px; outline: none; font-size: 13px; }
      #omni-input:focus { border-color: #2563EB; }
      #omni-send { background: #2563EB; color: #fff; border: none; padding: 8px 14px; border-radius: 8px; cursor: pointer; font-weight: 600; }
      #omni-badge { font-size: 10px; text-align: center; color: #94A3B8; padding-bottom: 4px; background: #fff; }
    </style>

    <div id="omni-bubble">⚡</div>

    <div id="omni-box">
      <div id="omni-header">
        <span>OmniAgent AI</span>
        <span style="cursor:pointer;font-size:18px;" id="omni-close">×</span>
      </div>
      <div id="omni-logs">
        <div class="omni-msg omni-bot">Hello! How can I assist you with our services today?</div>
      </div>
      <div id="omni-input-row">
        <input type="text" id="omni-input" placeholder="Type a message..." autocomplete="off">
        <button id="omni-send">Send</button>
      </div>
      <div id="omni-badge">Powered by Sinha AI Tech Solutions</div>
    </div>
  `;
  document.body.appendChild(container);

  const bubble = document.getElementById("omni-bubble");
  const box = document.getElementById("omni-box");
  const closeBtn = document.getElementById("omni-close");
  const sendBtn = document.getElementById("omni-send");
  const input = document.getElementById("omni-input");
  const logs = document.getElementById("omni-logs");

  bubble.onclick = () => { box.style.display = box.style.display === "flex" ? "none" : "flex"; };
  closeBtn.onclick = () => { box.style.display = "none"; };

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    logs.innerHTML += `<div class="omni-msg omni-user">${text}</div>`;
    input.value = "";
    logs.scrollTop = logs.scrollHeight;

    chatHistory.push({ role: "user", content: text });

    try {
      const res = await fetch(BACKEND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ history: chatHistory, message: text }),
      });
      const data = await res.json();
      logs.innerHTML += `<div class="omni-msg omni-bot">${data.reply}</div>`;
      chatHistory.push({ role: "assistant", content: data.reply });
      logs.scrollTop = logs.scrollHeight;
    } catch (err) {
      logs.innerHTML += `<div class="omni-msg omni-bot" style="color:red;">Error connecting to OmniAgent server.</div>`;
    }
  }

  sendBtn.onclick = sendMessage;
  input.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMessage(); });
})();
