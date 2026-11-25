import sys
path = r"C:\Users\ActOnline\Documents\Agent-Nemo\opwin-dev\App.tsx"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Step 1: Add serviceArea state
old_chat_state = "const [chat, setChat] = useState(false);"
new_chat_state = old_chat_state + "\n  const [serviceArea, setServiceArea] = useState<string | null>(null);"
content = content.replace(old_chat_state, new_chat_state, 1)
print("Step 1 done")

# Step 2: Add dropdown in header after phone number
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

# Step 3: Wrap the booking card section with {!serviceArea && ( ... )}
# Find the start of the booking card section
booking_start = '<section className="booking-card" ref={booking} aria-labelledby="booking-title">'
booking_start_idx = content.find(booking_start)
if booking_start_idx < 0:
    print("ERROR: booking card start not found")
    sys.exit(1)

# Find the end of the booking card section - the </section> right before the FAQ section
faq_start = '<section className="faq-section" aria-labelledby="faq-title">'
faq_idx = content.find(faq_start)
if faq_idx < 0:
    print("ERROR: FAQ section not found")
    sys.exit(1)

# Find the last </section> before the FAQ section
booking_section_end = content.rfind('</section>', 0, faq_idx)
if booking_section_end < 0:
    print("ERROR: booking card end not found")
    sys.exit(1)
# The </section> tag is 9 chars long
booking_section_end_tag_end = booking_section_end + len('</section>')

# Wrap the booking card section
before_booking = content[:booking_start_idx]
booking_section = content[booking_start_idx:booking_section_end_tag_end]
after_booking = content[booking_section_end_tag_end:]

wrapped_booking = '{!serviceArea && (\n          ' + booking_section + '\n          )}'

content = before_booking + wrapped_booking + after_booking
print("Step 3 done")

# Step 4: Insert service area view before the wrapped booking card
service_area_view = '''          {serviceArea && (
            <section className="service-area-view" aria-labelledby="service-area-title">
              <div className="wrap">
                <button onClick={() => setServiceArea(null)} className="close-service" aria-label="Close service area" data-testid="button-close-service">✕</button>
                <h2 id="service-area-title">Service area details</h2>
                <p>{serviceAreaDescriptions[serviceArea]}</p>
              </div>
            </section>
          )}
'''

# Find the position of the wrapped booking card
wrapped_start = content.find('{!serviceArea && (')
content = content[:wrapped_start] + service_area_view + content[wrapped_start:]
print("Step 4 done")

# Step 5: Add descriptions object before authModal
old_auth = '      {authModal && ('
descriptions = '''      }

      const serviceAreaDescriptions: Record<string, string> = {
        web: "Full stack web development: I build end-to-end web applications — frontend, backend, databases, and deployment. From concept to production, I handle the full stack.",
        cyber: "Cyber security: I secure networks, harden systems, and protect data against threats. Risk assessment, penetration testing, and incident response.",
        av: "Audio video solutions: I install and configure surveillance camera systems, audio setups, and video streaming infrastructure. Getting your gear online and working.",
        ai: "Local AI: I deploy and run local AI models — chatbots, assistants, and automation — on your own hardware. Private, offline, and under your control.",
      };

      {authModal && ('''
content = content.replace(old_auth, descriptions, 1)
print("Step 5 done")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("All done. File length:", len(content), "chars")
