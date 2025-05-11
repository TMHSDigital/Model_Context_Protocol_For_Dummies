# MCP Features and Capabilities

MCP servers can expose three primary types of capabilities to AI models:

## 1. Resources

**Resources** are static or queryable content that the LLM can request. They represent data that can be read but not directly modified.

### Examples of Resources:
- File contents from a filesystem
- Documents from Google Drive or Dropbox
- Database query results
- Search results from repositories
- Web page content

### Resource Operations:
- `ListResources`: Discover available resources
- `ReadResource`: Retrieve content of a specific resource
- `SearchResources`: Find resources matching criteria

Resources provide AI models with access to up-to-date information from various data stores, allowing them to answer questions based on current data rather than just their training data.

## 2. Prompts/Workflows

**Prompts/Workflows** are pre-built templated dialogs or multi-step procedures that guide the user or model through a task.

### Characteristics:
- Consist of multiple steps with defined messages and action buttons
- Can include intermediate user inputs
- Follow a structured flow with conditional paths
- May include visual elements like selection menus

### Use Cases:
- Guided task completion (e.g., "Summarize Meeting Notes")
- Form-based data collection
- Multi-step approval processes
- Interactive data visualization workflows

Prompts/Workflows enable richer AI-powered chat interfaces that include tool-based interactions rather than pure freeform text.

## 3. Tools/Functions

**Tools/Functions** are executable functions that the model can invoke with arguments. These act similar to API calls, allowing the model to perform actions in external systems.

### Examples of Tool Functions:
- `search_github_issues(query, repository)` - Search GitHub issues
- `create_jira_ticket(title, description, priority)` - Create a new Jira ticket
- `generate_image(prompt, style, dimensions)` - Create an image with a diffusion model
- `send_email(recipient, subject, body)` - Compose and send an email

### Tool Implementation:
Functions are defined with:
- Name
- Description
- Required and optional parameters (with types)
- Return value type
- Execution logic

The MCP server exposes these tools via `ListTools` and executes them via `CallTool` requests.

## Feature Negotiation

During initialization, the MCP client and server negotiate which features are supported. A server declares the features it supports, and the client can then use only the available functionality.

For example, a simple file server might only support Resources, while a GitHub server might support both Resources (repo files) and Tools (issue creation).

## Security and Permissions

Each feature type has different security implications:

- **Resources**: May expose sensitive data; requires access control and user consent
- **Prompts/Workflows**: Must be transparent about what actions they'll perform
- **Tools/Functions**: Can execute code with potential side effects; requires authorization

The MCP specification emphasizes that hosts must implement appropriate security measures for each feature type, including user consent prompts, sandboxing, and transparent operation.

## Example: Database MCP Server

A database MCP server might expose:

1. **Resources**: 
   - Database tables as browsable resources
   - Query results as readable content

2. **Prompts/Workflows**:
   - "Create New Table" workflow with schema definition steps
   - "Data Analysis" prompt with visualization options

3. **Tools/Functions**:
   - `execute_query(sql, parameters)` - Run a SQL query
   - `explain_query_plan(sql)` - Get execution plan for a query
   - `export_results(format, destination)` - Export query results

This combination of features provides a complete interface for AI models to interact with databases in a controlled, secure manner. 