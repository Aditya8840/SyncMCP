import sys
from fastmcp import FastMCP
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

from tools.auth import register_auth_tools
from tools.google_calendar import register_google_calendar_tools
from tools.google_tasks import register_google_tasks_tools

load_dotenv()

print("Starting gcalender MCP HTTP server...", file=sys.stderr, flush=True)

mcp = FastMCP("gcalender")

register_auth_tools(mcp)
register_google_calendar_tools(mcp)
register_google_tasks_tools(mcp)

if __name__ == "__main__":
    print("About to start HTTP MCP server on http://127.0.0.1:8000/mcp", file=sys.stderr, flush=True)
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")