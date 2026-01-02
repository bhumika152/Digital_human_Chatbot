# executors/tool_executor.py

def execute_tool(tool_request: dict) -> dict:
    """
    Tool Executor (Mock)
    -------------------
    Represents Team A execution layer.
    Executes tool requests deterministically.
    NO LLM, NO reasoning.
    """

    if not tool_request:
        return {}

    tool_name = tool_request.get("tool_name")
    parameters = tool_request.get("parameters", {})

    # -----------------------------
    # Web Search (Mock)
    # -----------------------------
    if tool_name == "web_search":
        query = parameters.get("query", "")

        # Mocked response
        return {
            "documents": [
                {
                    "title": "Redis Persistence Overview",
                    "content": (
                        "Redis persistence allows data to be saved to disk using "
                        "RDB snapshots and AOF logs."
                    ),
                    "source": "redis.io"
                }
            ],
            "query_used": query
        }

    # -----------------------------
    # Unknown tool
    # -----------------------------
    return {
        "error": f"Unsupported tool: {tool_name}"
    }
