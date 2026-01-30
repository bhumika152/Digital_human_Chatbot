import os
import requests
from agents import function_tool, RunContextWrapper
from backend.context.agent_context import AgentRunContext


@function_tool
def property_tool(
    ctx: RunContextWrapper[AgentRunContext],
    params: dict
) -> dict:
    """
    Property Tool
    DigitalHuman (8001) → Property Backend (8000)
    """

    # Property backend URL (8000)
    PROPERTY_SERVICE_URL = os.getenv(
        "PROPERTY_SERVICE_URL",
        "http://localhost:8000"
    )

    action = params.get("action")

    if not action:
        return {"error": "action is required"}

    try:
        # ---------------- SEARCH ----------------
        if action == "search":
            r = requests.get(
                f"{PROPERTY_SERVICE_URL}/properties/search",
                params={
                    "city": params.get("city"),
                    "purpose": params.get("purpose"),
                    "budget": params.get("budget"),
                },
                timeout=10
            )
            return r.json()

        # ---------------- REGION FILTER ----------------
        if action == "region":
            r = requests.get(
                f"{PROPERTY_SERVICE_URL}/properties/region",
                params={
                    "city": params.get("city"),
                    "locality": params.get("locality"),
                    "purpose": params.get("purpose"),
                    "max_budget": params.get("max_budget"),
                },
                timeout=10
            )
            return r.json()

        # ---------------- ADD PROPERTY ----------------
        if action == "add":
            r = requests.post(
                f"{PROPERTY_SERVICE_URL}/properties/",
                json=params.get("payload"),
                headers={
                    # auth token backend context se
                    "Authorization": f"Bearer {ctx.context.auth_token}"
                },
                timeout=10
            )
            return r.json()

        # ---------------- RENT PROPERTY ----------------
        if action == "rent":
            r = requests.post(
                f"{PROPERTY_SERVICE_URL}/properties/rent",
                json=params.get("payload"),
                headers={
                    "Authorization": f"Bearer {ctx.context.auth_token}"
                },
                timeout=10
            )
            return r.json()

        return {"error": f"Unknown action: {action}"}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
