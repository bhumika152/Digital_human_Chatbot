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
 
# ---------------- SERPAPI SEARCH ----------------
def serpapi_search_tool(params: dict):
    query = params.get("query")
    api_key = os.getenv("SERPAPI_API_KEY")
 
    if not api_key:
        return {"error": "SERPAPI_API_KEY not set"}
 
    url = "https://serpapi.com/search.json"
 
    r = requests.get(
        url,
        params={
            "q": query,
            "engine": "google",
            "api_key": api_key,
            "num": 5
        },
        timeout=10
    )
 
    data = r.json()
 
    # Normalize output
    results = []
    for item in data.get("organic_results", []):
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })
 
    return {
        "query": query,
        "results": results
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

# ---------------- PROPERTY TOOL (SINGLE SERVICE) ----------------
from database import get_db
from models import Property
from sqlalchemy.orm import Session
def property_tool(params: dict):
    action = params.get("action")

    if action != "search":
        return {"error": "Only search supported in single-service mode"}

    city = params.get("city")
    purpose = params.get("purpose")
    budget = params.get("budget")

    if not city or not purpose or budget is None:
        return {
            "error": "Missing required parameters: city, purpose, budget"
        }

    db_gen = get_db()
    db: Session = next(db_gen)

    try:
        results = (
            db.query(Property)
            .filter(
                Property.city.ilike(f"%{city}%"),
                Property.purpose == purpose,
                Property.price <= budget,
            )
            .all()
        )

        return {
            "count": len(results),
            "results": [
                {
                    "title": p.title,
                    "city": p.city,
                    "locality": p.locality,
                    "price": p.price,
                    "bhk": p.bhk,
                    "area_sqft": p.area_sqft,
                }
                for p in results
            ],
        }
    finally:
        db.close()
