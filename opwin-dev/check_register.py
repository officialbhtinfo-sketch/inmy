with open(r"C:\Users\ActOnline\Documents\Agent-Nemo\opwin-dev\App.tsx", "r", encoding="utf-8") as f:
    content = f.read()
idx = content.find("const register =")
if idx >= 0:
    print(content[idx:idx+800])
