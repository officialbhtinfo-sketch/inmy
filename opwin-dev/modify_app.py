import sys
path = r"C:\Users\ActOnline\Documents\Agent-Nemo\opwin-dev\App.tsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Step 1: Add LLM_API_BASE after faqs array
marker = "\n\nexport default function App()"
idx = content.find(marker)
if idx < 0:
    print("ERROR: marker not found")
    sys.exit(1)
llm = "\n// LLM endpoint for the fun chatbot. Points to the local llama-server on this\n// machine during testing; switch to the Mac's IP when deployed.\nconst LLM_API_BASE = \"http://127.0.0.1:9931/v1\";\n\n"
content = content[:idx] + llm + content[idx:]
print("Step 1 done")

# Step 2: Add chatLoading state
content = content.replace("const [chat, setChat] = useState(false);", "const [chat, setChat] = useState(false);\n  const [chatLoading, setChatLoading] = useState(false);")
print("Step 2 done")

# Step 3: Replace answer() function
start = content.find("const answer = (q: string) => {")
end_marker = "    setQuestion(\"\");\n  };"
end = content.find(end_marker, start) + len(end_marker)
if start < 0 or end <= start:
    print("ERROR: answer function not found")
    sys.exit(1)
new_answer = '''const answer = async (q: string) => {
    setChatItems(prev => [...prev, { role: "you", text: q.slice(0, 300) }]);
    setQuestion("");
    setChatLoading(true);
    try {
      const res = await fetch(`${LLM_API_BASE}/chat/completions`, {
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
      if (!res.ok) throw new Error(`LLM error: ${res.status}`);
      const data = await res.json();
      const reply = data.choices?.[0]?.message?.content || "Sorry, I didn't get a response.";
      setChatItems(prev => [...prev, { role: "assistant", text: reply }]);
    } catch (e: any) {
      setChatItems(prev => [...prev, { role: "assistant", text: "Having trouble connecting to my brain right now. Try again in a moment!" }]);
      console.error(e);
    } finally {
      setChatLoading(false);
    }
  };'''
content = content[:start] + new_answer + content[end:]
print("Step 3 done")

# Step 4: Add loading bubble
old_log = "{chatItems.map((item, i) => ("
new_log = """            {chatLoading && (
              <div className="bubble assistant">Thinking...</div>
            )}
            {chatItems.map((item, i) => ("""
content = content.replace(old_log, new_log)
print("Step 4 done")

# Step 5: Update disclaimer
content = content.replace('<p className="chat-disclaimer">Automated FAQ, not a live chat. No messages are sent.</p>', '<p className="chat-disclaimer">Powered by a local AI. Fun, not official. No messages are stored.</p>')
print("Step 5 done")

# Step 6: Add specialties section before booking card
bc_start = content.find('<section className="booking-card"')
if bc_start < 0:
    print("ERROR: booking card not found")
    sys.exit(1)
specialties = """          <section className="specialties" aria-labelledby="specialties-title">
            <div className="wrap">
              <span className="eyebrow">WHAT WE DO</span>
              <h2 id="specialties-title">Our specialties.</h2>
              <p className="specialties-intro">Opwin.io focuses on three areas where tech meets real life:</p>
              <div className="specialty-grid">
                <article className="specialty-card">
                  <div className="specialty-icon">🔒</div>
                  <h3>Cybersecurity</h3>
                  <p>Locking down your devices, networks, and data so you can work without worry.</p>
                </article>
                <article className="specialty-card">
                  <div className="specialty-icon">📹</div>
                  <h3>Audio & Video</h3>
                  <p>Setting up security cameras, surveillance systems, and video streaming — getting your gear online and working.</p>
                </article>
                <article className="specialty-card">
                  <div className="specialty-icon">🤖</div>
                  <h3>AI & Virtual Assistants</h3>
                  <p>Local AI chatbots, automation, and virtual assistant setup that actually works for you.</p>
                </article>
              </div>
            </div>
          </section>

"""
content = content[:bc_start] + specialties + content[bc_start:]
print("Step 6 done")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("All done. File length:", len(content), "chars")
