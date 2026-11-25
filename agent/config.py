# app_config.py  (or wherever your init() lives)
import os
import yaml

CFG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")

CFG: dict = {}


def init(path: str = CFG_PATH) -> dict:
    """Load the config file beside main.py by default.

    TAVILY_API_KEY env var overrides the value in the file.
    """
    global CFG

    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        CFG = yaml.safe_load(f) or {}

    env_key = os.environ.get("TAVILY_API_KEY")
    if env_key:
        CFG["tavily_api_key"] = env_key

    return CFG