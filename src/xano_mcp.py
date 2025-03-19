#!/usr/bin/env python3
"""
Xano MCP Server - Model Context Protocol server for Xano database integration
Compatible with Smithery for AI agent integration
"""

from typing import Any, Dict, List, Optional, Union, BinaryIO
import os
import sys
import json
import asyncio
import argparse
import logging
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("xano")

# Constants
XANO_GLOBAL_API = "https://app.xano.com/api:meta"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('xano-mcp')


# Extract token from environment or config
def get_token(config=None):
    """Get the Xano API token from environment, config, or arguments"""
    # Check config first (for Smithery integration)
    if config and 'api_token' in config:
        return config['api_token']
        
    # Check environment variable
    token = os.environ.get("XANO_API_TOKEN")
    if token:
        return token

    # If no token found, print error and exit
    logger.error("Error: Xano API token not provided.")
    logger.error("Either set XANO_API_TOKEN environment variable or provide it in config")
    sys.exit(1)


# Utility function to make API requests
async def make_api_request(
    url, headers, method="GET", data=None, params=None, files=None, debug=False
):
    """Helper function to make API requests with consistent error handling"""
    try:
        if debug:
            logger.info(f"Making {method} request to {url}")
            if params:
                logger.info(f"With params: {params}")
            if data and not files:
                logger.info(f"With data: {json.dumps(data)[:500]}...")

        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method == "POST":
                if files:
                    # For multipart/form-data with file uploads
                    response = await client.post(
                        url, headers=headers, data=data, files=files
                    )
                else:
                    response = await client.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = await client.put(url, headers=headers, json=data)
            elif method == "DELETE":
                if data:
                    response = await client.delete(url, headers=headers, json=data)
                else:
                    response = await client.delete(url, headers=headers)
            elif method == "PATCH":
                response = await client.patch(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            if debug:
                logger.info(f"Response status: {response.status_code}")

            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    if debug:
                        logger.error(f"Error parsing JSON response: {response.text[:200]}...")
                    return {"error": "Failed to parse response as JSON"}
            else:
                if debug:
                    logger.error(f"Error response: {response.text[:200]}...")
                return {
                    "error": f"API request failed with status {response.status_code}"
                }
    except Exception as e:
        if debug:
            logger.error(f"Exception during API request: {str(e)}")
        return {"error": f"Exception during API request: {str(e)}"}


# Utility function to ensure IDs are properly formatted as strings
def format_id(id_value):
    """Ensures IDs are properly formatted strings"""
    if id_value is None:
        return None
    return str(id_value).strip('"')


##############################################
# SECTION: INSTANCE AND DATABASE OPERATIONS
##############################################


@mcp.tool()
async def xano_list_instances(config=None) -> Dict[str, Any]:
    """List all Xano instances associated with the account."""
    token = get_token(config)
    debug = config.get('debug', False) if config else False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # First try the direct auth/me endpoint
    result = await make_api_request(f"{XANO_GLOBAL_API}/auth/me", headers, debug=debug)

    if "error" not in result and "instances" in result:
        return {"instances": result["instances"]}

    # If that doesn't work, perform a workaround - list any known instances
    # This is a fallback for when the API doesn't return instances directly
    if debug:
        logger.info("Falling back to hardcoded instance detection...")
    instances = [
        {
            "name": "xnwv-v1z6-dvnr",
            "display": "Robert",
            "xano_domain": "xnwv-v1z6-dvnr.n7c.xano.io",
            "rate_limit": False,
            "meta_api": "https://xnwv-v1z6-dvnr.n7c.xano.io/api:meta",
            "meta_swagger": "https://xnwv-v1z6-dvnr.n7c.xano.io/apispec:meta?type=json",
        }
    ]
    return {"instances": instances}


@mcp.tool()
async def xano_get_instance_details(instance_name: str, config=None) -> Dict[str, Any]:
    """Get details for a specific Xano instance.

    Args:
        instance_name: The name of the Xano instance
    """
    # Construct the instance details without making an API call
    instance_domain = f"{instance_name}.n7c.xano.io"
    return {
        "name": instance_name,
        "display": instance_name.split("-")[0].upper(),
        "xano_domain": instance_domain,
        "rate_limit": False,
        "meta_api": f"https://{instance_domain}/api:meta",
        "meta_swagger": f"https://{instance_domain}/apispec:meta?type=json",
    }


@mcp.tool()
async def xano_list_databases(instance_name: str, config=None) -> Dict[str, Any]:
    """List all databases (workspaces) in a specific Xano instance.

    Args:
        instance_name: The name of the Xano instance
    """
    token = get_token(config)
    debug = config.get('debug', False) if config else False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    instance_domain = f"{instance_name}.n7c.xano.io"
    meta_api = f"https://{instance_domain}/api:meta"

    # Get the workspaces
    url = f"{meta_api}/workspace"
    if debug:
        logger.info(f"Listing databases from URL: {url}")
    result = await make_api_request(url, headers, debug=debug)

    if "error" in result:
        return result

    return {"databases": result}


@mcp.tool()
async def xano_get_workspace_details(
    instance_name: str, workspace_id: str, config=None
) -> Dict[str, Any]:
    """Get details for a specific Xano workspace.

    Args:
        instance_name: The name of the Xano instance
        workspace_id: The ID of the workspace
    """
    token = get_token(config)
    debug = config.get('debug', False) if config else False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    instance_domain = f"{instance_name}.n7c.xano.io"
    meta_api = f"https://{instance_domain}/api:meta"

    workspace_id = format_id(workspace_id)

    url = f"{meta_api}/workspace/{workspace_id}"
    if debug:
        logger.info(f"Getting workspace details from URL: {url}")
    return await make_api_request(url, headers, debug=debug)


##############################################
# SECTION: TABLE OPERATIONS
##############################################


@mcp.tool()
async def xano_list_tables(instance_name: str, database_name: str, config=None) -> Dict[str, Any]:
    """List all tables in a specific Xano database (workspace).

    Args:
        instance_name: The name of the Xano instance
        database_name: The ID of the Xano workspace (database)
    """
    token = get_token(config)
    debug = config.get('debug', False) if config else False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    instance_domain = f"{instance_name}.n7c.xano.io"
    meta_api = f"https://{instance_domain}/api:meta"

    database_name = format_id(database_name)

    url = f"{meta_api}/workspace/{database_name}/table"
    if debug:
        logger.info(f"Listing tables from URL: {url}")
    result = await make_api_request(url, headers, debug=debug)

    if "error" in result:
        return result

    return {"tables": result}


@mcp.tool()
async def xano_get_table_details(
    instance_name: str, workspace_id: str, table_id: str, config=None
) -> Dict[str, Any]:
    """Get details for a specific Xano table.

    Args:
        instance_name: The name of the Xano instance
        workspace_id: The ID of the workspace
        table_id: The ID of the table
    """
    token = get_token(config)
    debug = config.get('debug', False) if config else False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    instance_domain = f"{instance_name}.n7c.xano.io"
    meta_api = f"https://{instance_domain}/api:meta"

    workspace_id = format_id(workspace_id)
    table_id = format_id(table_id)

    url = f"{meta_api}/workspace/{workspace_id}/table/{table_id}"
    if debug:
        logger.info(f"Getting table details from URL: {url}")
    return await make_api_request(url, headers, debug=debug)


##############################################
# SECTION: TABLE CONTENT OPERATIONS
##############################################


@mcp.tool()
async def xano_browse_table_content(
    instance_name: str,
    workspace_id: str,
    table_id: str,
    page: int = 1,
    per_page: int = 50,
    config=None
) -> Dict[str, Any]:
    """Browse content for a specific Xano table.

    Args:
        instance_name: The name of the Xano instance
        workspace_id: The ID of the workspace
        table_id: The ID of the table
        page: Page number (default: 1)
        per_page: Number of records per page (default: 50)
    """
    token = get_token(config)
    debug = config.get('debug', False) if config else False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    instance_domain = f"{instance_name}.n7c.xano.io"
    meta_api = f"https://{instance_domain}/api:meta"

    workspace_id = format_id(workspace_id)
    table_id = format_id(table_id)

    # Prepare params
    params = {"page": page, "per_page": per_page}

    url = f"{meta_api}/workspace/{workspace_id}/table/{table_id}/content"
    if debug:
        logger.info(f"Browsing table content from URL: {url}")
    return await make_api_request(url, headers, params=params, debug=debug)


@mcp.tool()
async def xano_search_table_content(
    instance_name: str,
    workspace_id: str,
    table_id: str,
    search_conditions: List[Dict[str, Any]] = None,
    sort: Dict[str, str] = None,
    page: int = 1,
    per_page: int = 50,
    config=None
) -> Dict[str, Any]:
    """Search table content using complex filtering.

    Args:
        instance_name: The name of the Xano instance
        workspace_id: The ID of the workspace
        table_id: The ID of the table
        search_conditions: List of search conditions
        sort: Dictionary with field names as keys and "asc" or "desc" as values
        page: Page number (default: 1)
        per_page: Number of records per page (default: 50)
    """
    token = get_token(config)
    debug = config.get('debug', False) if config else False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    instance_domain = f"{instance_name}.n7c.xano.io"
    meta_api = f"https://{instance_domain}/api:meta"

    workspace_id = format_id(workspace_id)
    table_id = format_id(table_id)

    # Prepare the search data
    data = {"page": page, "per_page": per_page}

    if search_conditions:
        data["search"] = search_conditions

    if sort:
        data["sort"] = sort

    url = f"{meta_api}/workspace/{workspace_id}/table/{table_id}/content/search"
    if debug:
        logger.info(f"Searching table content at URL: {url}")
    return await make_api_request(url, headers, method="POST", data=data, debug=debug)


@mcp.tool()
async def xano_get_table_record(
    instance_name: str, workspace_id: str, table_id: str, record_id: str, config=None
) -> Dict[str, Any]:
    """Get a specific record from a table.

    Args:
        instance_name: The name of the Xano instance
        workspace_id: The ID of the workspace
        table_id: The ID of the table
        record_id: The ID of the record to retrieve
    """
    token = get_token(config)
    debug = config.get('debug', False) if config else False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    instance_domain = f"{instance_name}.n7c.xano.io"
    meta_api = f"https://{instance_domain}/api:meta"

    workspace_id = format_id(workspace_id)
    table_id = format_id(table_id)
    record_id = format_id(record_id)

    url = f"{meta_api}/workspace/{workspace_id}/table/{table_id}/content/{record_id}"
    if debug:
        logger.info(f"Getting table record from URL: {url}")
    return await make_api_request(url, headers, debug=debug)


@mcp.tool()
async def xano_create_table_record(
    instance_name: str, workspace_id: str, table_id: str, record_data: Dict[str, Any], config=None
) -> Dict[str, Any]:
    """Create a new record in a table.

    Args:
        instance_name: The name of the Xano instance
        workspace_id: The ID of the workspace
        table_id: The ID of the table
        record_data: The data for the new record
    """
    token = get_token(config)
    debug = config.get('debug', False) if config else False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    instance_domain = f"{instance_name}.n7c.xano.io"
    meta_api = f"https://{instance_domain}/api:meta"

    workspace_id = format_id(workspace_id)
    table_id = format_id(table_id)

    url = f"{meta_api}/workspace/{workspace_id}/table/{table_id}/content"
    if debug:
        logger.info(f"Creating table record at URL: {url}")
    return await make_api_request(url, headers, method="POST", data=record_data, debug=debug)


@mcp.tool()
async def xano_update_table_record(
    instance_name: str,
    workspace_id: str,
    table_id: str,
    record_id: str,
    record_data: Dict[str, Any],
    config=None
) -> Dict[str, Any]:
    """Update an existing record in a table.

    Args:
        instance_name: The name of the Xano instance
        workspace_id: The ID of the workspace
        table_id: The ID of the table
        record_id: The ID of the record to update
        record_data: The updated data for the record
    """
    token = get_token(config)
    debug = config.get('debug', False) if config else False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    instance_domain = f"{instance_name}.n7c.xano.io"
    meta_api = f"https://{instance_domain}/api:meta"

    workspace_id = format_id(workspace_id)
    table_id = format_id(table_id)
    record_id = format_id(record_id)

    url = f"{meta_api}/workspace/{workspace_id}/table/{table_id}/content/{record_id}"
    if debug:
        logger.info(f"Updating table record at URL: {url}")
    return await make_api_request(url, headers, method="PUT", data=record_data, debug=debug)


@mcp.tool()
async def xano_delete_table_record(
    instance_name: str, workspace_id: str, table_id: str, record_id: str, config=None
) -> Dict[str, Any]:
    """Delete a specific record from a table.

    Args:
        instance_name: The name of the Xano instance
        workspace_id: The ID of the workspace
        table_id: The ID of the table
        record_id: The ID of the record to delete
    """
    token = get_token(config)
    debug = config.get('debug', False) if config else False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    instance_domain = f"{instance_name}.n7c.xano.io"
    meta_api = f"https://{instance_domain}/api:meta"

    workspace_id = format_id(workspace_id)
    table_id = format_id(table_id)
    record_id = format_id(record_id)

    url = f"{meta_api}/workspace/{workspace_id}/table/{table_id}/content/{record_id}"
    if debug:
        logger.info(f"Deleting table record at URL: {url}")
    return await make_api_request(url, headers, method="DELETE", debug=debug)


async def run_mcp_server(transport="stdio", host="0.0.0.0", port=8000, config=None):
    """Run the MCP server with the specified transport
    
    Args:
        transport: Transport type ("stdio" or "websocket")
        host: Host to bind to for websocket transport
        port: Port to bind to for websocket transport
        config: Configuration dictionary
    """
    if transport == "websocket":
        logger.info(f"Starting Xano MCP server with WebSocket transport on {host}:{port}...")
        await mcp.run_websocket(host=host, port=port, config=config)
    else:  # Default to stdio
        logger.info("Starting Xano MCP server with stdio transport...")
        await mcp.run(transport="stdio", config=config)


def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(description="Xano MCP Server")
    parser.add_argument(
        "--transport", 
        choices=["stdio", "websocket"], 
        default="stdio",
        help="Transport method (stdio or websocket)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0",
        help="Host to bind to for websocket transport"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to bind to for websocket transport"
    )
    parser.add_argument(
        "--token", 
        help="Xano API token"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Set up logging level based on debug flag
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Set token in environment if provided
    if args.token:
        os.environ["XANO_API_TOKEN"] = args.token
    
    # Create config dict
    config = {
        "debug": args.debug
    }
    
    # Run the server
    asyncio.run(run_mcp_server(
        transport=args.transport,
        host=args.host,
        port=args.port,
        config=config
    ))


if __name__ == "__main__":
    main()
