from digital_human_sdk.app.intelligence.contracts.tool_request import ToolRequest


class ToolExecutor:

    @staticmethod
    def execute(tool_request):
        if tool_request.tool_name == "calculator":
            try:
                expr = tool_request.arguments.get("expression", "")
                if not all(c in "0123456789+-*/(). " for c in expr):
                    raise ValueError("Invalid chars")
                return {"result": eval(expr)}
            except Exception:
                return {"error": "Tool execution failed"}

        return {"error": "Tool not allowed"}

