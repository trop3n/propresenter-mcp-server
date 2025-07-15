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
# Each function decorated with `@mcp.tool()` becomes a tool that an AI can use.
# The docstring of the function is important, as it tells the AI what the tool does.

@mcp.tool()
def get_active_presentation_status() -> Dict[str, Any]:
    """
    Retrieves the status of the currently active presentation in ProPresenter.
    This includes the presentation name, current slide index, and total number of slides.
    """
    return call_propresenter_api("/v1/presentation/active/status")

@mcp.tool()
def next_slide() -> Dict[str, Any]:
    """
    Triggers the next slide in the currently active ProPresenter presentation.
    """
    return call_propresenter_api("/v1/presentation/active/next", method="POST")

@mcp.tool()
def previous_slide() -> Dict[str, Any]:
    """
    Triggers the previous slide in the currently active ProPresenter presentation.
    """
    return call_propresenter_api("/v1/presentation/active/previous", method="POST")

@mcp.tool()
def clear_all() -> Dict[str, Any]:
    """
    Clears all layers in ProPresenter (slide, media, props, messages, etc.)
    """
    return call_propresenter_api("/v1/clear/all", method="POST")

@mcp.tool()
def trigger_macro_by_name(name: str) -> Dict[str, Any]:
    """
    Triggers a ProPresenter Macro by its exact name.
    
    Args:
        name: The case-sensitive name of the macro to trigger.
    """
    # First, get all macros to find the ID for the given name
    macros_response = call_propresenter_api("/v1/macros")
    if macros_response.get("status") == "error":
        return macros_response
    
    macro_id = None
    for macro in macros_response:
        if macro.get("name") == name:
            macro_id = macro.get("id")
            break
    
    if not macro_id:
        return {"status": "error", "message": f"Macro with name '{name}' not found."}
    
    # Trigger the macro by its found ID
    return call_propresenter_api(f"/v1/macro/{macro_id}/trigger", method="POST")

# --- Main entry point to run the server ---
if __name__ == '__main__':
    import uvicorn
    print("--- ProPresenter MCP Server ---")
    print(f"Attempting to connect to ProPresenter at: {PROPRESENTER_API_URL}")
    print("Set the PROPRESENTER_HOST and PROPRESENTER_PORT env variables to change the target.")
    print("Server starting. Press CTRL+C to exit.")

    # Use uvicorn to run the FastAPI application
    # The MCP CLI will automatically find and run this.
    # To run manually: uvicorn "script_name":mcp.app --reload
    uvicorn.run(mcp.app, host="127.0.0.1", port=8000)