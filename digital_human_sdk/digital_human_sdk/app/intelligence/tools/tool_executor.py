from digital_human_sdk.app.intelligence.contracts.tool_request import ToolRequest


class ToolExecutor:
    """Minimal stub so the SDK can run without backend tool plumbing."""

    @staticmethod
    def execute(request: ToolRequest):
        # In this SDK-only run, we don't actually call external tools.
        return {
            "status": "noop",
            "tool_requested": request.tool_name,
            "arguments": request.arguments,
            "message": "Tool execution not implemented in SDK sandbox.",
        }

