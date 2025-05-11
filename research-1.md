# Model Context Protocol (MCP): A Technical Overview

*This research report was prepared by TM Hospitality Strategies, May 2025*

[![Model Context Protocol](https://img.shields.io/badge/Protocol-MCP-blue)](https://github.com/TMHSDigital/Model_Context_Protocol_For_Dummies)
[![Research Report](https://img.shields.io/badge/Document-Research-orange)](https://github.com/TMHSDigital/Model_Context_Protocol_For_Dummies/blob/main/research-1.md)

## Executive Summary

Model Context Protocol (MCP) is an open standard (introduced in late 2024 by Anthropic) that **standardizes how AI models connect to data sources and tools**. An MCP *server* is a lightweight program that exposes specific capabilities (data, prompts, or functions) over a JSON-RPC interface, enabling LLM applications to consume them. In the MCP architecture, an AI application (the *host*, e.g. Claude, an IDE, or an agent) uses a built-in *client* to open a stateful JSON-RPC connection to each MCP server. For example, a "Filesystem" MCP server might expose file-reading functions as tools, while a "Google Drive" MCP server exposes your Drive files as resources. In effect, MCP servers act like USB-C ports or "plugins" for AI – they let the model query your company wiki, run database queries, search code repositories, or invoke external APIs in a uniform way.

---

## Architecture and Protocol

MCP uses a **client–server architecture** similar to the Language Server Protocol (LSP). An MCP *host* (the AI front-end) launches one or more MCP *clients*, each of which maintains a 1:1 connection with an MCP *server* (a separate process or service). Communication is done via **JSON-RPC 2.0** messages (over stdio, WebSocket/SSE, or HTTP). Each connection is *stateful*, and during initialization the client and server negotiate supported capabilities (much like LSP). A server declares one or more features from the protocol: typically **Resources** (data payloads, e.g. files or database query results), **Prompts/Workflows** (templated instructions with interactive steps), and **Tools/Functions** (callable routines that the model can invoke). Clients may also support "sampling" (server-initiated prompts) for agent-like behaviors.

In practice, many MCP servers run as subprocesses on the same machine (using stdio transport), while others run remotely and communicate via HTTP+Server-Sent-Events (SSE). For example, OpenAI's Agents SDK lets you launch a local node/python server (using a command like `npx -y @modelcontextprotocol/server-filesystem <path>`) and will call `list_tools()` and `call_tool()` on it as needed. When an LLM (through the host) wants to use a capability, it issues a JSON-RPC request (e.g. "ListResources" or "CallTool") to the server via the client. The server responds with structured data (e.g. resource content or function output), which the host then incorporates into the model's context. In effect, **MCP servers present data and actions as "tools" to the language model**, and frameworks like OpenAI's Agents SDK automatically list these tools to the model and handle any function calls.

---

## Features and Security

### Server Capabilities

A server can expose three kinds of things:

* **Resources:** Static or queryable content (documents, file contents, database results, etc.) that the LLM can request. For instance, a "PostgreSQL" server may list tables as resources and return query output on demand.
* **Prompts/Workflows:** Pre-built templated dialogs or multi-step procedures (each with messages and action buttons) that guide the user or model through a task.
* **Tools/Functions:** Executable functions that the model can invoke with arguments (like API calls or scripts). For example, a "GitHub" server provides tools to search repos or create issues, and an "Image Generator" server provides a `generate_image` tool that calls a diffusion model.

### Protocol Details

The MCP specification mandates JSON-RPC 2.0, with methods such as `ListResources`, `ReadResource`, `ListTools`, and `CallTool` defined in the schema. Connections are typically long-lived and bi-directional. The protocol also includes utility messages for configuration, progress updates, cancellations, logging, and error reporting. Servers must advertise their "manifest" (name, version, capabilities) to clients, which then trust and use them accordingly.

### Security/Trust

Because MCP servers can potentially access arbitrary data and run code, strong safeguards are required. The MCP spec explicitly emphasizes user consent and data privacy: hosts must ensure users explicitly approve any data sharing or tool invocation. For example, the host should prompt the user before a server reads private files or before an LLM tool call is executed. Data sent to servers or out-of-process must be protected by access controls. Tools (functions) are treated as untrusted code: hosts should let users inspect and authorize them before use. Finally, any LLM sampling or recursive querying must be transparent: users control whether a server can initiate another LLM request and see its prompt. In short, **MCP makes the connection standardized, but actual deployments must implement robust consent flows, authentication, and sandboxing**. For example, Microsoft's Copilot Studio integrates MCP servers via a secure "Connector" framework, applying enterprise controls like virtual network isolation, data-loss prevention, and multi-factor auth. Similarly, Google's MCP database toolbox uses OAuth2/OIDC and OpenTelemetry auditing for security.

---

## Interaction with LLMs and Agents

From the LLM's perspective, MCP servers function like an external tool library. Before running, the host queries each connected server for its capabilities. For instance, an OpenAI Agent will call `list_tools()` on each MCP server so that the model "knows" what functions it can call. When the LLM decides to use a tool (e.g. "Search my GitHub issues"), the host relays the request via `CallTool` to the server and returns the result as part of the prompt. This model-to-tool invocation is akin to OpenAI's function-calling feature: the difference is that MCP is a generic, server-based protocol, not tied to any single model provider.

Because MCP is decoupled from any particular LLM API, agents and chat tools can mix and match models. For example, Claude Desktop, Microsoft Copilot, or custom Python agents can all consume the same MCP servers as long as they implement the protocol. Conversely, a single LLM can use multiple servers: an AI assistant could pull data from Google Drive and query a company database in one session, simply by calling two different MCP servers. In multi-agent frameworks, MCP servers act as shared middleware: agents invoke server tools (via JSON-RPC) as needed, and the servers return structured data that the agent incorporates back into its reasoning.

![MCP Architecture](https://via.placeholder.com/800x400?text=Google+MCP+Toolbox+Architecture)
*Figure: Google's open-source MCP "Toolbox for Databases" connects AI agents (via its ADK) to many database systems (Cloud SQL, Spanner, BigQuery, etc.) through a unified MCP server interface.*

---

## Practical Use Cases

MCP servers enable **real-world AI applications** to plug into live data and services. Some examples include:

### Data Access & Retrieval

* **File Systems and Cloud Drives**: Let an AI assistant read local files or Google Drive/Dropbox documents. "Everything Search" servers provide fast file search on desktop (via Everything or `locate`).

* **Databases and Knowledge Bases**: A database MCP (Postgres, MySQL, BigQuery, etc.) allows the model to query enterprise data warehouses with natural language. Similarly, a knowledge base or vector database server can retrieve relevant text chunks for context (e.g. a "Memory" or "Pinecone" server). These empower LLMs to answer questions using up-to-date, internal data instead of outdated training knowledge.

### Development & Code

* **Source Code Management**: GitHub provides an official MCP server (Go) that lets Claude or other agents list repositories, read code files, open PRs, or even run code scanning features. Likewise, a GitLab/Jira MCP server can search issues and commits.

* **DevOps and Infrastructure**: Docker's MCP server allows an AI to manage containers and images by calling Docker commands, which could help automate infrastructure tasks. Other dev-related servers include StackOverflow search, CI/CD integration (CircleCI), and project tracking (Linear, Asana).

### Web & External APIs

* **Web Interaction**: "Fetch" servers can scrape or retrieve web pages in a format optimized for LLMs. Search servers (Brave, Google, GitHub Search) let the AI perform web or code searches.

* **Mapping and Communication**: Mapping and geolocation tasks can use a Google Maps/Place details server. There are even MCP servers for social media (Discord, Slack) and communications (Gmail).

### Productivity & Business

* **Business Applications**: CRM servers (Salesforce, HubSpot, Chargebee) allow an assistant to invoice customers or retrieve account info. Project tools (Atlassian, Monday.com) can expose issues and tasks. Even home automation apps (Home Assistant) have MCP integrations.

### Workflows/Chatbots

MCP can also model guided interactions. A server might offer a "Summarize Meeting Notes" prompt or a multi-step approval workflow, with buttons and inputs, that the user can execute within the chat UI. For example, an MCP "Everything" server could prompt: *"Select a file to attach"* then return its contents as a resource. These capabilities let developers build richer AI-powered chat interfaces that include tool-based interactions rather than pure freeform text.

---

## Notable MCP Implementations

Many MCP servers have been released, both as reference examples and production-grade connectors. Key implementations include:

### Reference Servers (Anthropic)

The official [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) repository contains dozens of example servers in TypeScript and Python. These "reference" servers demonstrate core capabilities: e.g. **Filesystem** (secure file access), **GitHub/GitLab** (repo management), **Google Drive/Maps** (file and location services), **Slack/Puppeteer** (messaging and browser automation), **PostgreSQL/Redis** (database queries), **Image generation (EverArt)**, and more. They are open-source (MIT) and built with the official SDKs.

**Strengths:** broad coverage of examples and easy-to-customize code.  
**Limitations:** mostly for demonstration; not hardened for all production uses.

### GitHub MCP Server (GitHub, Go)

In April 2025 GitHub published its own open-source server (written in Go), taking over Anthropic's GitHub example. It supports all GitHub API operations, plus added features like customizable tool descriptions, code scanning, and a new `get_me` query for user data. This server is tightly integrated into VS Code and GitHub Copilot environments.

**Strengths:** official support, covers private repos (with auth), designed for developers.  
**Use cases:** AI code assistants, automated code maintenance.

### AWS MCP Servers (AWS, Python)

Amazon released a suite of **AWS-specific MCP servers** for use in their developer tools. These open-source servers let agents perform cloud tasks (e.g. generate infrastructure-as-code, analyze costs, run Athena queries, manage S3 objects) while enforcing AWS best practices and security controls. Each server focuses on a domain (e.g. compute, databases, security), collectively giving an AI the ability to configure AWS resources. AWS also added MCP support to its Q Developer CLI.

**Strengths:** deep cloud service integration, cost/security guidance built-in.  
**Use cases:** AI-assisted cloud development, code generation with AWS context.

### Google MCP Toolbox & ADK (Google, Java/Python)

Google Cloud offers an **MCP Toolbox for Databases** (open source) that exposes many database systems (Cloud SQL, Spanner, BigQuery, AlloyDB, etc.) to agents. Built on their new Agent Development Kit (ADK), it simplifies connecting LLMs to enterprise data. The Toolbox includes built-in OAuth2/OIDC security, connection pooling, and telemetry. Google also notes that *"ADK supports MCP, enabling secure, two-way connections between your data sources and AI agents."*

**Strengths:** enterprise-ready, high performance, easy cloud integration.  
**Use cases:** multi-agent pipelines that query corporate databases.

### Docker MCP Server (Docker, Go/Shell)

Docker's GitHub org curates many MCP servers, including one for **Docker** itself. This server lets an agent manage Docker containers, images, networks and volumes via natural language. For example, an AI could create and run a container by simply describing it, with the server translating to Docker CLI commands.

**Strengths:** convenient container orchestration.  
**Use cases:** autonomous DevOps assistants.

### Other Community Servers

The ecosystem is rapidly expanding. There are community-built servers for CRM (Stripe, Chargebee), web scraping (Apify), blockchain APIs, GIS, even personal tools (Gmail, calendar, Figma). Many server implementations exist (in languages like Go, Python, Node, .NET) – see the [MCP Servers directory](https://github.com/modelcontextprotocol/servers) for hundreds of projects.

---

## Implementation Comparison Table

| **Server Implementation** | **Maintainer** | **Language** | **Key Capabilities** | **Use Cases / Notes** |
| ------------------------- | -------------- | ------------ | -------------------- | --------------------- |
| *Reference (Filesystem, Google Drive, Slack, etc.)* | Anthropic (GitHub) | TypeScript, Python | Generic demos: file I/O, search, DB queries, image gen, web, chat, etc. | Broad examples, official SDK usage. Good for prototyping; not hardened. |
| *GitHub MCP Server* | GitHub | Go | Full GitHub API (repos, files, issues); code scanning, `get_me` query | Strong GitHub integration; VS Code support. Great for code assistants. |
| *AWS MCP Servers* | AWS (open source) | Python | AWS service operations (CloudFormation, S3, Athena, Bedrock Agents); security/cost advice | Agentic cloud development with AWS best practices. |
| *Google DB Toolbox* | Google Cloud | Java/Python | Multi-DB queries (Spanner, BigQuery, Cloud SQL, etc.); integrates with ADK | Enterprise data access; used with Google ADK. |
| *Docker MCP Server* | Docker Inc. | Go / Shell | Docker CLI actions: manage containers, images, networks | AI-driven DevOps and container management. |
| *Community / Other* | Various (OSS) | Many | CRM (Stripe, Chargebee), CMS (Drupal, Ghost), spreadsheets (Excel), IoT (Home Assistant), code CI (CircleCI), etc. | Thousands of servers exist; pick per domain (see directory). |

---

## Developing and Deploying MCP Servers

MCP is designed to be developer-friendly. Official SDKs are available in many languages (TypeScript/Node, Python, Java, Kotlin, C#, Swift). These SDKs provide base classes for servers and clients, JSON-RPC schemas, and helper functions. To build a server, you typically:

1. **Initialize a server instance** with a name, version, and enabled features (resources, prompts, tools).
2. **Register handlers** for each request type (e.g. `ListResources`, `ReadResource`, `ListTools`, `CallTool`). In code you declare what resources and tools you expose, and implement the callback logic.
3. **Run the server** on a chosen transport. For local desktop use, many servers run on **stdio** as a subprocess. For example, a Node.js server can be launched via `node` or `npx` and will listen on its stdin/stdout. For remote deployment, servers can listen on HTTP+SSE on a port or domain.

For example, in TypeScript one might use the MCP SDK to define a server and then launch it with:

```bash
npx @modelcontextprotocol/inspector node build/index.js
```

which starts an interactive MCP Inspector connected to your server. The Inspector tool (provided by Anthropic) is extremely helpful: it lets you list the server's resources/tools, invoke them, and debug the JSON-RPC messages. Alternatively, Claude Desktop users can add a server by editing the `mcpServers` section of the app's configuration (pointing to the server's executable and args).

Because MCP uses standard I/O or HTTP, servers can be packaged in Docker containers or deployed on cloud platforms. Many implementations provide Docker images (e.g. GitHub's official server and others on Docker Hub) or Kubernetes Helm charts. Authentication and credentials are handled externally (e.g. AWS roles or OAuth tokens) – MCP itself only transmits data over its connection.

### Tools & Frameworks

In addition to the language SDKs, several frameworks have added MCP support. LangChain provides MCP adapters so that MCP tools can be used as LangChain Tools. JBang and Spring AI have support to easily run Java-based MCP servers. OpenAI's Agents SDK (Python) includes classes (`MCPServerStdio`, `MCPServerSse`) to connect to servers. Microsoft's Copilot Studio uses MCP servers via a "Connector" abstraction with enterprise controls. In short, existing AI/agent frameworks now treat MCP servers as first-class plugins.

---

## Recent Developments and Industry Support

Since its debut in late 2024, MCP has seen rapid adoption and support across the AI ecosystem. Anthropic open-sourced the specification, SDKs, and sample servers in Nov 2024, and shared pre-built servers for common tools like Google Drive, Slack, GitHub, Postgres and Puppeteer. Early adopters in industry include Block and Apollo, and developer platforms Zed, Replit, Codeium and Sourcegraph are integrating MCP to enhance code assistance.

Notable 2025 milestones include:

* **GitHub (Apr 2025):** Released the official "GitHub MCP Server", a complete Go-based server for GitHub APIs. This supersedes Anthropic's example and is now supported in VS Code Copilot.

* **AWS (Apr 2025):** Added MCP support to its Amazon Q Developer CLI and open-sourced a set of "AWS MCP Servers" for cloud tasks. These servers embed AWS well-architected guidance, security checks, and cost-optimization prompts into AI assistants.

* **Microsoft (Mar 2025):** Announced MCP integration in **Copilot Studio**. MCP servers can be added as enterprise-grade "Connector" components with Azure networking and DLP controls, letting agents query internal data sources through the MCP protocol.

* **Google (2024–25):** Updated its AI toolkits to embrace MCP. The Google Cloud "Toolbox for Databases" now runs as an MCP server (permitting agents to query AlloyDB, Spanner, etc.). Their new Agent Development Kit (ADK) includes native MCP support, explicitly enabling "secure, two-way connections" between AI agents and data.

* **OpenAI (2025):** The OpenAI Agents SDK (for its chat models) includes built-in MCP connectors. In fact, InfoQ reports that OpenAI and Google have publicly announced support for MCP, and frameworks like LangChain4j, Quarkus, Spring AI and ZenML quickly added MCP support in late 2024/early 2025.

* **Ecosystem growth:** New directories and catalogs have emerged. Anthropic curates an official MCP Servers list on GitHub, while community sites (e.g. mcpserverfinder.com) index servers by language and category. Over 1000 MCP server projects now exist, reflecting broad community and vendor engagement.

---

## Conclusion

In summary, MCP servers are rapidly becoming the de facto way to plug AI systems into the real world. By providing a USB‑C‑like standard for data and tools, MCP is accelerating the creation of agentic AI workflows. Developers can build and deploy MCP servers using the rich SDKs and tools now available, and leverage a growing marketplace of existing servers in production.

---

*This research report was prepared by TM Hospitality Strategies in May 2025.*

**Sources:** Official MCP documentation and spec; Anthropic and Google announcements; GitHub and AWS blogs; Microsoft Copilot blog; AWS news; InfoQ tech news; and open-source GitHub repositories (modelcontextprotocol, docker/mcp-servers).
