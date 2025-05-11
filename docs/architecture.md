# MCP Architecture

The Model Context Protocol (MCP) uses a **client-server architecture** similar to the Language Server Protocol (LSP). This document explains the key components and how they interact.

## Architectural Components

### 1. Host

The **Host** is the AI front-end application, such as:
- Claude Desktop
- Microsoft Copilot
- Custom AI agent applications
- IDEs with AI assistants

The host is responsible for:
- Managing the MCP client connections
- Handling user interactions
- Processing AI model responses
- Ensuring user consent and security

### 2. Client

Each host launches one or more MCP **Clients**, which:
- Maintain a 1:1 connection with an MCP server
- Handle communication protocol details
- Translate between the host application and server
- Negotiate capabilities during initialization

### 3. Server

An MCP **Server** is a separate process or service that:
- Exposes specific capabilities to AI models
- Responds to client requests
- Implements specific functionalities (file access, API calls, etc.)
- Declares supported features from the protocol

## Communication Protocol

MCP uses **JSON-RPC 2.0** messages for communication, which can be transmitted over:
- Standard I/O (stdio) - common for local servers running as subprocesses
- WebSocket/Server-Sent Events (SSE) - for network connections
- HTTP - for RESTful implementations

Each connection is **stateful**, meaning the server maintains context between requests.

### Protocol Flow

1. **Initialization**: The client connects to the server and they negotiate supported capabilities
2. **Resource/Tool Discovery**: The client queries what resources and tools the server provides
3. **Requests**: The host (via the client) issues JSON-RPC requests to the server
4. **Responses**: The server processes requests and returns structured data
5. **Context Integration**: The host incorporates server responses into the model's context

### Core JSON-RPC Methods

MCP defines standard methods including:
- `ListResources` - Discover available resources
- `ReadResource` - Request content of a specific resource
- `ListTools` - Discover available functions/tools
- `CallTool` - Execute a specific function with arguments

## Deployment Models

MCP servers can be deployed in various ways:

1. **Local Subprocess**:
   ```bash
   npx -y @modelcontextprotocol/server-filesystem <path>
   ```
   The server runs locally as a subprocess using stdio transport.

2. **Remote Service**:
   Servers can run as remote services and communicate via HTTP+SSE.

3. **Container/Cloud**:
   Many implementations can be packaged in Docker containers or deployed on cloud platforms.

## Security Considerations

MCP servers can potentially access sensitive data and run code, requiring strong safeguards:

- **User Consent**: Hosts must ensure users explicitly approve data access or tool invocation
- **Data Privacy**: Information sent to servers must be protected by access controls
- **Tool Authorization**: Users should be able to inspect and authorize tools before use
- **Transparency**: Any sampling or recursive querying must be visible to users

## Practical Example

When an LLM (through the host) wants to use a capability:

1. The model decides it needs to "Search my GitHub issues"
2. The host relays this request via `CallTool` to the GitHub MCP server
3. The server executes the search against the GitHub API
4. The server returns structured search results
5. The host incorporates these results into the model's context
6. The model can now respond based on the actual GitHub data

This architecture allows AI models to access real-time data and services in a standardized way, greatly enhancing their capabilities beyond their training data. 