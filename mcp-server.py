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

            # Perform HTTP Request
            response = client.request(method, full_url, timeout=5.0)

            # Raise an exception if the request was unsuccessful (e.g., 404, 500)
            response.raise_for_status()

            # If the response has content, return it as JSON. Otherwise, return success.
            if response.status_code == 204: # No content
                return {"status": "success", "message": "Action completed."}
            return response.json()

    except httpx.RequestError as exc:
        # Handle network-related erros (e.g., connection refused)
        print(f"An error occurred while requesting {exc.request.url!r}.")
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}
    except Exception as e:
        # Handle other potential errors
        print(f"An unexpected error occurred: {e}")
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}

# --- MCP Tool Definitions ---
