# Building and Deploying MCP Servers

This guide walks you through the process of developing, testing, and deploying your own MCP servers.

## Getting Started

MCP is designed to be developer-friendly with official SDKs available in multiple languages:

- TypeScript/Node.js
- Python
- Java
- Kotlin
- C#
- Swift

### Setting Up Your Environment

#### TypeScript/Node.js

1. Create a new project:
   ```bash
   mkdir my-mcp-server
   cd my-mcp-server
   npm init -y
   ```

2. Install the MCP SDK:
   ```bash
   npm install @modelcontextprotocol/sdk
   ```

#### Python

1. Create a new project:
   ```bash
   mkdir my-mcp-server
   cd my-mcp-server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the MCP SDK:
   ```bash
   pip install modelcontextprotocol-sdk
   ```

## Implementing a Basic MCP Server

### Step 1: Initialize a Server Instance

Start by creating a server instance with a name, version, and enabled features.

#### TypeScript Example:

```typescript
import { Server, ServerOptions } from '@modelcontextprotocol/sdk';

const options: ServerOptions = {
  name: 'MyCustomServer',
  version: '1.0.0',
  features: {
    resources: true,
    tools: true,
    prompts: false
  }
};

const server = new Server(options);
```

#### Python Example:

```python
from modelcontextprotocol import Server

server = Server(
    name="MyCustomServer",
    version="1.0.0",
    features={
        "resources": True,
        "tools": True,
        "prompts": False
    }
)
```

### Step 2: Register Handlers

Next, implement handlers for the operations your server supports.

#### TypeScript Resource Example:

```typescript
// Register resource handlers
server.registerResourceHandler({
  listResources: async () => {
    return {
      resources: [
        {
          id: 'example-data',
          name: 'Example Data',
          description: 'An example dataset'
        }
      ]
    };
  },
  
  readResource: async ({ resourceId }) => {
    if (resourceId === 'example-data') {
      return {
        content: 'This is example data from the MCP server.'
      };
    }
    
    throw new Error(`Resource ${resourceId} not found`);
  }
});
```

#### TypeScript Tool Example:

```typescript
// Register tool handlers
server.registerToolHandler({
  listTools: async () => {
    return {
      tools: [
        {
          name: 'greet',
          description: 'Returns a greeting message',
          parameters: {
            type: 'object',
            properties: {
              name: {
                type: 'string',
                description: 'Name to greet'
              }
            },
            required: ['name']
          }
        }
      ]
    };
  },
  
  callTool: async ({ name, parameters }) => {
    if (name === 'greet') {
      const { name: personName } = parameters as { name: string };
      return {
        result: `Hello, ${personName}!`
      };
    }
    
    throw new Error(`Tool ${name} not found`);
  }
});
```

#### Python Example:

```python
# Register resource handlers
@server.list_resources
async def list_resources():
    return {
        "resources": [
            {
                "id": "example-data",
                "name": "Example Data",
                "description": "An example dataset"
            }
        ]
    }

@server.read_resource
async def read_resource(resource_id):
    if resource_id == "example-data":
        return {
            "content": "This is example data from the MCP server."
        }
    
    raise ValueError(f"Resource {resource_id} not found")

# Register tool handlers
@server.list_tools
async def list_tools():
    return {
        "tools": [
            {
                "name": "greet",
                "description": "Returns a greeting message",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name to greet"
                        }
                    },
                    "required": ["name"]
                }
            }
        ]
    }

@server.call_tool
async def call_tool(name, parameters):
    if name == "greet":
        person_name = parameters["name"]
        return {
            "result": f"Hello, {person_name}!"
        }
    
    raise ValueError(f"Tool {name} not found")
```

### Step 3: Run the Server

Finally, start the server on your chosen transport.

#### TypeScript Example:

```typescript
// Start the server on stdio
server.listen();

// Or for HTTP+SSE
server.listen({
  transport: 'http',
  port: 3000
});
```

#### Python Example:

```python
# Start the server on stdio
server.listen()

# Or for HTTP+SSE
server.listen(transport="http", port=3000)
```

## Testing Your MCP Server

The MCP Inspector tool allows you to interact with your server for testing:

```bash
npx @modelcontextprotocol/inspector node build/index.js
```

The Inspector provides a UI to:
- List the server's resources and tools
- Invoke tools with parameters
- Examine JSON-RPC messages
- Debug responses

## Deployment Options

### Local Subprocess

For desktop applications, MCP servers often run as local subprocesses:

```bash
# TypeScript
node server.js

# Python
python server.py
```

### Docker Container

Package your server in a Docker container:

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

EXPOSE 3000
CMD ["node", "build/index.js"]
```

Build and run:
```bash
docker build -t my-mcp-server .
docker run -p 3000:3000 my-mcp-server
```

### Cloud Deployment

Deploy your MCP server on cloud platforms:

- **AWS Lambda**: Package as a serverless function behind API Gateway
- **Google Cloud Run**: Deploy container with HTTP transport
- **Azure Functions**: Use HTTP trigger for serverless deployment
- **Kubernetes**: Deploy container with a service for load balancing

## Security Best Practices

1. **Authentication**: Implement OAuth, API keys, or other auth mechanisms
2. **Authorization**: Check permissions before accessing resources
3. **Input Validation**: Validate all tool parameters
4. **Rate Limiting**: Prevent abuse with appropriate limits
5. **Logging**: Maintain audit logs of all operations
6. **Error Handling**: Return appropriate error messages without leaking internals

## Additional Frameworks

Several frameworks have added MCP support:

- **LangChain**: Provides MCP adapters so MCP tools can be used as LangChain Tools
- **JBang and Spring AI**: Support for Java-based MCP servers
- **OpenAI Agents SDK**: Includes classes to connect to MCP servers
- **Microsoft Copilot Studio**: Uses MCP servers via "Connector" abstractions

These frameworks can simplify development and integration of MCP servers into existing AI ecosystems. 