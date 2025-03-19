FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Make the Python scripts executable
RUN chmod +x /app/src/xano_mcp.py

# Set the entrypoint to use bash so Smithery can execute the command
CMD ["/bin/bash", "-c", "python -m src.xano_mcp --token \${XANO_API_TOKEN} \${DEBUG_FLAG}"]
