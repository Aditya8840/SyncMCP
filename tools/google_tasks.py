from googleapiclient.discovery import build
from .shared import auth_server
from typing import Optional
from datetime import date, datetime

def register_google_tasks_tools(mcp):
    """Register Google Tasks tools with the MCP server"""
    
    def get_default_tasklist_id(service):
        """Helper function to get the first available task list ID"""
        try:
            task_lists_result = service.tasklists().list().execute()
            task_lists = task_lists_result.get('items', [])
            if not task_lists:
                raise Exception("No task lists found")
            return task_lists[0]['id']
        except Exception as e:
            raise Exception(f"Error getting task lists: {str(e)}")
    
    @mcp.tool()
    def add_task(title: str, notes: Optional[str] = None, due_date: Optional[date] = None) -> str:
        """
        Adds a task to the default Google Tasks list with proper date handling.
        
        Args:
            title: The title of the task.
            notes: The notes or description for the task (optional).
            due_date: A Python datetime.date object for the due date (optional).
        """
        if not auth_server.is_authenticated():
            return "Not authenticated. Please run authenticate() first."

        try:
            credentials = auth_server.get_credentials()
            service = build('tasks', 'v1', credentials=credentials)

            tasklist_id = get_default_tasklist_id(service)

            task_body = {
                'title': title,
            }

            if notes:
                task_body['notes'] = notes

            if due_date:
                # Convert the date object to the required RFC 3339 string format
                due_string = datetime.combine(due_date, datetime.min.time()).isoformat() + "Z"
                task_body['due'] = due_string

            task = service.tasks().insert(
                tasklist=tasklist_id,
                body=task_body
            ).execute()
            
            return f"Task added: {task['title']}"
        except Exception as e:
            return f"Error adding task: {str(e)}"

    @mcp.tool()
    def get_tasks() -> str:
        """Get all tasks from the Google Tasks API"""
        if not auth_server.is_authenticated():
            return "Not authenticated. Please run authenticate() first."

        try:
            credentials = auth_server.get_credentials()
            service = build('tasks', 'v1', credentials=credentials)

            task_lists_result = service.tasklists().list().execute()
            task_lists = task_lists_result.get('items', [])
            all_tasks = []
            all_task_presentable = []
            if not task_lists:
                return "No tasks found"
            for task_list in task_lists:
                tasks_result = service.tasks().list(tasklist=task_list['id']).execute()
                tasks = tasks_result.get('items', [])
                if not tasks:
                    continue
                all_tasks.extend(tasks)
                
            for task in all_tasks:
                title = task.get('title', 'No title')
                description = task.get('notes', 'No description')
                due = task.get('due', 'No due date')
                all_task_presentable.append(f"• {title} (Description: {description}, Due: {due})")
            
            return f"Found {len(all_task_presentable)} tasks:\n" + "\n".join(all_task_presentable)
        except Exception as e:
            return f"Error fetching tasks: {str(e)}"

    @mcp.tool()
    def update_task(
        task_id: str,
        tasklist_id: Optional[str] = None,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        due_date: Optional[date] = None,
        status: Optional[str] = None
    ) -> str:
        """
        Updates an existing task in a specified Google Tasks list.
        Only provided fields will be updated.
        
        Args:
            task_id: The ID of the task to update.
            tasklist_id: The ID of the list containing the task. If None, uses the default list.
            title: The new title for the task (optional).
            notes: The new notes/description for the task (optional).
            due_date: The new due date as a datetime.date object (optional).
            status: The new status, e.g., 'completed' or 'needsAction' (optional).
        """
        if not auth_server.is_authenticated():
            return "Not authenticated. Please run authenticate() first."

        try:
            credentials = auth_server.get_credentials()
            service = build('tasks', 'v1', credentials=credentials)

            if tasklist_id is None:
                tasklist_id = get_default_tasklist_id(service)

            task_body = {}

            if title is not None:
                task_body['title'] = title
            
            if notes is not None:
                task_body['notes'] = notes
            
            if due_date is not None:
                due_string = datetime.combine(due_date, datetime.min.time()).isoformat() + "Z"
                task_body['due'] = due_string
                
            if status is not None:
                task_body['status'] = status

            if not task_body:
                return "No update information provided."

            updated_task = service.tasks().update(
                tasklist=tasklist_id,
                task=task_id,
                body=task_body
            ).execute()

            return f"Task updated: {updated_task.get('title')}"
        except Exception as e:
            return f"Error updating task: {str(e)}"