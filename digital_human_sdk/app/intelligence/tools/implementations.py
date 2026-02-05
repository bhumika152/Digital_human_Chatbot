import os
import requests
from dotenv import load_dotenv
load_dotenv()
import math
 
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
def browser_search_tool(params: dict):
    query = params.get("query")
 
    url = "https://duckduckgo.com/html/"
    r = requests.post(url, data={"q": query}, timeout=10)
 
    return {
        "query": query,
        "html_length": len(r.text)
    }
 
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
            "num": 5
        },
        timeout=10
    )

    data = r.json()

    response = []
    for item in data.get("organic_results", []):
        title = item.get("title")
        link = item.get("link")
        snippet = item.get("snippet")

        response.append(
            f"🔗 **[{title}]({link})**\n{snippet}\n"
        )

    return {
        "answer": "\n".join(response)
    }

 
 
# ---------------- MATH ----------------
def math_tool(params: dict):
    expression = params.get("expression")
    try:
        result = eval(expression, {"__builtins__": {}})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


# # ---------------- PROPERTY TOOL ----------------
# def property_tool(params: dict):
#     """
#     DigitalHuman (8001) → Property Backend (8000)
#     DB is NOT accessed here.
#     """

#     PROPERTY_SERVICE_URL = os.getenv(
#         "PROPERTY_SERVICE_URL",
#         "http://127.0.0.1:8000"
#     )

#     action = params.get("action")

#     if not action:
#         return {"error": "Missing action for property tool"}

#     try:
#         # 🔍 SEARCH PROPERTY
#         if action == "search":
#             r = requests.get(
#                 f"{PROPERTY_SERVICE_URL}/properties/search",
#                 params={
#                     "city": params.get("city"),
#                     "purpose": params.get("purpose"),
#                     "budget": params.get("budget"),
#                 },
#                 timeout=10,
#             )
#             return r.json()

#         # 📍 REGION FILTER
#         if action == "region":
#             r = requests.get(
#                 f"{PROPERTY_SERVICE_URL}/properties/region",
#                 params={
#                     "city": params.get("city"),
#                     "locality": params.get("locality"),
#                     "purpose": params.get("purpose"),
#                     "max_budget": params.get("max_budget"),
#                 },
#                 timeout=10,
#             )
#             return r.json()

#         # ➕ ADD PROPERTY (AUTH REQUIRED)
#         if action == "add":
#             r = requests.post(
#                 f"{PROPERTY_SERVICE_URL}/properties/",
#                 json=params.get("payload"),
#                 headers={
#                     "Authorization": params.get("auth_token", "")
#                 },
#                 timeout=10,
#             )
#             return r.json()

#         # 🏠 ADD RENT PROPERTY
#         if action == "rent":
#             r = requests.post(
#                 f"{PROPERTY_SERVICE_URL}/properties/rent",
#                 json=params.get("payload"),
#                 headers={
#                     "Authorization": params.get("auth_token", "")
#                 },
#                 timeout=10,
#             )
#             return r.json()

#         return {"error": f"Unknown property action: {action}"}

#     except requests.exceptions.RequestException as e:
#         return {"error": str(e)}
import os
import logging
import requests
 
logger = logging.getLogger("property_tool")
 
PROPERTY_SERVICE_URL = os.getenv(
    "PROPERTY_SERVICE_URL",
    "http://127.0.0.1:8000"
)
 
# --------------------------------------------------
# PAYLOAD NORMALIZER (LLM → BACKEND CONTRACT)
# --------------------------------------------------
 
def normalize_property_payload(payload: dict) -> dict:
    """
    Normalize LLM payload keys to backend PropertyCreateRequest schema
    """
    return {
        "title": payload.get("title") or "Untitled Property",
        "city": payload.get("city"),
        "locality": payload.get("locality"),
        "purpose": payload.get("purpose"),
        "price": payload.get("price"),
        "bhk": payload.get("bhk"),
        "area_sqft": payload.get("area_sqft") or payload.get("size_sqft"),
        "is_legal": payload.get("is_legal", True),
        "owner_name": payload.get("owner_name"),
        "contact_phone": payload.get("contact_phone") or payload.get("owner_contact"),
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
        # 🔍 SEARCH PROPERTY
        if action == "search":
            r = requests.get(
                f"{PROPERTY_SERVICE_URL}/properties/search",
                params={
                    "city": params.get("city"),
                    "purpose": params.get("purpose"),
                    "budget": params.get("budget"),
                },
                timeout=10,
            )
            return r.json()
 
        # ➕ ADD PROPERTY
        if action == "add":
            raw_payload = params.get("payload", {})
            normalized_payload = normalize_property_payload(raw_payload)
 
            logger.info(f"📤 Sending property payload: {normalized_payload}")
 
            r = requests.post(
                f"{PROPERTY_SERVICE_URL}/properties/",
                json=normalized_payload,
                headers=headers,
                timeout=10,
            )
            return r.json()
 
        # ✏️ UPDATE PROPERTY
        if action == "update":
            property_id = params.get("property_id")
            if not property_id:
                return {"error": "Missing property_id"}
 
            normalized_payload = normalize_property_payload(
                params.get("payload", {})
            )
 
            r = requests.put(
                f"{PROPERTY_SERVICE_URL}/properties/{property_id}",
                json=normalized_payload,
                headers=headers,
                timeout=10,
            )
            return r.json()
 
        # ❌ DELETE PROPERTY
        if action == "delete":
            property_id = params.get("property_id")
            if not property_id:
                return {"error": "Missing property_id"}
 
            r = requests.delete(
                f"{PROPERTY_SERVICE_URL}/properties/{property_id}",
                headers=headers,
                timeout=10,
            )
            return r.json()
 
        # 🌍 REGION FILTER
        if action == "region":
            r = requests.get(
                f"{PROPERTY_SERVICE_URL}/properties/region",
                params={
                    "city": params.get("city"),
                    "locality": params.get("locality"),
                    "purpose": params.get("purpose"),
                    "max_budget": params.get("max_budget"),
                },
                timeout=10,
            )
            return r.json()
 
        return {"error": f"Unknown action: {action}"}
 
    except requests.exceptions.RequestException as e:
        logger.exception("❌ Property service request failed")
        return {"error": str(e)}
 
 