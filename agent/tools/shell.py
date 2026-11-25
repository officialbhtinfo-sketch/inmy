import platform
import subprocess

def shell(command: str) -> str:
    """Run a command via PowerShell (Windows) or sh (elsewhere). Returns combined output."""
    if platform.system() == "Windows":
        # PowerShell 5.1 otherwise writes redirected output in a legacy code page.
        prefix = "[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false); "
        cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", prefix + command]
    else:
        cmd = ["sh", "-c", command]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120)
    except subprocess.TimeoutExpired:
        return "Command timed out after 120 seconds."
    out = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    if err:
        out = (out + "\n[stderr]\n" + err).strip()
    return out[:12000] or f"(no output, exit code {p.returncode})"

def needs_approval(command: str, allowlist) -> bool:
    """True if the command's first token isn't on the read-only allowlist."""
    tokens = command.strip().split(maxsplit=1)
    if not tokens:
        return True
    head = tokens[0].lower().lstrip(".\\")
    return head not in {a.lower() for a in (allowlist or [])}
