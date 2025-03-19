# Xano MCP Server Usage Guide

This document provides detailed instructions on how to use the Xano MCP server with Smithery and Claude AI.

## Getting Started

### Authentication

Before using the Xano MCP server, you need to obtain a Xano API token:

1. Log in to your Xano account
2. Navigate to your account settings
3. Generate an API token with appropriate permissions
4. Keep this token secure - it provides full access to your Xano databases

### Configuration

When deploying the MCP server to Smithery, you'll need to provide the following configuration:

```json
{
  "xano_api_token": "YOUR_XANO_API_TOKEN",
  "debug": false,
  "transport": "stdio"
}
```

## Using with Claude AI

Once the MCP server is deployed to Smithery, Claude AI can interact with your Xano databases. Here are some examples of how Claude might use the available tools:

### Exploring Your Xano Environment

```
I need to understand your Xano environment. Let me list the available instances and databases.
```

Claude will use the `xano_list_instances` and `xano_list_databases` tools to explore your Xano environment.

### Working with Tables

```
I'll help you manage your customer data table. Let me check its structure first.
```

Claude will use tools like `xano_list_tables`, `xano_get_table_details`, and `xano_get_table_schema` to understand your data structure.

### Querying Data

```
Let me find all customers who made a purchase in the last month.
```

Claude will use `xano_search_table_content` with appropriate search conditions to query your data.

### Modifying Data

```
I'll update the status of all pending orders to 'processing'.
```

Claude will use tools like `xano_search_and_update_records` or `xano_update_table_record` to modify your data.

## Common Workflows

### Creating a New Database Table

1. Claude identifies the need for a new table
2. Uses `xano_create_table` to create the table structure
3. Uses `xano_add_field_to_schema` to add necessary fields
4. Uses `xano_create_btree_index` or other index tools to optimize performance

### Importing Data

1. Claude helps prepare data in the correct format
2. Uses `xano_bulk_create_records` to import multiple records efficiently

### Data Analysis

1. Claude uses `xano_browse_table_content` or `xano_search_table_content` to retrieve data
2. Analyzes the data and provides insights
3. Optionally updates data based on analysis using appropriate update tools

## Security Best Practices

1. **API Token Management**:
   - Regularly rotate your Xano API token
   - Use the principle of least privilege when generating tokens

2. **Data Access**:
   - Be specific about which databases and tables Claude should access
   - Consider creating a separate Xano workspace with limited permissions for AI access

3. **Sensitive Data**:
   - Mark sensitive fields appropriately in your Xano schema
   - Instruct Claude to handle sensitive data with care

## Troubleshooting

### Common Issues

1. **Authentication Errors**:
   - Verify your API token is correct and has not expired
   - Check that you have the necessary permissions

2. **Rate Limiting**:
   - Xano may impose rate limits on API requests
   - Consider adding delays between operations if you encounter rate limiting

3. **Data Format Issues**:
   - Ensure data being sent to Xano matches the expected schema
   - Check for required fields and data type constraints

### Getting Help

If you encounter issues with the Xano MCP server:

1. Check the server logs by enabling debug mode
2. Review the Xano API documentation for specific endpoints
3. Contact support through the Smithery platform

## Advanced Usage

### Custom Workflows

You can create custom workflows by combining multiple Xano operations. For example:

1. Retrieve customer data
2. Process and analyze the data
3. Update customer records with new insights
4. Generate and store reports

### Integration with Other Systems

The Xano MCP server can be part of a larger workflow in Smithery that involves other systems:

1. Retrieve data from Xano
2. Process it with Claude AI
3. Send results to another system via a different MCP server

## Conclusion

The Xano MCP server provides a powerful bridge between Claude AI and your Xano databases. By following this guide, you can leverage the full capabilities of both systems to create intelligent, data-driven applications.
