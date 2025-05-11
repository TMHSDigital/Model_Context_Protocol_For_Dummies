# Notable MCP Implementations

This document outlines key MCP server implementations, both reference examples and production-grade connectors.

## Reference Implementations

### Anthropic Reference Servers

The official [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) repository contains dozens of example servers in TypeScript and Python.

**Included servers:**
- **Filesystem** - Secure file access
- **GitHub/GitLab** - Repository management
- **Google Drive/Maps** - File and location services
- **Slack/Puppeteer** - Messaging and browser automation
- **PostgreSQL/Redis** - Database queries
- **Image generation (EverArt)**

**Strengths:**
- Broad coverage of examples
- Easy-to-customize code
- Open-source (MIT license)
- Built with official SDKs

**Limitations:**
- Primarily for demonstration
- Not all hardened for production use

## Enterprise Implementations

### GitHub MCP Server (Go)

In April 2025, GitHub published its own open-source server written in Go, which took over from Anthropic's GitHub example.

**Features:**
- Full GitHub API operations
- Customizable tool descriptions
- Code scanning capabilities
- `get_me` query for user data
- Tight integration with VS Code and GitHub Copilot

**Strengths:**
- Official support from GitHub
- Covers private repositories (with authentication)
- Designed specifically for developers
- Production-ready implementation

**Use cases:**
- AI code assistants
- Automated code maintenance
- Repository management

### AWS MCP Servers (Python)

Amazon released a suite of AWS-specific MCP servers for use in their developer tools.

**Key capabilities:**
- Infrastructure-as-code generation
- Cost analysis
- Athena query execution
- S3 object management
- Security configuration

**Strengths:**
- Deep cloud service integration
- Cost/security guidance built-in
- Works with AWS Q Developer CLI

**Use cases:**
- AI-assisted cloud development
- Code generation with AWS context

### Google MCP Toolbox & ADK (Java/Python)

Google Cloud offers an MCP Toolbox for Databases that exposes many database systems to agents.

**Supported databases:**
- Cloud SQL
- Spanner
- BigQuery
- AlloyDB

**Features:**
- Built-in OAuth2/OIDC security
- Connection pooling
- Telemetry integration
- Works with Google's Agent Development Kit (ADK)

**Strengths:**
- Enterprise-ready
- High performance
- Easy cloud integration

**Use cases:**
- Multi-agent pipelines that query corporate databases

### Docker MCP Server (Go/Shell)

Docker's GitHub organization curates many MCP servers, including one for Docker itself.

**Capabilities:**
- Container management
- Image operations
- Network configuration
- Volume management

**Strengths:**
- Convenient container orchestration
- Natural language to Docker CLI translation

**Use cases:**
- Autonomous DevOps assistants
- Infrastructure management

## Community Servers

The ecosystem is rapidly expanding with community-built servers for various purposes:

- **CRM systems:** Stripe, Chargebee
- **Web scraping:** Apify
- **Blockchain:** Various cryptocurrency APIs
- **GIS:** Geographic information systems
- **Personal tools:** Gmail, calendar, Figma

## Implementation Comparison

| **Server Implementation** | **Maintainer** | **Language** | **Key Capabilities** | **Use Cases / Notes** |
|---------------------------|----------------|--------------|----------------------|------------------------|
| *Reference Servers* | Anthropic (GitHub) | TypeScript, Python | Generic demos: file I/O, search, DB queries, image gen, web, chat | Broad examples, official SDK usage. Good for prototyping; not hardened |
| *GitHub MCP Server* | GitHub | Go | Full GitHub API (repos, files, issues); code scanning, `get_me` query | Strong GitHub integration; VS Code support. Great for code assistants |
| *AWS MCP Servers* | AWS (open source) | Python | AWS service operations (CloudFormation, S3, Athena, Bedrock Agents); security/cost advice | Agentic cloud development with AWS best practices |
| *Google DB Toolbox* | Google Cloud | Java/Python | Multi-DB queries (Spanner, BigQuery, Cloud SQL, etc.); integrates with ADK | Enterprise data access; used with Google ADK |
| *Docker MCP Server* | Docker Inc. | Go / Shell | Docker CLI actions: manage containers, images, networks | AI-driven DevOps and container management |
| *Community / Other* | Various (OSS) | Many | CRM (Stripe, Chargebee), CMS (Drupal, Ghost), spreadsheets (Excel), IoT (Home Assistant), code CI (CircleCI), etc. | Thousands of servers exist; pick per domain |

## Finding MCP Servers

Several resources can help you find existing MCP servers:

1. **Official Directory:** Anthropic curates an official MCP Servers list on GitHub
2. **Community Sites:** Websites like mcpserverfinder.com index servers by language and category
3. **Package Registries:** npm, PyPI, and other package managers contain MCP server implementations
4. **GitHub Search:** Search for "mcp-server" or "modelcontextprotocol" to find implementations

As of May 2025, over 1000 MCP server projects exist, reflecting broad community and vendor engagement. 