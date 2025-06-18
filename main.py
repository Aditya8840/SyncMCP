import sys
from fastmcp import FastMCP
from dotenv import load_dotenv
import os
from auth.server import AuthServer
from googleapiclient.discovery import build
from datetime import datetime, timedelta

load_dotenv()

print("Starting gcalender MCP HTTP server...", file=sys.stderr, flush=True)

mcp = FastMCP("gcalender")

auth_server = AuthServer()

@mcp.tool()
def test_auth_status() -> str:
    """Check current authentication status"""

    if auth_server.is_authenticated():
        creds = auth_server.get_credentials()
        if creds and creds.valid:
            return "✅ Authenticated and credentials are valid"
        elif creds and creds.expired:
            return "⚠️ Authenticated but credentials are expired"
        else:
            return "❓ Authentication status unclear"
    else:
        return "❌ Not authenticated"


@mcp.tool()
def authenticate() -> str:
    """Authenticate with Google Calendar API"""
    try:
        success = auth_server.authenticate()
        if success:
            return "✅ Authentication successful! You can now access Google Calendar."
        else:
            return "❌ Authentication failed. Please check your credentials file."
    except Exception as e:
        return f"❌ Authentication error: {str(e)}"

@mcp.tool()
def get_all_calendars() -> str:
    """Get all calendars from the Google Calendar API"""
    if not auth_server.is_authenticated():
        return "Not authenticated. Please run authenticate() first."
    
    try:
        credentials = auth_server.get_credentials()
        service = build('calendar', 'v3', credentials=credentials)
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])

        if not calendars:
            return "No calendars found"
        calendar_list = []
        for calendar in calendars:
            calendar_list.append(f"• {calendar['summary']} - {calendar['id']}")
        
        return f"Found {len(calendars)} calendars:\n" + "\n".join(calendar_list)
    except Exception as e:
        return f"Error fetching calendars: {str(e)}"

@mcp.tool()
def get_events(start_date: str, end_date: str) -> str:
    """Get events from the Google Calendar API"""

    if not auth_server.is_authenticated():
        return "Not authenticated. Please run authenticate() first."
    
    return "sample event"

if __name__ == "__main__":
    print("About to start HTTP MCP server on http://127.0.0.1:8000/mcp", file=sys.stderr, flush=True)
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")