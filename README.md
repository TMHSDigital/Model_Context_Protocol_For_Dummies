<h1 align="center">Model Context Protocol (MCP) For Dummies</h1>

<div align="center">
  <img src="docs/images/mcp-banner.png" alt="Model Context Protocol Banner" width="100%">
  <br><br>
  
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
  <a href="https://github.com/TMHSDigital"><img src="https://img.shields.io/badge/Maintained%20by-TM%20Hospitality%20Strategies-brightgreen" alt="Maintained by TM Hospitality Strategies"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
  <a href="https://commonmark.org"><img src="https://img.shields.io/badge/Made%20with-Markdown-1f425f.svg" alt="Made with Markdown"></a>
  <br>
  <img src="https://img.shields.io/github/last-commit/TMHSDigital/Model_Context_Protocol_For_Dummies" alt="GitHub last commit">
  <img src="https://img.shields.io/github/issues/TMHSDigital/Model_Context_Protocol_For_Dummies" alt="GitHub issues">
  <img src="https://img.shields.io/github/languages/top/TMHSDigital/Model_Context_Protocol_For_Dummies" alt="GitHub top language">
</div>

> A comprehensive guide to understanding and implementing the Model Context Protocol (MCP)

## 🚀 Start Here: Visual Learning Path

New to MCP? Follow this learning path to quickly understand the protocol:

1. **[Getting Started Guide](docs/getting-started.md)** - Visual explanation of MCP with diagrams and code walkthrough
2. **[Architecture Details](docs/architecture.md)** - Deeper dive into the client-server architecture
3. **[Code Examples](#quick-example)** - See MCP in action with working code
4. **[Use Cases](docs/use-cases.md)** - Explore real-world applications

The [Getting Started Guide](docs/getting-started.md) bridges the gap between MCP concepts and implementation with sequence diagrams and annotated code examples.

## What is MCP?

Model Context Protocol (MCP) is an open standard (introduced in late 2024 by Anthropic) that **standardizes how AI models connect to data sources and tools**. This repository aims to provide a clear, comprehensive explanation of MCP, its architecture, implementations, and practical applications.

An MCP *server* is a lightweight program that exposes specific capabilities (data, prompts, or functions) over a JSON-RPC interface, enabling LLM applications to consume them. In the MCP architecture:

- An AI application (the *host*, e.g. Claude, an IDE, or an agent) uses a built-in *client* to open a stateful JSON-RPC connection to each MCP server
- MCP servers act like USB-C ports or "plugins" for AI – they let the model query your company wiki, run database queries, search code repositories, or invoke external APIs in a uniform way

## Repository Contents

```
Model_Context_Protocol_For_Dummies/
├── docs/                          # Documentation
│   ├── architecture.md            # Client-server architecture details
│   ├── features.md                # Resources, Prompts/Workflows, and Tools
│   ├── implementations.md         # Notable MCP server implementations
│   ├── development-guide.md       # Building and deploying MCP servers
│   └── use-cases.md               # Real-world applications and examples
├── examples/                      # Code examples
│   ├── typescript/                # TypeScript examples
│   │   ├── simple-server.ts       # Weather data MCP server
│   │   └── monday-server.ts       # Monday.com integration MCP server
│   └── python/                    # Python examples
│       ├── simple_server.py       # Note-taking MCP server
│       └── monday_server.py       # Monday.com integration MCP server
├── CODE_OF_CONDUCT.md             # Code of conduct
├── CONTRIBUTING.md                # Contribution guidelines
├── LICENSE                        # MIT License
├── README.md                      # This file
└── research-1.md                  # Technical overview of MCP
└── research-2.md                  # Monday.com integration research
```

## Getting Started

Browse the repository to learn about:

| Topic | Description |
|-------|-------------|
| [Architecture](docs/architecture.md) | Understanding the client-server architecture and protocol details |
| [Features](docs/features.md) | Resources, Prompts/Workflows, and Tools/Functions |
| [Implementations](docs/implementations.md) | Notable MCP server implementations |
| [Development Guide](docs/development-guide.md) | Building and deploying your own MCP servers |
| [Use Cases](docs/use-cases.md) | Real-world applications and examples |
| [Research Report](research-1.md) | Comprehensive technical overview of MCP |
| [Monday.com Integration](research-2.md) | Technical feasibility study on Monday.com MCP integration |

## Quick Example

Here's a brief example of what an MCP server looks like in TypeScript:

```typescript
import { Server } from '@modelcontextprotocol/sdk';

const server = new Server({
  name: 'SimpleServer',
  version: '1.0.0',
  features: { resources: true, tools: true }
});

// Register a simple tool
server.registerToolHandler({
  listTools: async () => ({
    tools: [{
      name: 'greet',
      description: 'Returns a greeting',
      parameters: {
        type: 'object',
        properties: { name: { type: 'string', description: 'Name to greet' } },
        required: ['name']
      }
    }]
  }),
  callTool: async ({ name, parameters }) => {
    if (name === 'greet') {
      return { result: `Hello, ${parameters.name}!` };
    }
    throw new Error(`Unknown tool: ${name}`);
  }
});

server.listen();
```

## Integration Examples

### Monday.com Integration

We've implemented an MCP server for Monday.com that demonstrates how to connect AI models to project management data:

```typescript
// Sample Monday.com MCP tool call
const response = await mondayServer.callTool({
  name: 'create_item',
  parameters: {
    board_id: 1234567890,
    group_id: "topics",
    item_name: "Implement MCP integration",
    column_values: {
      status: "Working on it",
      date: "2025-06-01",
      person: "12345"
    }
  }
});
```

This integration enables AI agents to:
- Query project data (boards, tasks, team members)
- Create and update tasks using natural language
- Generate reports and insights from project metrics
- Follow guided workflows for project management processes

See [Monday.com Integration Research](research-2.md) for implementation details and [examples/typescript/monday-server.ts](examples/typescript/monday-server.ts) for code examples.

## Why Use MCP?

- **Standardized Interface**: Consistent way for AI models to access tools and data
- **Model Agnostic**: Works with Claude, GPT, and other LLMs
- **Composable**: Mix and match servers based on your needs
- **Secure**: Built with user consent and data privacy in mind
- **Extensible**: Build custom servers for your specific use cases

## Contributing

We welcome contributions to improve this resource! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This repository is licensed under [MIT License](LICENSE).

---

<div align="center">
  <sub>Maintained with ❤️ by <a href="https://github.com/TMHSDigital">TM Hospitality Strategies</a></sub>
</div>

