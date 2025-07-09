import httpx
import os
from typing import Any, Dict

# Import MCP Server Framework
from mcp.server.fastmcp import FastMCP

# --- Configuration ---
# It's best practice to use environment variable in your configuration
# You can set these in your terminal before running the script
# Example: export PROPRESENTER_HOST="192.168.1.100"
PROPRESENTER_HOST = os.getenv("PROPRESENTER_HOST", "localhost")
PROPRESENTER_PORT = int(os.getenv("PROPRESENTER_PORT", "50001"))

# Construct the base URL for the ProPresenter API
PROPRESENTER_API_URL = f"http://{PROPRESENTER_HOST}:{PROPRESENTER_PORT}"

# Initialize the MCP server. The name is used to identify your server.
mcp = FastMCP("propresenter_control_server")

# --- ProPresenter API Helper ---
# This helper function simplifies making calls to the ProPresenter API
# It handles constructing the URL and sending the request.
def call_propresenter_api(endpoint: str, method: str = "GET") -> Dict[str, Any]:
    """
    A helper function to make API calls to ProPresenter

    Args:
        endpoint: The API endpoint to call
        method: The HTTP method to use

    Returns:
        A dictionary containing the JSON response from the API.
    """
    try:
        with httpx.Client() as client:
            # Construct the full URL for the API request
            full_url = f"{PROPRESENTER_API_URL}{endpoint}"
            print(f"Calling ProPresenter API: {method} {full_url}")