from googleapiclient.discovery import build
from .shared import auth_server

def register_google_tools(mcp):
    """Register Google Calendar tools with the MCP server"""
    
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