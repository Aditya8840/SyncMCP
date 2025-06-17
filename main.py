import sys
from fastmcp import FastMCP

print("Starting gcalender MCP HTTP server...", file=sys.stderr, flush=True)

mcp = FastMCP("gcalender")

@mcp.tool()
def get_events(start_date: str, end_date: str) -> str:
    """Get events from the Google Calendar API"""
    print(f"get_events called with start_date={start_date}, end_date={end_date}", file=sys.stderr, flush=True)
    return "Sample event data"

if __name__ == "__main__":
    print("About to start HTTP MCP server on http://127.0.0.1:8000/mcp", file=sys.stderr, flush=True)
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")