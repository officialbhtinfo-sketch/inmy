import requests
from .. import config

def web_search(query: str) -> str:
    """Web search via Tavily. Returns numbered results with URL + snippet."""
    r = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {config.CFG.get('tavily_api_key', '')}"},
        json={"query": query, "search_depth": "basic", "max_results": 5},
        timeout=30,
    )
    if r.status_code == 401:
        return "Tavily API key missing or invalid - set tavily_api_key in config.yaml."
    r.raise_for_status()
    results = r.json().get("results", [])
    if not results:
        return f"No results for: {query}"
    return "\n\n".join(
        f"{i}. {x['title']}\n   URL: {x['url']}\n   {x.get('content', '').strip()[:400]}"
        for i, x in enumerate(results, 1)
    )