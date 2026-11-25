import sys
path = r"C:\Users\ActOnline\Documents\Agent-Nemo\opwin-dev\App.tsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Step 1: Add serviceArea state after existing useState declarations
# Find the line with "const [chat, setChat] = useState(false);"
old_chat_state = "const [chat, setChat] = useState(false);"
new_chat_state = old_chat_state + "\n  const [serviceArea, setServiceArea] = useState<string | null>(null);"
content = content.replace(old_chat_state, new_chat_state, 1)
print("Step 1 done")

# Step 2: Add service areas dropdown in the header, after the phone number link
# Find the phone number link in the header
old_phone = '<a href="sms:+12528763008" data-testid="link-text-header">Text 252-876-3008 <ArrowUpRight size={15} /></a>'
new_dropdown = old_phone + '''
          <div className="service-dropdown" data-testid="service-dropdown">
            <label htmlFor="service-area-select">Service areas</label>
            <select id="service-area-select" onChange={e => setServiceArea(e.target.value || null)}>
              <option value="">Select a service area</option>
              <option value="web">Full stack web development</option>
              <option value="cyber">Cyber security</option>
              <option value="av">Audio video solutions</option>
              <option value="ai">Local AI</option>
            </select>
          </div>'''
content = content.replace(old_phone, new_dropdown, 1)
print("Step 2 done")

# Step 3: Add service area descriptions and conditional rendering
# Find the booking card section start and add conditional content before it
old_booking = '<section className="booking-card" ref={booking} aria-labelledby="booking-title">'
new_conditional = '''          {serviceArea && (
            <section className="service-area-view" aria-labelledby="service-area-title">
              <div className="wrap">
                <button onClick={() => setServiceArea(null)} className="close-service" aria-label="Close service area" data-testid="button-close-service">✕</button>
                <h2 id="service-area-title">Service area details</h2>
                <p>{serviceAreaDescriptions[serviceArea]}</p>
              </div>
            </section>
          )}
          {!serviceArea && ('''
content = content.replace(old_booking, new_conditional, 1)
print("Step 3 done")

# Step 4: Close the conditional and add descriptions
# Find the end of the App component's return and add descriptions before it
# We need to add the descriptions object and close the conditional
old_return_end = '      {authModal && ('
new_descriptions = '''      }

      const serviceAreaDescriptions: Record<string, string> = {
        web: "Full stack web development: I build end-to-end web applications — frontend, backend, databases, and deployment. From concept to production, I handle the full stack.",
        cyber: "Cyber security: I secure networks, harden systems, and protect data against threats. Risk assessment, penetration testing, and incident response.",
        av: "Audio video solutions: I install and configure surveillance camera systems, audio setups, and video streaming infrastructure. Getting your gear online and working.",
        ai: "Local AI: I deploy and run local AI models — chatbots, assistants, and automation — on your own hardware. Private, offline, and under your control.",
      };

      {authModal && ('''
content = content.replace(old_return_end, new_descriptions, 1)
print("Step 4 done")

# Step 5: Close the conditional div after the booking card section
# Find the closing of the booking card section and add the closing of the conditional
# The booking card section ends with </section> followed by the FAQ section
# We need to add } after the booking card's closing section tag
old_faq_section = '          <section className="faq-section" aria-labelledby="faq-title">'
new_close_conditional = '''          )}
          <section className="faq-section" aria-labelledby="faq-title">'''
content = content.replace(old_faq_section, new_close_conditional, 1)
print("Step 5 done")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("All done. File length:", len(content), "chars")
