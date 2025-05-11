"""
Simple MCP Server Example in Python

This demonstrates a basic MCP server that exposes both resources and tools.
It simulates a note-taking service with:
- Resources: Notes stored by the user
- Tools: Functions to create, update, and search notes
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

# Note: In a real implementation, you would use the actual MCP SDK
# from modelcontextprotocol import Server
# Since this is an example, we'll simulate the MCP server behavior

class NoteMCPServer:
    """A simulated MCP server for note-taking functionality."""
    
    def __init__(self):
        self.name = "NoteMCPServer"
        self.version = "1.0.0"
        self.notes = {
            "note-1": {
                "id": "note-1",
                "title": "Welcome to MCP Notes",
                "content": "This is your first note. You can create more using the create_note tool.",
                "tags": ["welcome", "introduction"],
                "created_at": "2025-05-01T10:00:00Z",
                "updated_at": "2025-05-01T10:00:00Z"
            },
            "note-2": {
                "id": "note-2",
                "title": "Shopping List",
                "content": "- Milk\n- Eggs\n- Bread\n- Apples",
                "tags": ["shopping", "groceries"],
                "created_at": "2025-05-02T14:30:00Z",
                "updated_at": "2025-05-02T14:30:00Z"
            }
        }
    
    async def list_resources(self) -> Dict[str, List[Dict[str, str]]]:
        """List available resources (notes)."""
        resources = []
        for note_id, note in self.notes.items():
            resources.append({
                "id": note_id,
                "name": note["title"],
                "description": f"Note created on {note['created_at'].split('T')[0]}"
            })
        return {"resources": resources}
    
    async def read_resource(self, resource_id: str) -> Dict[str, str]:
        """Read a specific resource (note)."""
        if resource_id in self.notes:
            return {"content": json.dumps(self.notes[resource_id], indent=2)}
        raise ValueError(f"Note {resource_id} not found")
    
    async def list_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """List available tools."""
        return {
            "tools": [
                {
                    "name": "create_note",
                    "description": "Create a new note",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the note"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content of the note"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags for the note"
                            }
                        },
                        "required": ["title", "content"]
                    }
                },
                {
                    "name": "update_note",
                    "description": "Update an existing note",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "note_id": {
                                "type": "string",
                                "description": "ID of the note to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New title (optional)"
                            },
                            "content": {
                                "type": "string",
                                "description": "New content (optional)"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "New tags (optional)"
                            }
                        },
                        "required": ["note_id"]
                    }
                },
                {
                    "name": "search_notes",
                    "description": "Search notes by query or tags",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (searches titles and content)"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by tags"
                            }
                        }
                    }
                }
            ]
        }
    
    async def call_tool(self, name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool."""
        if name == "create_note":
            return await self._create_note(parameters)
        elif name == "update_note":
            return await self._update_note(parameters)
        elif name == "search_notes":
            return await self._search_notes(parameters)
        raise ValueError(f"Tool {name} not found")
    
    async def _create_note(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new note."""
        title = parameters["title"]
        content = parameters["content"]
        tags = parameters.get("tags", [])
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        note_id = f"note-{len(self.notes) + 1}"
        
        self.notes[note_id] = {
            "id": note_id,
            "title": title,
            "content": content,
            "tags": tags,
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        return {
            "result": {
                "id": note_id,
                "title": title,
                "message": "Note created successfully"
            }
        }
    
    async def _update_note(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing note."""
        note_id = parameters["note_id"]
        
        if note_id not in self.notes:
            raise ValueError(f"Note {note_id} not found")
        
        note = self.notes[note_id]
        
        if "title" in parameters:
            note["title"] = parameters["title"]
        if "content" in parameters:
            note["content"] = parameters["content"]
        if "tags" in parameters:
            note["tags"] = parameters["tags"]
        
        note["updated_at"] = datetime.utcnow().isoformat() + "Z"
        
        return {
            "result": {
                "id": note_id,
                "title": note["title"],
                "message": "Note updated successfully"
            }
        }
    
    async def _search_notes(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Search notes by query or tags."""
        query = parameters.get("query", "").lower()
        tags = parameters.get("tags", [])
        
        results = []
        
        for note_id, note in self.notes.items():
            # Check if the note matches the query
            query_match = (
                not query or
                query in note["title"].lower() or
                query in note["content"].lower()
            )
            
            # Check if the note has all the required tags
            tag_match = (
                not tags or
                all(tag in note["tags"] for tag in tags)
            )
            
            if query_match and tag_match:
                results.append({
                    "id": note_id,
                    "title": note["title"],
                    "preview": note["content"][:100] + "..." if len(note["content"]) > 100 else note["content"],
                    "tags": note["tags"],
                    "updated_at": note["updated_at"]
                })
        
        return {
            "result": {
                "count": len(results),
                "notes": results
            }
        }
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an MCP JSON-RPC request."""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "ListResources":
            return await self.list_resources()
        elif method == "ReadResource":
            return await self.read_resource(params["resourceId"])
        elif method == "ListTools":
            return await self.list_tools()
        elif method == "CallTool":
            return await self.call_tool(params["name"], params["parameters"])
        else:
            raise ValueError(f"Unsupported method: {method}")

    async def listen(self):
        """Simulates the MCP server listening for requests."""
        print(f"{self.name} v{self.version} is running...")
        print("This is a simulated server. In a real implementation, you would use:")
        print("  from modelcontextprotocol import Server")
        print("  server = Server(name='NoteMCPServer', version='1.0.0', features={...})")
        print("  @server.list_resources")
        print("  async def list_resources():")
        print("      # Your implementation")
        print("  server.listen()")

async def main():
    server = NoteMCPServer()
    await server.listen()
    
    # Example of how client interaction would work
    print("\nSimulating client requests:")
    
    # List resources
    print("\n> Client requests ListResources")
    response = await server.process_request({"method": "ListResources"})
    print(f"< Server responds: {json.dumps(response, indent=2)}")
    
    # Create a note
    print("\n> Client calls CreateNote tool")
    response = await server.process_request({
        "method": "CallTool",
        "params": {
            "name": "create_note",
            "parameters": {
                "title": "Meeting Notes",
                "content": "Discussed MCP integration plans for Q3",
                "tags": ["meeting", "planning"]
            }
        }
    })
    print(f"< Server responds: {json.dumps(response, indent=2)}")
    
    # Search notes
    print("\n> Client searches for 'meeting' notes")
    response = await server.process_request({
        "method": "CallTool",
        "params": {
            "name": "search_notes",
            "parameters": {
                "tags": ["meeting"]
            }
        }
    })
    print(f"< Server responds: {json.dumps(response, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main()) 