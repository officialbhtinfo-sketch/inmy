import base64
import io

def screenshot() -> dict:
    """Capture the primary monitor. Returns {'w', 'h', 'b64'} -
    the loop attaches the image so your vision model can see it."""
    import pyautogui
    img = pyautogui.screenshot()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return {"w": img.width, "h": img.height,
            "b64": base64.b64encode(buf.getvalue()).decode("ascii")}