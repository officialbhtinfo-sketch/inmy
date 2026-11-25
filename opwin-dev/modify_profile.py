import os
import sys
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "App.tsx")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Step 1: Remove the "Owner" option from the role select
old_role = '<div className="auth-field"><label>Role</label><select name="role"><option value="customer">Customer</option><option value="owner">Owner</option></select></div>'
new_role = '<div className="auth-field"><label>Role</label><select name="role"><option value="customer">Customer</option></select></div>'
content = content.replace(old_role, new_role, 1)
print("Step 1 done")

# Step 2: Add profile state after chatLoading state
old_state = "const [chatLoading, setChatLoading] = useState(false);"
new_state = old_state + "\n  const [profile, setProfile] = useState(false);"
content = content.replace(old_state, new_state, 1)
print("Step 2 done")

# Step 3: After successful registration, set profile to true
old_register_end = 'const data = await res.json();\n      setUser(data);\n      setAuthModal(false);\n      return data;'
new_register_end = 'const data = await res.json();\n      setUser(data);\n      setAuthModal(false);\n      setProfile(true);\n      return data;'
content = content.replace(old_register_end, new_register_end, 1)
print("Step 3 done")

# Step 4: Add profile page view before the auth modal
old_auth_modal = '      {authModal && ('
profile_page = """      {profile && (
        <div className="auth-modal-overlay" onClick={() => setProfile(false)}>
          <div className="auth-modal" onClick={e => e.stopPropagation()}>
            <button className="auth-close" onClick={() => setProfile(false)}>×</button>
            <h2>Your Profile</h2>
            <div className="profile-content">
              <p className="profile-anon">Keeping you anonymous.</p>
              <h3>Free Cybersecurity Tools</h3>
              <div className="tool-grid">
                <div className="tool-card">
                  <h4>DNS Leak Test</h4>
                  <p>Check if your DNS requests are leaking outside your VPN.</p>
                  <button className="primary-button" disabled>Run Test</button>
                </div>
                <div className="tool-card">
                  <h4>What's My IP?</h4>
                  <p>See your public IP address and location.</p>
                  <button className="primary-button" disabled>Check IP</button>
                </div>
                <div className="tool-card">
                  <h4>Background Check Removal</h4>
                  <p>Request removal of your info from background check websites.</p>
                  <button className="primary-button" disabled>Start Removal</button>
                </div>
              </div>
              <p className="profile-note">More tools coming soon. All tools are free and run through secure APIs.</p>
            </div>
            <button className="primary-button" onClick={() => setProfile(false)}>Close</button>
          </div>
        </div>
      )}
      {authModal && ("""
content = content.replace(old_auth_modal, profile_page, 1)
print("Step 4 done")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("All done. File length:", len(content), "chars")
