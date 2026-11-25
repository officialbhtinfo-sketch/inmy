import os
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "App.tsx"), "r", encoding="utf-8") as f:
    content = f.read()
idx = content.find("const register =")
if idx >= 0:
    print(content[idx:idx+800])
