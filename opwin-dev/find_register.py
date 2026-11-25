with open(r"C:\Users\ActOnline\Documents\Agent-Nemo\opwin-dev\App.tsx", "r", encoding="utf-8") as f:
    content = f.read()
# Find the registration form
idx = content.find("authMode === \"register\"")
if idx >= 0:
    print(content[idx:idx+2500])
else:
    print("authMode === \"register\" not found")
    # Try to find the register form differently
    idx2 = content.find("Create account")
    if idx2 >= 0:
        print(content[idx2-200:idx2+1500])
