import os
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "App.tsx")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove the descriptions object from its current location (inside JSX)
descriptions_block = """      const serviceAreaDescriptions: Record<string, string> = {
        web: "Full stack web development: I build end-to-end web applications — frontend, backend, databases, and deployment. From concept to production, I handle the full stack.",
        cyber: "Cyber security: I secure networks, harden systems, and protect data against threats. Risk assessment, penetration testing, and incident response.",
        av: "Audio video solutions: I install and configure surveillance camera systems, audio setups, and video streaming infrastructure. Getting your gear online and working.",
        ai: "Local AI: I deploy and run local AI models — chatbots, assistants, and automation — on your own hardware. Private, offline, and under your control.",
      };

"""
content = content.replace(descriptions_block, '')
print('Removed descriptions from JSX')

# Find the return statement and insert descriptions before it
return_idx = content.find("return (")
if return_idx < 0:
    print("ERROR: return statement not found")
else:
    descriptions = """      const serviceAreaDescriptions: Record<string, string> = {
        web: "Full stack web development: I build end-to-end web applications — frontend, backend, databases, and deployment. From concept to production, I handle the full stack.",
        cyber: "Cyber security: I secure networks, harden systems, and protect data against threats. Risk assessment, penetration testing, and incident response.",
        av: "Audio video solutions: I install and configure surveillance camera systems, audio setups, and video streaming infrastructure. Getting your gear online and working.",
        ai: "Local AI: I deploy and run local AI models — chatbots, assistants, and automation — on your own hardware. Private, offline, and under your control.",
      };

"""
    content = content[:return_idx] + descriptions + content[return_idx:]
    print("Inserted descriptions before return")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
