# MCP Configuration

This repo uses [mcporter](https://mcporter.dev) for Model Context Protocol (MCP) tool access.

## Setup

```bash
npm install -g mcporter
npm install -g @modelcontextprotocol/server-filesystem @modelcontextprotocol/server-memory @modelcontextprotocol/server-sequential-thinking
```

## Config

See `config/mcporter.json` for server definitions.

## Usage

```bash
# List available tools
mcporter list

# Call a tool
mcporter call filesystem.read_file path:README.md
mcporter call memory.create_entity "entity_type:\"project\" name:\"sig-botti\""
```

## Servers

- **filesystem** - Read/write files in workspace
- **memory** - Knowledge graph memory
- **thinking** - Sequential thinking & problem solving
