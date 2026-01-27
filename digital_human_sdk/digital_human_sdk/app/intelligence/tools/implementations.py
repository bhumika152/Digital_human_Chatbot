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
 
 
# # ---------------- BING SEARCH ----------------
# def bing_search_tool(params: dict):
#     query = params.get("query")
#     api_key = os.getenv("BING_API_KEY")
 
#     if not api_key:
#         return {"error": "BING_API_KEY not set"}
 
#     url = "https://api.bing.microsoft.com/v7.0/search"
#     headers = {
#         "Ocp-Apim-Subscription-Key": api_key
#     }
 
#     r = requests.get(
#         url,
#         headers=headers,
#         params={"q": query},
#         timeout=10
#     )
 
#     return r.json()
 
 
 
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
 