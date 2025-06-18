from .shared import auth_server

def register_auth_tools(mcp):
    """Register authentication tools with the MCP server"""
    
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