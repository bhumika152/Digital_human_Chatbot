from executors.tool_executor import execute_tool

tool_request = {
    "tool_name": "web_search",
    "parameters": {
        "query": "Explain Redis persistence",
        "top_k": 5
    }
}

result = execute_tool(tool_request)

print(result)
