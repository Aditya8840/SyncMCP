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
        """Get events from the Google Calendar API
        
        Args:
            start_date: Lower bound (exclusive) for an event's end time to filter by.
                    Must be an RFC3339 timestamp with mandatory time zone offset.
                    Examples: '2011-06-03T10:00:00-07:00', '2011-06-03T10:00:00Z'
            end_date: Upper bound (exclusive) for an event's start time to filter by.
                    Must be an RFC3339 timestamp with mandatory time zone offset.
                    Examples: '2011-06-03T10:00:00-07:00', '2011-06-03T10:00:00Z'
                    Must be greater than start_date.
        
        Returns:
            String containing list of events or error message
        """
        if not auth_server.is_authenticated():
            return "Not authenticated. Please run authenticate() first."
        
        try:
            credentials = auth_server.get_credentials()
            service = build('calendar', 'v3', credentials=credentials)

            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_date,
                timeMax=end_date,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])

            if not events:
                return "No events found"
            event_list = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                event_list.append(f"• {summary} - {start}")
            
            return f"Found {len(events)} events:\n" + "\n".join(event_list)
        except Exception as e:
            return f"Error fetching events: {str(e)}"

    @mcp.tool()
    def create_event(summary: str, description: str, start_date: str, end_date: str) -> str:
        """Create an event in the Google Calendar API
        
        Args:
            summary: The title of the event
            description: The description of the event
            start_date: The start date of the event
            end_date: The end date of the event
        """
        if not auth_server.is_authenticated():
            return "Not authenticated. Please run authenticate() first."
        
        try:
            credentials = auth_server.get_credentials()
            service = build('calendar', 'v3', credentials=credentials)
            
            event = service.events().insert(calendarId='primary', body={
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_date,
                    'timeZone': 'Asia/Kolkata'
                },
                'end': {
                    'dateTime': end_date,
                    'timeZone': 'Asia/Kolkata'
                }
            }).execute()

            return f"Event created: {event['summary']}"
        except Exception as e:
            return f"Error creating event: {str(e)}"
