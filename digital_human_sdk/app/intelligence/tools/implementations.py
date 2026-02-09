import os
import requests
from dotenv import load_dotenv
load_dotenv()
import math
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re


def fetch_page_content(url: str, max_chars: int = 3000) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (DigitalHumanBot/1.0)"
        }
        r = requests.get(url, headers=headers, timeout=8)

        if r.status_code != 200:
            return ""

        soup = BeautifulSoup(r.text, "html.parser")

        # Remove scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ")
        text = re.sub(r"\s+", " ", text).strip()

        return text[:max_chars]

    except Exception:
        return ""
    
# ---------------- WEATHER ----------------
def weather_tool(params: dict):
    city = params.get("city")
    api_key = os.getenv("OPENWEATHER_API_KEY")
 
    if not api_key:
        return {"error": "OPENWEATHER_API_KEY not set"}
 
    url = "https://api.openweathermap.org/data/2.5/weather"
    r = requests.get(
        url,
        params={
            "q": city,
            "appid": api_key,
            "units": "metric"
        },
        timeout=10
    )
 
    return r.json()
 
 
# ---------------- BROWSER SEARCH (NO KEY) ----------------
def browser_tool(params: dict):
    url = params.get("url")
    query = params.get("query")

    # Case 1: URL is provided → fetch directly
    if url:
        content = fetch_page_content(url)
        return {
            "source": "url",
            "url": url,
            "content": content
        }

    # Case 2: Only query is provided → search + fetch
    if query:
        search_url = "https://duckduckgo.com/html/"
        r = requests.post(search_url, data={"q": query}, timeout=10)

        # very basic link extraction
        soup = BeautifulSoup(r.text, "html.parser")
        link = soup.find("a", href=True)

        if link:
            content = fetch_page_content(link["href"])
            return {
                "source": "search",
                "query": query,
                "content": content
            }

    return {"error": "No url or query provided"}

# ---------------- SERPAPI SEARCH ----------------
def serpapi_search_tool(params: dict):
    query = params.get("query")
    api_key = os.getenv("SERPAPI_API_KEY")


    if not api_key:
        return {"error": "SERPAPI_API_KEY not set"}


    r = requests.get(
        "https://serpapi.com/search.json",
        params={
            "q": query,
            "engine": "google",
            "api_key": api_key,
            "num": 10
        },
        timeout=10
    )


    data = r.json()

    enriched_results = []

    for item in data.get("organic_results", [])[:10]:
        link = item.get("link")
        content = fetch_page_content(link)

        enriched_results.append({
            "title": item.get("title"),
            "link": link,
            "snippet": item.get("snippet"),
            "content": content
        })

    return {
        "query": query,
        "results": enriched_results
    }


 
 
# ---------------- MATH ----------------
def math_tool(params: dict):
    expression = params.get("expression")
    try:
        result = eval(expression, {"__builtins__": {}})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

import os
import logging
import requests

from app.intelligence.utils.json_utils import safe_json_loads

logger = logging.getLogger("property_tool")

PROPERTY_SERVICE_URL = os.getenv(
    "PROPERTY_SERVICE_URL",
    "http://127.0.0.1:8000"
)

# --------------------------------------------------
# PAYLOAD NORMALIZER (LLM → BACKEND CONTRACT)
# --------------------------------------------------
def normalize_property_payload(payload: dict) -> dict:
    return {
        "title": payload.get("title"),
        "city": payload.get("city"),
        "locality": payload.get("locality"),
        "purpose": payload.get("purpose"),
        "price": payload.get("price"),
        "bhk": payload.get("bhk"),
        "area_sqft": payload.get("area_sqft"),
        "is_legal": payload.get("is_legal"),
        "owner_name": payload.get("owner_name"),
        "contact_phone": payload.get("contact_phone"),
    }


# --------------------------------------------------
# PROPERTY TOOL
# --------------------------------------------------
def property_tool(params: dict):
    action = params.get("action")
    auth_token = params.get("auth_token")

    headers = {}
    if auth_token:
        headers["Authorization"] = (
            auth_token if auth_token.startswith("Bearer ")
            else f"Bearer {auth_token}"
        )

    try:
        # --------------------------------------------------
        # 🔍 SEARCH PROPERTY (PARTIAL ALLOWED)
        # --------------------------------------------------
        if action == "search":
            payload = params.get("payload", {})

            r = requests.get(
                f"{PROPERTY_SERVICE_URL}/properties/search",
                params={
                    "city": payload.get("city"),
                    "purpose": payload.get("purpose"),
                    "budget": payload.get("budget"),
                },
                timeout=10,
            )

            parsed = safe_json_loads(r.text, default=None)

            if parsed is None:
                logger.error(
                    "❌ Invalid JSON from property service | "
                    "status=%s | body=%s",
                    r.status_code,
                    r.text,
                )
                return {
                    "success": False,
                    "errors": ["Invalid response from property service"],
                    "status_code": r.status_code,
                }

            return parsed

        # --------------------------------------------------
        # ➕ ADD PROPERTY
        # --------------------------------------------------
        if action == "add":
            payload = normalize_property_payload(
                params.get("payload", {})
            )

            r = requests.post(
                f"{PROPERTY_SERVICE_URL}/properties/",
                json=payload,
                headers=headers,
                timeout=10,
            )

            parsed = safe_json_loads(r.text, default=None)
            if parsed is None:
                return {
                    "success": False,
                    "errors": ["Invalid response from property service"],
                }

            return parsed

        # --------------------------------------------------
        # ✏️ UPDATE PROPERTY
        # --------------------------------------------------
        if action == "update":
            property_id = params.get("property_id")
            if not property_id:
                return {
                    "success": False,
                    "errors": ["property_id is required"],
                }

            payload = {
                k: v
                for k, v in normalize_property_payload(
                    params.get("payload", {})
                ).items()
                if v is not None
            }

            r = requests.put(
                f"{PROPERTY_SERVICE_URL}/properties/{property_id}",
                json=payload,
                headers=headers,
                timeout=10,
            )

            parsed = safe_json_loads(r.text, default=None)
            if parsed is None:
                return {
                    "success": False,
                    "errors": ["Invalid response from property service"],
                }

            return parsed

        # --------------------------------------------------
        # ❌ DELETE PROPERTY
        # --------------------------------------------------
        if action == "delete":
            property_id = params.get("property_id")
            if not property_id:
                return {
                    "success": False,
                    "errors": ["property_id is required"],
                }

            r = requests.delete(
                f"{PROPERTY_SERVICE_URL}/properties/{property_id}",
                headers=headers,
                timeout=10,
            )

            parsed = safe_json_loads(r.text, default=None)
            if parsed is None:
                return {
                    "success": False,
                    "errors": ["Invalid response from property service"],
                }

            return parsed

        # --------------------------------------------------
        # UNKNOWN ACTION
        # --------------------------------------------------
        return {
            "success": False,
            "errors": [f"Unknown action: {action}"],
        }

    except requests.exceptions.RequestException as e:
        logger.exception("❌ Property service request failed")
        return {
            "success": False,
            "errors": [str(e)],
        }
