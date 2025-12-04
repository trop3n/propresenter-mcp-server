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
def call_propresenter_api(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    A helper function to make API calls to ProPresenter

    Args:
        endpoint: The API endpoint to call
        method: The HTTP method to use
        data: Optional JSON data to send in the request body

    Returns:
        A dictionary containing the JSON response from the API or an error status.
    """
    try:
        with httpx.Client() as client:
            # Construct the full URL for the API request
            full_url = f"{PROPRESENTER_API_URL}{endpoint}"
            print(f"Calling ProPresenter API: {method} {full_url}")

            # Perform HTTP Request
            kwargs = {"timeout": 10.0}
            if data:
                kwargs["json"] = data

            response = client.request(method, full_url, **kwargs)

            # Raise an exception if the request was unsuccessful (e.g., 404, 500)
            response.raise_for_status()

            # If the response has content, return it as JSON. Otherwise, return success.
            if response.status_code == 204: # No content
                return {"status": "success", "message": "Action completed successfully."}
            if response.status_code == 200 and not response.content:
                return {"status": "success", "message": "Action completed successfully."}

            # Try to parse JSON response
            try:
                return response.json()
            except ValueError:
                # If response is not JSON, return the text content
                return {"status": "success", "data": response.text}

    except httpx.TimeoutException as exc:
        # Handle timeout errors specifically
        error_msg = f"Request timed out connecting to ProPresenter at {PROPRESENTER_API_URL}. Ensure ProPresenter is running and the network API is enabled."
        print(f"Timeout error: {error_msg}")
        return {"status": "error", "message": error_msg}

    except httpx.ConnectError as exc:
        # Handle connection errors (e.g., ProPresenter not running or wrong host/port)
        error_msg = f"Cannot connect to ProPresenter at {PROPRESENTER_API_URL}. Check that ProPresenter is running, the API is enabled in Network settings, and the host/port are correct."
        print(f"Connection error: {error_msg}")
        return {"status": "error", "message": error_msg}

    except httpx.HTTPStatusError as exc:
        # Handle HTTP errors (4xx, 5xx)
        status_code = exc.response.status_code
        if status_code == 404:
            error_msg = f"Endpoint not found: {endpoint}. This endpoint may not be supported in your ProPresenter version."
        elif status_code == 401 or status_code == 403:
            error_msg = f"Authentication failed. Check if ProPresenter requires authentication credentials."
        elif status_code == 500:
            error_msg = f"ProPresenter server error. The API request was received but ProPresenter encountered an internal error."
        else:
            error_msg = f"HTTP {status_code} error: {exc.response.text}"

        print(f"HTTP error: {error_msg}")
        return {"status": "error", "message": error_msg, "status_code": status_code}

    except httpx.RequestError as exc:
        # Handle other network-related errors
        error_msg = f"Network error occurred: {str(exc)}"
        print(f"Request error: {error_msg}")
        return {"status": "error", "message": error_msg}

    except Exception as e:
        # Handle other unexpected errors
        error_msg = f"Unexpected error: {str(e)}"
        print(f"Unexpected error: {error_msg}")
        return {"status": "error", "message": error_msg}

# --- MCP Tool Definitions ---
# Each function decorated with `@mcp.tool()` becomes a tool that an AI can use.
# The docstring of the function is important, as it tells the AI what the tool does.

# ===== Presentation Control =====

@mcp.tool()
def get_active_presentation() -> Dict[str, Any]:
    """
    Retrieves the currently active presentation with detailed information including
    presentation UUID, name, and path.
    """
    return call_propresenter_api("/v1/presentation/active")

@mcp.tool()
def get_slide_index() -> Dict[str, Any]:
    """
    Gets the current slide index of the active presentation.
    """
    return call_propresenter_api("/v1/presentation/slide_index")

@mcp.tool()
def trigger_slide_by_index(index: int) -> Dict[str, Any]:
    """
    Triggers a specific slide in the active presentation by its index.

    Args:
        index: The zero-based index of the slide to trigger.
    """
    return call_propresenter_api(f"/v1/presentation/active/{index}/trigger", method="GET")

@mcp.tool()
def next_slide() -> Dict[str, Any]:
    """
    Triggers the next slide in the currently active ProPresenter presentation.
    """
    return call_propresenter_api("/v1/presentation/active/next", method="GET")

@mcp.tool()
def previous_slide() -> Dict[str, Any]:
    """
    Triggers the previous slide in the currently active ProPresenter presentation.
    """
    return call_propresenter_api("/v1/presentation/active/previous", method="GET")

@mcp.tool()
def focus_presentation() -> Dict[str, Any]:
    """
    Focuses (activates/selects) the currently active presentation in ProPresenter.
    """
    return call_propresenter_api("/v1/presentation/active/focus", method="GET")

# ===== Library Management =====

@mcp.tool()
def get_libraries() -> Dict[str, Any]:
    """
    Retrieves a list of all available libraries in ProPresenter.
    """
    return call_propresenter_api("/v1/libraries")

@mcp.tool()
def get_library_items(library_id: str) -> Dict[str, Any]:
    """
    Retrieves all items (presentations) in a specific library.

    Args:
        library_id: The UUID of the library.
    """
    return call_propresenter_api(f"/v1/library/{library_id}")

# ===== Playlist Management =====

@mcp.tool()
def get_playlists() -> Dict[str, Any]:
    """
    Retrieves a list of all playlists in ProPresenter.
    """
    return call_propresenter_api("/v1/playlists")

@mcp.tool()
def get_active_playlist() -> Dict[str, Any]:
    """
    Retrieves the currently focused/active playlist.
    """
    return call_propresenter_api("/v1/playlist/active")

@mcp.tool()
def get_playlist_items(playlist_id: str) -> Dict[str, Any]:
    """
    Retrieves all items in a specific playlist.

    Args:
        playlist_id: The UUID of the playlist.
    """
    return call_propresenter_api(f"/v1/playlist/{playlist_id}")

@mcp.tool()
def focus_playlist_item(playlist_id: str, index: int) -> Dict[str, Any]:
    """
    Focuses (selects) a specific item in a playlist by its index.

    Args:
        playlist_id: The UUID of the playlist.
        index: The zero-based index of the item to focus.
    """
    return call_propresenter_api(f"/v1/playlist/{playlist_id}/{index}/focus", method="GET")

@mcp.tool()
def trigger_playlist_item(playlist_id: str, index: int) -> Dict[str, Any]:
    """
    Triggers a specific item in a playlist by its index.

    Args:
        playlist_id: The UUID of the playlist.
        index: The zero-based index of the item to trigger.
    """
    return call_propresenter_api(f"/v1/playlist/{playlist_id}/{index}/trigger", method="GET")

# ===== Looks (Visual Presets) =====

@mcp.tool()
def get_looks() -> Dict[str, Any]:
    """
    Retrieves all saved audience looks (visual presets) in ProPresenter.
    """
    return call_propresenter_api("/v1/looks")

@mcp.tool()
def get_current_look() -> Dict[str, Any]:
    """
    Gets the currently active look.
    """
    return call_propresenter_api("/v1/look/current")

@mcp.tool()
def trigger_look_by_id(look_id: str) -> Dict[str, Any]:
    """
    Triggers a specific look by its UUID.

    Args:
        look_id: The UUID of the look to trigger.
    """
    return call_propresenter_api(f"/v1/look/{look_id}/trigger", method="GET")

# ===== Macros =====

@mcp.tool()
def get_macros() -> Dict[str, Any]:
    """
    Retrieves a list of all macros in ProPresenter.
    """
    return call_propresenter_api("/v1/macros")

@mcp.tool()
def trigger_macro_by_id(macro_id: str) -> Dict[str, Any]:
    """
    Triggers a ProPresenter macro by its UUID.

    Args:
        macro_id: The UUID of the macro to trigger.
    """
    return call_propresenter_api(f"/v1/macro/{macro_id}/trigger", method="GET")

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
            macro_id = macro.get("id", {}).get("uuid")
            break

    if not macro_id:
        return {"status": "error", "message": f"Macro with name '{name}' not found."}

    # Trigger the macro by its found ID
    return call_propresenter_api(f"/v1/macro/{macro_id}/trigger", method="GET")

# ===== Messages =====

@mcp.tool()
def get_messages() -> Dict[str, Any]:
    """
    Retrieves a list of all messages in ProPresenter.
    """
    return call_propresenter_api("/v1/messages")

@mcp.tool()
def trigger_message_by_id(message_id: str) -> Dict[str, Any]:
    """
    Shows a specific message by its UUID.

    Args:
        message_id: The UUID of the message to display.
    """
    return call_propresenter_api(f"/v1/message/{message_id}/trigger", method="POST")

@mcp.tool()
def clear_message_by_id(message_id: str) -> Dict[str, Any]:
    """
    Hides/clears a specific message by its UUID.

    Args:
        message_id: The UUID of the message to clear.
    """
    return call_propresenter_api(f"/v1/message/{message_id}/clear", method="GET")

# ===== Props =====

@mcp.tool()
def get_props() -> Dict[str, Any]:
    """
    Retrieves a list of all props in ProPresenter.
    """
    return call_propresenter_api("/v1/props")

@mcp.tool()
def trigger_prop_by_id(prop_id: str) -> Dict[str, Any]:
    """
    Triggers a specific prop by its UUID.

    Args:
        prop_id: The UUID of the prop to trigger.
    """
    return call_propresenter_api(f"/v1/prop/{prop_id}/trigger", method="GET")

@mcp.tool()
def clear_prop_by_id(prop_id: str) -> Dict[str, Any]:
    """
    Clears a specific prop by its UUID.

    Args:
        prop_id: The UUID of the prop to clear.
    """
    return call_propresenter_api(f"/v1/prop/{prop_id}/clear", method="GET")

# ===== Timers =====

@mcp.tool()
def get_timers() -> Dict[str, Any]:
    """
    Retrieves a list of all timers in ProPresenter.
    """
    return call_propresenter_api("/v1/timers")

@mcp.tool()
def start_timer_by_id(timer_id: str) -> Dict[str, Any]:
    """
    Starts a specific timer by its UUID.

    Args:
        timer_id: The UUID of the timer to start.
    """
    return call_propresenter_api(f"/v1/timer/{timer_id}/start", method="GET")

@mcp.tool()
def stop_timer_by_id(timer_id: str) -> Dict[str, Any]:
    """
    Stops a specific timer by its UUID.

    Args:
        timer_id: The UUID of the timer to stop.
    """
    return call_propresenter_api(f"/v1/timer/{timer_id}/stop", method="GET")

@mcp.tool()
def reset_timer_by_id(timer_id: str) -> Dict[str, Any]:
    """
    Resets a specific timer by its UUID.

    Args:
        timer_id: The UUID of the timer to reset.
    """
    return call_propresenter_api(f"/v1/timer/{timer_id}/reset", method="GET")

# ===== Audio =====

@mcp.tool()
def get_audio_playlists() -> Dict[str, Any]:
    """
    Retrieves a list of all audio playlists.
    """
    return call_propresenter_api("/v1/audio/playlists")

@mcp.tool()
def get_audio_playlist_items(playlist_id: str) -> Dict[str, Any]:
    """
    Retrieves all items in a specific audio playlist.

    Args:
        playlist_id: The UUID of the audio playlist.
    """
    return call_propresenter_api(f"/v1/audio/playlist/{playlist_id}")

# ===== Clear Operations =====

@mcp.tool()
def clear_all() -> Dict[str, Any]:
    """
    Clears all layers in ProPresenter (slide, media, props, messages, etc.)
    """
    return call_propresenter_api("/v1/clear/all", method="GET")

@mcp.tool()
def clear_layer(layer: str) -> Dict[str, Any]:
    """
    Clears a specific layer in ProPresenter.

    Args:
        layer: The layer to clear (e.g., 'audio', 'props', 'messages', 'announcements', 'slide', 'media', 'video_input')
    """
    return call_propresenter_api(f"/v1/clear/layer/{layer}", method="GET")

@mcp.tool()
def get_clear_groups() -> Dict[str, Any]:
    """
    Retrieves a list of all clear groups.
    """
    return call_propresenter_api("/v1/clear/groups")

@mcp.tool()
def trigger_clear_group_by_id(group_id: str) -> Dict[str, Any]:
    """
    Triggers a specific clear group by its UUID.

    Args:
        group_id: The UUID of the clear group to trigger.
    """
    return call_propresenter_api(f"/v1/clear/group/{group_id}/trigger", method="GET")

# ===== Stage Display =====

@mcp.tool()
def get_stage_layouts() -> Dict[str, Any]:
    """
    Retrieves a list of all stage display layouts.
    """
    return call_propresenter_api("/v1/stage/layouts")

@mcp.tool()
def get_active_stage_layout() -> Dict[str, Any]:
    """
    Gets the currently active stage display layout.
    """
    return call_propresenter_api("/v1/stage/layout")

@mcp.tool()
def set_stage_layout_by_id(layout_id: str) -> Dict[str, Any]:
    """
    Sets the stage display layout by its UUID.

    Args:
        layout_id: The UUID of the stage layout to activate.
    """
    return call_propresenter_api(f"/v1/stage/layout/{layout_id}", method="PUT")

# ===== Themes =====

@mcp.tool()
def get_themes() -> Dict[str, Any]:
    """
    Retrieves a list of all themes in ProPresenter.
    """
    return call_propresenter_api("/v1/themes")

@mcp.tool()
def get_theme_by_id(theme_id: str) -> Dict[str, Any]:
    """
    Retrieves details of a specific theme by its UUID.

    Args:
        theme_id: The UUID of the theme.
    """
    return call_propresenter_api(f"/v1/theme/{theme_id}")

# ===== Video Inputs =====

@mcp.tool()
def get_video_inputs() -> Dict[str, Any]:
    """
    Retrieves a list of all video inputs in ProPresenter.
    """
    return call_propresenter_api("/v1/video_inputs")

@mcp.tool()
def trigger_video_input_by_index(input_index: int) -> Dict[str, Any]:
    """
    Triggers a specific video input by its index.

    Args:
        input_index: The zero-based index of the video input to trigger.
    """
    return call_propresenter_api(f"/v1/video_input/{input_index}/trigger", method="GET")

# ===== Utility Functions =====

@mcp.tool()
def find_my_mouse() -> Dict[str, Any]:
    """
    Executes the 'Find My Mouse' feature in ProPresenter to highlight the cursor.
    """
    return call_propresenter_api("/v1/find_my_mouse", method="GET")

# The server is now intended to be run from the command line using the 'mcp' command,
# so the __main__ block has been removed.