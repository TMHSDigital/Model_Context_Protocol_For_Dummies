"""
Monday.com MCP Server Example in Python

This demonstrates a basic MCP server that integrates with Monday.com's GraphQL API.
It provides:
- Resources: Access to boards, items, and user information 
- Tools: Functions to create and update items, assign users, etc.
"""

import json
import os
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp

# Note: In a real implementation, you would use the actual MCP SDK
# from modelcontextprotocol import Server, ServerOptions
# Since this is an example, we'll simulate the MCP server behavior

class MondayMCPServer:
    """An MCP server that integrates with Monday.com's GraphQL API."""
    
    def __init__(self):
        self.name = "MondayMCPServer"
        self.version = "1.0.0"
        self.api_url = "https://api.monday.com/v2"
        self.api_token = os.environ.get("MONDAY_API_TOKEN", "your-api-token")
        
        # Rate limiting state
        self.rate_limits = {
            "daily_remaining": 1000,  # Depends on subscription tier
            "reset_time": time.time() + 86400,
            "active_requests": 0
        }
        
        # Cache for frequently accessed data
        self.cache = {
            "boards": {},
            "board_structure": {},
            "items": {},
            "users": {}
        }
    
    async def query_monday_api(self, query: str, variables: Dict = None) -> Dict:
        """Execute a GraphQL query against the Monday.com API."""
        if variables is None:
            variables = {}
        
        await self._check_rate_limit()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": self.api_token
                    },
                    json={"query": query, "variables": variables}
                ) as response:
                    result = await response.json()
                    
                    if "errors" in result:
                        raise ValueError(f"Monday.com API Error: {result['errors'][0]['message']}")
                    
                    return result["data"]
        finally:
            self._release_rate_limit()
    
    async def _check_rate_limit(self) -> bool:
        """Check if the request can proceed under rate limits."""
        if self.rate_limits["daily_remaining"] <= 0:
            reset_time_str = datetime.fromtimestamp(self.rate_limits["reset_time"]).isoformat()
            raise ValueError(f"Rate limit exceeded. Resets at {reset_time_str}")
        
        if self.rate_limits["active_requests"] >= 10:
            raise ValueError("Too many concurrent requests. Please try again.")
        
        self.rate_limits["daily_remaining"] -= 1
        self.rate_limits["active_requests"] += 1
        
        return True
    
    def _release_rate_limit(self):
        """Release the active request counter."""
        self.rate_limits["active_requests"] -= 1
    
    async def list_resources(self) -> Dict[str, List[Dict[str, str]]]:
        """List available resources."""
        return {
            "resources": [
                {
                    "id": "list_boards",
                    "name": "Boards",
                    "description": "List all accessible boards"
                },
                {
                    "id": "get_board_structure",
                    "name": "Board Structure",
                    "description": "Get the structure of a specific board"
                },
                {
                    "id": "list_items_by_board",
                    "name": "Items by Board",
                    "description": "List all items in a specific board"
                },
                {
                    "id": "list_items_by_status",
                    "name": "Items by Status",
                    "description": "List items filtered by status"
                },
                {
                    "id": "list_overdue_items",
                    "name": "Overdue Items",
                    "description": "List items past their due dates"
                },
                {
                    "id": "get_user_details",
                    "name": "User Details",
                    "description": "Get details about team members"
                },
                {
                    "id": "get_user_workload",
                    "name": "User Workload",
                    "description": "View task distribution across team members"
                }
            ]
        }
    
    async def read_resource(self, resource_id: str, parameters: Dict = None) -> Dict[str, str]:
        """Read a specific resource."""
        if parameters is None:
            parameters = {}
        
        # Resource handlers
        resource_handlers = {
            "list_boards": self.list_boards,
            "get_board_structure": self.get_board_structure,
            "list_items_by_board": self.list_items_by_board,
            "list_items_by_status": self.list_items_by_status,
            "list_overdue_items": self.list_overdue_items,
            "get_user_details": self.get_user_details,
            "get_user_workload": self.get_user_workload
        }
        
        if resource_id not in resource_handlers:
            raise ValueError(f"Resource {resource_id} not found")
        
        return await resource_handlers[resource_id](parameters)
    
    async def list_boards(self, parameters: Dict = None) -> Dict[str, str]:
        """List all accessible boards."""
        # Check cache first
        if "all" in self.cache["boards"] and self.cache["boards"]["all"]["timestamp"] > time.time() - 300:
            return {"content": json.dumps(self.cache["boards"]["all"]["data"])}
        
        query = """
            query {
                boards {
                    id
                    name
                    description
                    state
                    board_kind
                    updated_at
                }
            }
        """
        
        result = await self.query_monday_api(query)
        
        # Store in cache for 5 minutes
        self.cache["boards"]["all"] = {
            "timestamp": time.time(),
            "data": result["boards"]
        }
        
        return {"content": json.dumps(result["boards"])}
    
    async def get_board_structure(self, parameters: Dict) -> Dict[str, str]:
        """Get the structure of a specific board."""
        if "board_id" not in parameters:
            raise ValueError("board_id parameter is required")
        
        board_id = parameters["board_id"]
        
        # Check cache first
        cache_key = f"structure-{board_id}"
        if cache_key in self.cache["board_structure"] and self.cache["board_structure"][cache_key]["timestamp"] > time.time() - 300:
            return {"content": json.dumps(self.cache["board_structure"][cache_key]["data"])}
        
        query = f"""
            query {{
                boards(ids: {board_id}) {{
                    columns {{
                        id
                        title
                        type
                        settings_str
                    }}
                    groups {{
                        id
                        title
                        color
                        position
                    }}
                }}
            }}
        """
        
        result = await self.query_monday_api(query)
        board_structure = result["boards"][0]
        
        # Store in cache for 5 minutes
        self.cache["board_structure"][cache_key] = {
            "timestamp": time.time(),
            "data": board_structure
        }
        
        return {"content": json.dumps(board_structure)}
    
    async def list_items_by_board(self, parameters: Dict) -> Dict[str, str]:
        """List all items in a specific board."""
        if "board_id" not in parameters:
            raise ValueError("board_id parameter is required")
        
        board_id = parameters["board_id"]
        
        query = f"""
            query {{
                boards(ids: {board_id}) {{
                    name
                    items {{
                        id
                        name
                        state
                        column_values {{
                            id
                            title
                            text
                            value
                        }}
                        created_at
                        updated_at
                    }}
                }}
            }}
        """
        
        result = await self.query_monday_api(query)
        return {"content": json.dumps(result["boards"][0])}
    
    async def list_items_by_status(self, parameters: Dict) -> Dict[str, str]:
        """List items filtered by status."""
        if "board_id" not in parameters or "status" not in parameters:
            raise ValueError("board_id and status parameters are required")
        
        board_id = parameters["board_id"]
        status = parameters["status"]
        
        # First, get the status column id
        board_structure_result = await self.get_board_structure({"board_id": board_id})
        board_structure = json.loads(board_structure_result["content"])
        
        status_column = next((col for col in board_structure["columns"] if col["type"] == "status"), None)
        if not status_column:
            raise ValueError("Status column not found on this board")
        
        query = f"""
            query {{
                boards(ids: {board_id}) {{
                    items {{
                        id
                        name
                        column_values(ids: ["{status_column["id"]}"]) {{
                            text
                        }}
                        created_at
                        updated_at
                    }}
                }}
            }}
        """
        
        result = await self.query_monday_api(query)
        
        # Filter items by status
        filtered_items = [
            item for item in result["boards"][0]["items"]
            if item["column_values"][0]["text"].lower() == status.lower()
        ]
        
        return {"content": json.dumps(filtered_items)}
    
    async def list_overdue_items(self, parameters: Dict = None) -> Dict[str, str]:
        """List items past their due dates."""
        query = """
            query {
                items_by_column_values(
                    board_id: ALL_BOARDS
                    column_id: "date"
                    column_value: "overdue"
                ) {
                    id
                    name
                    board {
                        id
                        name
                    }
                    column_values {
                        title
                        text
                    }
                }
            }
        """
        
        result = await self.query_monday_api(query)
        return {"content": json.dumps(result["items_by_column_values"])}
    
    async def get_user_details(self, parameters: Dict) -> Dict[str, str]:
        """Get details about a team member."""
        if "user_id" not in parameters:
            raise ValueError("user_id parameter is required")
        
        user_id = parameters["user_id"]
        
        # Check cache first
        if user_id in self.cache["users"] and self.cache["users"][user_id]["timestamp"] > time.time() - 300:
            return {"content": json.dumps(self.cache["users"][user_id]["data"])}
        
        query = f"""
            query {{
                users(ids: {user_id}) {{
                    id
                    name
                    email
                    title
                    photo_thumb
                    created_at
                }}
            }}
        """
        
        result = await self.query_monday_api(query)
        
        # Store in cache for 5 minutes
        self.cache["users"][user_id] = {
            "timestamp": time.time(),
            "data": result["users"][0]
        }
        
        return {"content": json.dumps(result["users"][0])}
    
    async def get_user_workload(self, parameters: Dict) -> Dict[str, str]:
        """View task distribution for a team member."""
        if "user_id" not in parameters:
            raise ValueError("user_id parameter is required")
        
        user_id = parameters["user_id"]
        
        query = f"""
            query {{
                items_by_person_id(
                    person_id: {user_id}
                ) {{
                    id
                    name
                    board {{
                        id
                        name
                    }}
                    column_values {{
                        id
                        title
                        text
                    }}
                }}
            }}
        """
        
        result = await self.query_monday_api(query)
        return {"content": json.dumps(result["items_by_person_id"])}
    
    async def list_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """List available tools."""
        return {
            "tools": [
                {
                    "name": "create_item",
                    "description": "Create a new item on a board",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "board_id": {
                                "type": "number",
                                "description": "The ID of the board"
                            },
                            "group_id": {
                                "type": "string",
                                "description": "The ID of the group to add the item to"
                            },
                            "item_name": {
                                "type": "string",
                                "description": "The name of the item to create"
                            },
                            "column_values": {
                                "type": "object",
                                "description": "Column values for the new item"
                            }
                        },
                        "required": ["board_id", "item_name"]
                    }
                },
                {
                    "name": "update_item_status",
                    "description": "Update the status of an item",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                                "type": "number",
                                "description": "The ID of the item"
                            },
                            "status_column_id": {
                                "type": "string",
                                "description": "The ID of the status column"
                            },
                            "new_status": {
                                "type": "string",
                                "description": "The new status value"
                            }
                        },
                        "required": ["item_id", "status_column_id", "new_status"]
                    }
                },
                {
                    "name": "assign_user_to_item",
                    "description": "Assign a user to an item",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                                "type": "number",
                                "description": "The ID of the item"
                            },
                            "user_id": {
                                "type": "number",
                                "description": "The ID of the user to assign"
                            },
                            "person_column_id": {
                                "type": "string",
                                "description": "The ID of the person column"
                            }
                        },
                        "required": ["item_id", "user_id", "person_column_id"]
                    }
                },
                {
                    "name": "add_update_to_item",
                    "description": "Add an update/comment to an item",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                                "type": "number",
                                "description": "The ID of the item"
                            },
                            "update_text": {
                                "type": "string",
                                "description": "The text of the update"
                            }
                        },
                        "required": ["item_id", "update_text"]
                    }
                }
            ]
        }
    
    async def call_tool(self, name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool."""
        # Tool handlers
        tool_handlers = {
            "create_item": self.create_item,
            "update_item_status": self.update_item_status,
            "assign_user_to_item": self.assign_user_to_item,
            "add_update_to_item": self.add_update_to_item
        }
        
        if name not in tool_handlers:
            raise ValueError(f"Tool {name} not found")
        
        return await tool_handlers[name](parameters)
    
    async def create_item(self, parameters: Dict) -> Dict[str, Any]:
        """Create a new item on a board."""
        board_id = parameters["board_id"]
        item_name = parameters["item_name"]
        group_id = parameters.get("group_id")
        column_values = parameters.get("column_values", {})
        
        column_values_json = json.dumps(column_values)
        
        query = f"""
            mutation {{
                create_item(
                    board_id: {board_id},
                    {f'group_id: "{group_id}",' if group_id else ''}
                    item_name: "{item_name}",
                    column_values: '{column_values_json}'
                ) {{
                    id
                    name
                }}
            }}
        """
        
        result = await self.query_monday_api(query)
        
        return {
            "result": {
                "id": result["create_item"]["id"],
                "name": result["create_item"]["name"],
                "message": "Item created successfully"
            }
        }
    
    async def update_item_status(self, parameters: Dict) -> Dict[str, Any]:
        """Update the status of an item."""
        item_id = parameters["item_id"]
        status_column_id = parameters["status_column_id"]
        new_status = parameters["new_status"]
        
        column_value = json.dumps({
            "label": new_status
        })
        
        query = f"""
            mutation {{
                change_column_value(
                    item_id: {item_id},
                    column_id: "{status_column_id}",
                    value: '{column_value}'
                ) {{
                    id
                    name
                }}
            }}
        """
        
        result = await self.query_monday_api(query)
        
        return {
            "result": {
                "id": result["change_column_value"]["id"],
                "message": "Status updated successfully"
            }
        }
    
    async def assign_user_to_item(self, parameters: Dict) -> Dict[str, Any]:
        """Assign a user to an item."""
        item_id = parameters["item_id"]
        user_id = parameters["user_id"]
        person_column_id = parameters["person_column_id"]
        
        column_value = json.dumps({
            "personsAndTeams": [
                {
                    "id": user_id,
                    "kind": "person"
                }
            ]
        })
        
        query = f"""
            mutation {{
                change_column_value(
                    item_id: {item_id},
                    column_id: "{person_column_id}",
                    value: '{column_value}'
                ) {{
                    id
                    name
                }}
            }}
        """
        
        result = await self.query_monday_api(query)
        
        return {
            "result": {
                "id": result["change_column_value"]["id"],
                "message": "User assigned successfully"
            }
        }
    
    async def add_update_to_item(self, parameters: Dict) -> Dict[str, Any]:
        """Add an update/comment to an item."""
        item_id = parameters["item_id"]
        update_text = parameters["update_text"]
        
        query = f"""
            mutation {{
                create_update(
                    item_id: {item_id},
                    body: "{update_text}"
                ) {{
                    id
                    text
                }}
            }}
        """
        
        result = await self.query_monday_api(query)
        
        return {
            "result": {
                "id": result["create_update"]["id"],
                "message": "Update added successfully"
            }
        }
    
    async def list_prompts(self) -> Dict[str, List[Dict[str, str]]]:
        """List available prompts/workflows."""
        return {
            "prompts": [
                {
                    "id": "project_initiation",
                    "name": "Project Initiation",
                    "description": "Start a new project with initial tasks and team assignments"
                },
                {
                    "id": "sprint_planning",
                    "name": "Sprint Planning",
                    "description": "Move items from backlog to current sprint with estimates and priorities"
                },
                {
                    "id": "risk_management",
                    "name": "Risk Management",
                    "description": "Identify and escalate tasks at risk"
                }
            ]
        }
    
    async def read_prompt(self, prompt_id: str) -> Dict[str, str]:
        """Read a specific prompt/workflow."""
        prompt_content = None
        
        if prompt_id == "project_initiation":
            prompt_content = {
                "name": "Project Initiation",
                "description": "Start a new project with initial tasks and team assignments",
                "steps": [
                    {
                        "id": "create_board",
                        "type": "input",
                        "label": "Create a new project board",
                        "fields": [
                            {
                                "id": "board_name",
                                "label": "Project Name",
                                "type": "text",
                                "required": True
                            },
                            {
                                "id": "template_id",
                                "label": "Template",
                                "type": "select",
                                "options": [
                                    {"label": "Basic Project", "value": "1"},
                                    {"label": "Scrum", "value": "2"},
                                    {"label": "Kanban", "value": "3"}
                                ],
                                "required": True
                            }
                        ]
                    },
                    {
                        "id": "assign_team",
                        "type": "input",
                        "label": "Assign Team Members",
                        "fields": [
                            {
                                "id": "team_members",
                                "label": "Team Members",
                                "type": "multiselect",
                                "dynamicOptions": "users",
                                "required": True
                            }
                        ]
                    },
                    {
                        "id": "setup_tasks",
                        "type": "input",
                        "label": "Set Up Initial Tasks",
                        "fields": [
                            {
                                "id": "tasks",
                                "label": "Tasks",
                                "type": "textarea",
                                "placeholder": "Enter tasks (one per line)",
                                "required": True
                            }
                        ]
                    }
                ]
            }
        
        elif prompt_id == "sprint_planning":
            prompt_content = {
                "name": "Sprint Planning",
                "description": "Move items from backlog to current sprint with estimates and priorities",
                "steps": [
                    {
                        "id": "select_board",
                        "type": "input",
                        "label": "Select Project Board",
                        "fields": [
                            {
                                "id": "board_id",
                                "label": "Board",
                                "type": "select",
                                "dynamicOptions": "boards",
                                "required": True
                            }
                        ]
                    },
                    {
                        "id": "select_backlog_items",
                        "type": "input",
                        "label": "Select Backlog Items for Sprint",
                        "fields": [
                            {
                                "id": "backlog_items",
                                "label": "Backlog Items",
                                "type": "multiselect",
                                "dynamicOptions": "items_by_status",
                                "required": True
                            }
                        ]
                    },
                    {
                        "id": "set_estimates",
                        "type": "input",
                        "label": "Set Estimates and Priorities",
                        "fields": [
                            {
                                "id": "due_date",
                                "label": "Sprint End Date",
                                "type": "date",
                                "required": True
                            }
                        ]
                    }
                ]
            }
        
        elif prompt_id == "risk_management":
            prompt_content = {
                "name": "Risk Management",
                "description": "Identify and escalate tasks at risk",
                "steps": [
                    {
                        "id": "select_project",
                        "type": "input",
                        "label": "Select Project",
                        "fields": [
                            {
                                "id": "board_id",
                                "label": "Board",
                                "type": "select",
                                "dynamicOptions": "boards",
                                "required": True
                            }
                        ]
                    },
                    {
                        "id": "identify_risks",
                        "type": "display",
                        "label": "Identifying Tasks at Risk...",
                        "computedContent": "delayed_tasks"
                    },
                    {
                        "id": "escalate_risks",
                        "type": "input",
                        "label": "Escalate Selected Risks",
                        "fields": [
                            {
                                "id": "risk_items",
                                "label": "Items at Risk",
                                "type": "multiselect",
                                "dynamicOptions": "delayed_tasks",
                                "required": True
                            },
                            {
                                "id": "notify_users",
                                "label": "Notify",
                                "type": "multiselect",
                                "dynamicOptions": "users",
                                "required": True
                            },
                            {
                                "id": "escalation_message",
                                "label": "Message",
                                "type": "textarea",
                                "required": True
                            }
                        ]
                    }
                ]
            }
        else:
            raise ValueError(f"Prompt {prompt_id} not found")
        
        return {"content": json.dumps(prompt_content)}
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an MCP JSON-RPC request."""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "ListResources":
            return await self.list_resources()
        
        elif method == "ReadResource":
            return await self.read_resource(params["resourceId"], params.get("parameters"))
        
        elif method == "ListTools":
            return await self.list_tools()
        
        elif method == "CallTool":
            return await self.call_tool(params["name"], params["parameters"])
        
        elif method == "ListPrompts":
            return await self.list_prompts()
        
        elif method == "ReadPrompt":
            return await self.read_prompt(params["promptId"])
        
        else:
            raise ValueError(f"Unsupported method: {method}")

    async def listen(self):
        """Simulates the MCP server listening for requests."""
        print(f"{self.name} v{self.version} is running...")
        print("This is a simulated server. In a real implementation, you would use:")
        print("  from modelcontextprotocol import Server")
        print("  server = Server(name='MondayMCPServer', version='1.0.0', features={...})")
        print("  server.listen()")

async def main():
    server = MondayMCPServer()
    await server.listen()
    
    # Example of how client interaction would work
    print("\nSimulating client requests:")
    
    # List resources
    print("\n> Client requests ListResources")
    response = await server.process_request({"method": "ListResources"})
    print(f"< Server responds: {json.dumps(response, indent=2)}")
    
    # Create a task
    print("\n> Client calls CreateItem tool")
    response = await server.process_request({
        "method": "CallTool",
        "params": {
            "name": "create_item",
            "parameters": {
                "board_id": 12345678,
                "group_id": "topics",
                "item_name": "Implement MCP integration",
                "column_values": {
                    "status": {
                        "label": "Working on it"
                    },
                    "date": "2025-06-01",
                    "person": {
                        "personsAndTeams": [
                            {
                                "id": 12345,
                                "kind": "person"
                            }
                        ]
                    }
                }
            }
        }
    })
    print(f"< Server responds: {json.dumps(response, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main()) 