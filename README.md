# SyncMCP

Sync your calendar and tasks seamlessly with MCP. It allows you to authenticate with Google services and perform various calendar and task management operations directly through conversational AI interfaces.

## Features

The following tools are available through this MCP server:

### Authentication Tools
- **`test_auth_status`** - Check current authentication status with Google APIs
- **`authenticate`** - Authenticate with Google Calendar and Tasks APIs using OAuth 2.0

### Google Calendar Tools
- **`get_all_calendars`** - Retrieve all calendars associated with your Google account
- **`get_events`** - Fetch events from your calendar within a specified date range
- **`create_event`** - Create new calendar events with title, description, and time details

### Google Tasks Tools
- **`add_task`** - Add new tasks to your default Google Tasks list with optional notes and due dates
- **`get_tasks`** - Retrieve all tasks from your Google Tasks lists
- **`update_task`** - Update existing tasks (title, notes, due date, completion status)

## Quick Start

1. **Set up Google Cloud credentials** (see Google Cloud Setup section below)
2. **Install dependencies** using uv
3. **Configure environment variables**
4. **Run the MCP server**
5. **Connect to Claude Desktop or Cursor**

## Prerequisites

- Python 3.11 or higher
- A Google Cloud project with the Calendar and Tasks API enabled
- OAuth 2.0 credentials (Desktop app type)
- [uv](https://github.com/astral-sh/uv) package manager

## Google Cloud Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API and Google Tasks API for your project
4. Create OAuth 2.0 credentials:
   - Go to Credentials → "Create Credentials" → "OAuth client ID"
   - Choose "User data" and add scopes: `https://www.googleapis.com/auth/calendar`, `https://www.googleapis.com/auth/tasks`
   - Select "Desktop app" as the application type (**Important!**)
   - Download and save the JSON credentials file as `credentials.json` in your project root

## Installation

1. **Install uv** (if not already installed):
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/Aditya8840/SyncMCP
   cd SyncMCP
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Modify the `.env` file with your preferred settings if needed.

## Usage

1. **Run the MCP server:**
   ```bash
   uv run main.py
   ```
   
   The server will start on `http://127.0.0.1:8000/mcp`

2. **Add MCP to Cursor or Claude:**
   
   Since this uses streamable-http transport, connect to: `http://127.0.0.1:8000/mcp`

## First Time Authentication

1. Start the MCP server
2. In Claude Desktop or Cursor, use the `authenticate()` function
3. A browser window will open for Google OAuth authentication
4. Grant the necessary permissions for Calendar and Tasks access
5. Once authenticated, you can use all the available tools

## Example Usage

Once authenticated, you can interact with your Google Calendar and Tasks:

- "Show me my events for next week"
- "Create a event titled 'Team Standup' tomorrow at 10 AM"
- "Add a task to review the project proposal"
- "What tasks do I have pending?"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
