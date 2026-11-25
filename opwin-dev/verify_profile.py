import os
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "App.tsx"), "r", encoding="utf-8") as f:
    content = f.read()
print('profile state:', 'profile' in content)
print('setProfile(true):', 'setProfile(true)' in content)
print('profile page:', '{profile && (' in content)
print('tool-grid:', 'tool-grid' in content)
print('tool-card:', 'tool-card' in content)
print('Owner option removed:', 'option value="owner"' not in content)
print('Customer option:', 'option value="customer"' in content)
