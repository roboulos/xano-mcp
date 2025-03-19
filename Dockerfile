FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Make the Python scripts executable
RUN chmod +x /app/src/xano_mcp.py

# Set the entrypoint
# The actual command will be provided by Smithery
ENTRYPOINT ["python", "-m", "src.xano_mcp"]
