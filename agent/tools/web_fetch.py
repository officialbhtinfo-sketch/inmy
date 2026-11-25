import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

def web_fetch(url: str) -> str:
    """Read a web page. Tries the lightweight Jina reader first,
    falls back to a real headless browser for JS-heavy pages."""
    try:
        r = requests.get(f"https://r.jina.ai/{url}", headers={"User-Agent": UA}, timeout=60)
        r.raise_for_status()
        text = r.text.strip()
        if len(text) < 200:
            raise RuntimeError("page returned almost nothing (likely JS-rendered)")
        return text[:12000]
    except Exception as e:
        return _browser_fetch(url, str(e))

def _browser_fetch(url: str, why: str) -> str:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return (f"Fetch failed ({why}). For JS-heavy pages run: "
                "pip install playwright && playwright install chromium")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=UA)
            page.goto(url, wait_until="networkidle", timeout=45000)
            text = page.inner_text("body")
            browser.close()
        return text.strip()[:12000] or "(page rendered but had no text)"
    except Exception as e2:
        return f"Fetch failed ({why}); browser fallback also failed: {e2}"