# Xano MCP Server for Smithery

A Model Context Protocol (MCP) server for integrating Xano databases with Smithery, enabling Claude AI to interact with Xano databases.

## Overview

This MCP server provides a bridge between Claude AI (via Smithery) and Xano databases, allowing Claude to perform operations on Xano data through a standardized interface. The server implements the Model Context Protocol, making it compatible with Smithery's serverless deployment model.

## Features

- Complete Xano API integration
- Support for both stdio and WebSocket transport methods
- Comprehensive database operations (tables, schemas, records)
- File management capabilities
- Request history tracking
- Import/export functionality

## Available Tools

The server provides the following categories of tools:

### Instance and Database Operations
- List Xano instances
- Get instance details
- List databases/workspaces
- Get workspace details

### Table Operations
- List tables
- Get table details
- Create, update, and delete tables

### Table Schema Operations
- Get and update table schemas
- Add, rename, and delete fields

### Table Index Operations
- List, create, and delete various index types (btree, unique, search, spatial, vector)

### Table Content Operations
- Browse and search table content
- CRUD operations on records (create, read, update, delete)
- Bulk operations for efficiency

### File Operations
- List, upload, and delete files
- Get file details

### Request History Operations
- Browse and search request history

### Workspace Import/Export
- Export and import workspaces and schemas

## Installation

### Prerequisites

- Python 3.10 or higher
- Smithery CLI (for deployment)
- Xano API token

### Local Installation

```bash
# Clone the repository
git clone https://github.com/roboulos/xano-mcp.git
cd xano-mcp

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running Locally

```bash
# Run with stdio transport (default)
python -m src.xano_mcp --token YOUR_XANO_API_TOKEN

# Run with WebSocket transport
python -m src.xano_mcp --token YOUR_XANO_API_TOKEN --transport websocket --port 8765

# Enable debug mode
python -m src.xano_mcp --token YOUR_XANO_API_TOKEN --debug
```

### Using with Smithery

1. Deploy the MCP server to Smithery:

```bash
smithery deploy
```

2. Configure the server with your Xano API token in the Smithery dashboard

3. Use the server in your Smithery workflows

## Security Considerations

- Store your Xano API token securely
- Use environment variables for sensitive information when possible
- Consider using access controls on your Xano database
- The MCP server has full access to your Xano database, so deploy it securely

## Configuration

The server can be configured using command-line arguments or environment variables:

| Option | Environment Variable | Description |
|--------|---------------------|-------------|
| --token | XANO_API_TOKEN | Your Xano API token (required) |
| --transport | MCP_TRANSPORT | Transport method: stdio or websocket (default: stdio) |
| --port | MCP_PORT | Port for WebSocket server (default: 8765) |
| --debug | MCP_DEBUG | Enable debug mode for verbose logging |

## Docker Support

You can run the server using Docker:

```bash
# Build the Docker image
docker build -t xano-mcp .

# Run with stdio transport
docker run -e XANO_API_TOKEN=YOUR_TOKEN xano-mcp

# Run with WebSocket transport
docker run -e XANO_API_TOKEN=YOUR_TOKEN -p 8765:8765 xano-mcp --transport websocket --port 8765
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
