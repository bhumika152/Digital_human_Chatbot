from .implementations import (
    weather_tool,
    browser_search_tool,
    serpapi_search_tool,
    math_tool,
)

TOOL_REGISTRY = {
    "weather": weather_tool,
    "calculator": math_tool,
    "web_search": serpapi_search_tool,
    "browser": browser_search_tool,
}

class ToolExecutor:
    @staticmethod
    def execute(tool: str, arguments: dict):
        if tool == "none":
            return None

        fn = TOOL_REGISTRY.get(tool)

        if not fn:
            return {"error": f"Unknown tool: {tool}"}

        return fn(arguments)