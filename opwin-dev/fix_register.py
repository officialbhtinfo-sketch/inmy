import os
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "App.tsx")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the registration success path
old = "      const data = await res.json();\n      setUser(data);\n      setAuthModal(false);\n      return data;"
new = "      const data = await res.json();\n      setUser(data);\n      setAuthModal(false);\n      setProfile(true);\n      return data;"
if old in content:
    content = content.replace(old, new, 1)
    print("Fixed registration success path")
else:
    print("Pattern not found, searching for alternative...")
    # Try with different indentation
    import re
    pattern = r"(const data = await res\.json\(\);[\s\S]*?setUser\(data\);[\s\S]*?setAuthModal\(false\);[\s\S]*?return data;)"
    match = re.search(pattern, content)
    if match:
        old_block = match.group(1)
        new_block = old_block.replace("setAuthModal(false);", "setAuthModal(false);\n      setProfile(true);")
        content = content.replace(old_block, new_block, 1)
        print("Fixed with regex")
    else:
        print("Could not find registration success path")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
