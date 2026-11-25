import os
import sys
html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Opwin.io Chatbot Test</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }
  .container { max-width: 600px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 1.5rem; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5); }
  h1 { color: #38bdf8; margin-bottom: 1rem; font-size: 1.5rem; }
  .chat-log { height: 300px; overflow-y: auto; border: 1px solid #334155; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; background: #0f172a; }
  .bubble { margin: 0.5rem 0; padding: 0.75rem 1rem; border-radius: 8px; max-width: 85%; line-height: 1.4; }
  .bubble.you { background: #38bdf8; color: #0f172a; margin-left: auto; text-align: right; }
  .bubble.assistant { background: #334155; color: #e2e8f0; }
  .input-area { display: flex; gap: 0.5rem; }
  input[type="text"] { flex: 1; padding: 0.75rem; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #e2e8f0; }
  button { padding: 0.75rem 1.5rem; border-radius: 6px; border: none; background: #38bdf8; color: #0f172a; font-weight: 600; cursor: pointer; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  .status { margin-top: 0.75rem; font-size: 0.85rem; color: #94a3b8; }
  .status.loading { color: #38bdf8; font-weight: 600; }
  .suggestions { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
  .sugg-btn { padding: 0.5rem 1rem; border-radius: 6px; border: 1px solid #475569; background: #1e293b; color: #e2e8f0; cursor: pointer; font-size: 0.9rem; }
  .sugg-btn:hover { border-color: #38bdf8; }
</style>
</head>
<body>
<div class="container">
  <h1>🤖 Opwin.io FAQ Assistant (Test)</h1>
  <p>Testing local LLM at <code>http://127.0.0.1:9931/v1/chat/completions</code></p>
  
  <div class="suggestions" id="suggestions">
    <button class="sugg-btn" onclick="askSuggestion('What does it cost?')">What does it cost?</button>
    <button class="sugg-btn" onclick="askSuggestion('How does a consultation work?')">How does a consultation work?</button>
    <button class="sugg-btn" onclick="askSuggestion('Outside California?')">Outside California?</button>
    <button class="sugg-btn" onclick="askSuggestion('Bitcoin payments?')">Bitcoin payments?</button>
  </div>

  <div class="chat-log" id="chatLog">
    <div class="bubble assistant">Hi. I can help with pricing, service area, and how consultations work. What would you like to know?</div>
  </div>

  <div class="input-area">
    <input type="text" id="questionInput" placeholder="Ask a quick question…" maxlength="300">
    <button id="sendBtn" onclick="sendQuestion()">Send</button>
  </div>
  <div class="status" id="status"></div>
</div>

<script>
const API_BASE = "http://127.0.0.1:9931/v1";
const chatLog = document.getElementById("chatLog");
const questionInput = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");
const status = document.getElementById("status");

function addBubble(role, text) {
  const div = document.createElement("div");
  div.className = "bubble " + role;
  div.textContent = text;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function setLoading(loading) {
  sendBtn.disabled = loading;
  status.textContent = loading ? "Thinking..." : "";
  status.className = loading ? "status loading" : "status";
}

async function answer(q) {
  addBubble("you", q);
  questionInput.value = "";
  setLoading(true);
  try {
    const res = await fetch(`${API_BASE}/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "local",
        messages: [
          { role: "system", content: "You are a fun, entertaining chatbot on Opwin.io. You are helpful but playful and conversational, not overly formal or rule-bound. You can talk about cybersecurity, audio/video setup, surveillance cameras, AI, virtual assistants, and consultations. Keep answers short and lively. Do not claim you can book appointments or process payments." },
          { role: "user", content: q }
        ],
        temperature: 0.7,
        max_tokens: 500,
      }),
    });
    if (!res.ok) throw new Error("LLM error: " + res.status);
    const data = await res.json();
    const reply = data.choices?.[0]?.message?.content || "Sorry, I didn't get a response.";
    addBubble("assistant", reply);
  } catch (e) {
    addBubble("assistant", "Having trouble connecting to my brain right now. Try again in a moment!");
    console.error(e);
  } finally {
    setLoading(false);
  }
}

function sendQuestion() {
  const q = questionInput.value.trim();
  if (!q) return;
  answer(q);
}

function askSuggestion(q) {
  answer(q);
}

questionInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendQuestion();
});
</script>
</body>
</html>"""

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_chat.html'), 'w', encoding='utf-8') as f:
    f.write(html)
print('Test page created successfully')
