import os
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "App.tsx"), "r", encoding="utf-8") as f:
    content = f.read()
print('setProfile(true):', 'setProfile(true)' in content)
print('Owner option removed:', 'option value="owner"' not in content)
print('profile page:', '{profile && (' in content)
print('tool-grid:', 'tool-grid' in content)
