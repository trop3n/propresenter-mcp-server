# ProPresenter MCP Server

A Model Context Protocol (MCP) server that enables AI assistants to control and automate ProPresenter presentations through its HTTP API.

## Features

This MCP server provides comprehensive control over ProPresenter with 48+ tools covering:

- **Presentation Control**: Navigate slides, trigger specific slides, get presentation status
- **Library Management**: Browse libraries and presentations
- **Playlist Management**: List, focus, and trigger playlist items
- **Looks**: Control visual presets and audience looks
- **Macros**: Execute macros by name or ID
- **Messages**: Display and clear messages
- **Props**: Trigger and clear props
- **Timers**: Start, stop, and reset timers
- **Audio**: Manage audio playlists
- **Clear Operations**: Clear specific layers or all content
- **Stage Display**: Control stage display layouts
- **Themes**: Access and manage themes
- **Video Inputs**: Trigger video inputs
- **Utilities**: Find My Mouse and other helper functions

## Prerequisites

- **ProPresenter 7.9+** with HTTP API enabled
- **Python 3.10 or higher**
- ProPresenter Network API enabled (Preferences → Network)

## Installation

### 1. Clone or download this repository

```bash
git clone <repository-url>
cd propresenter-mcp-server
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
# or if using pyproject.toml:
pip install -e .
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
PROPRESENTER_HOST=192.168.1.100
PROPRESENTER_PORT=57369
```

**Finding your ProPresenter API settings:**
1. Open ProPresenter
2. Go to Preferences → Network
3. Enable "Network"
4. Note the IP address and Port number
5. Update your `.env` file with these values

## Usage

### Running the MCP Server

The server is designed to be run via the MCP command-line interface:

```bash
mcp run mcp-server.py
```

Or install it in your MCP client configuration.

### MCP Client Configuration

Add this server to your MCP client's configuration file (e.g., Claude Desktop):

**On MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "propresenter": {
      "command": "python",
      "args": ["/path/to/propresenter-mcp-server/mcp-server.py"],
      "env": {
        "PROPRESENTER_HOST": "192.168.1.100",
        "PROPRESENTER_PORT": "57369"
      }
    }
  }
}
```

Or use the `mcp` CLI:

```bash
mcp install mcp-server.py --name propresenter
```

## Available Tools

### Presentation Control
- `get_active_presentation()` - Get current presentation info
- `get_slide_index()` - Get current slide index
- `trigger_slide_by_index(index)` - Go to specific slide
- `next_slide()` - Advance to next slide
- `previous_slide()` - Go to previous slide
- `focus_presentation()` - Focus active presentation

### Library & Playlists
- `get_libraries()` - List all libraries
- `get_library_items(library_id)` - Get presentations in library
- `get_playlists()` - List all playlists
- `get_active_playlist()` - Get current playlist
- `get_playlist_items(playlist_id)` - Get items in playlist
- `focus_playlist_item(playlist_id, index)` - Select playlist item
- `trigger_playlist_item(playlist_id, index)` - Trigger playlist item

### Looks & Macros
- `get_looks()` - List all looks
- `get_current_look()` - Get active look
- `trigger_look_by_id(look_id)` - Activate a look
- `get_macros()` - List all macros
- `trigger_macro_by_id(macro_id)` - Execute macro by ID
- `trigger_macro_by_name(name)` - Execute macro by name

### Messages & Props
- `get_messages()` - List all messages
- `trigger_message_by_id(message_id)` - Show message
- `clear_message_by_id(message_id)` - Hide message
- `get_props()` - List all props
- `trigger_prop_by_id(prop_id)` - Show prop
- `clear_prop_by_id(prop_id)` - Hide prop

### Timers & Audio
- `get_timers()` - List all timers
- `start_timer_by_id(timer_id)` - Start timer
- `stop_timer_by_id(timer_id)` - Stop timer
- `reset_timer_by_id(timer_id)` - Reset timer
- `get_audio_playlists()` - List audio playlists
- `get_audio_playlist_items(playlist_id)` - Get audio items

### Clear Operations
- `clear_all()` - Clear all layers
- `clear_layer(layer)` - Clear specific layer (audio, props, messages, slide, media, video_input)
- `get_clear_groups()` - List clear groups
- `trigger_clear_group_by_id(group_id)` - Execute clear group

### Stage & Display
- `get_stage_layouts()` - List stage layouts
- `get_active_stage_layout()` - Get current stage layout
- `set_stage_layout_by_id(layout_id)` - Change stage layout
- `get_themes()` - List themes
- `get_theme_by_id(theme_id)` - Get theme details

### Video & Utilities
- `get_video_inputs()` - List video inputs
- `trigger_video_input_by_index(input_index)` - Activate video input
- `find_my_mouse()` - Execute Find My Mouse

## Example Usage with AI Assistant

Once configured, you can ask your AI assistant natural language questions like:

- "Show me the current presentation status"
- "Go to the next slide"
- "Trigger the macro named 'Welcome'"
- "Start the countdown timer"
- "Clear all layers"
- "Switch to the 'Minimalist' stage layout"

## Troubleshooting

### Connection Errors

**Error**: `Cannot connect to ProPresenter at http://...`

**Solutions**:
1. Verify ProPresenter is running
2. Check Network API is enabled in ProPresenter Preferences → Network
3. Confirm the host IP and port in your `.env` file
4. Test connection: `curl http://YOUR_IP:YOUR_PORT/v1/presentation/active`
5. Check firewall settings aren't blocking the connection

### Timeout Errors

**Error**: `Request timed out connecting to ProPresenter`

**Solutions**:
1. Ensure ProPresenter isn't overloaded
2. Check network connectivity
3. Increase timeout in `call_propresenter_api()` function if needed

### Authentication Errors

**Error**: `Authentication failed`

Some ProPresenter configurations require authentication. If you see this error, you may need to add authentication support to the server.

### Endpoint Not Found

**Error**: `Endpoint not found: /v1/...`

This endpoint may not be supported in your ProPresenter version. Ensure you're running ProPresenter 7.9 or higher. Some endpoints may be version-specific.

## API Documentation

For complete ProPresenter API documentation, visit:
- Official: Access via ProPresenter → Preferences → Network → "API Documentation" button
- Community: [ProPresenter API Documentation](https://jeffmikels.github.io/ProPresenter-API/Pro7/)
- OpenAPI Spec: [https://openapi.propresenter.com/](https://openapi.propresenter.com/)

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black mcp-server.py
ruff check mcp-server.py
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [FastMCP](https://github.com/anthropics/fastmcp)
- ProPresenter API documentation by the community
- Renewed Vision for ProPresenter

## Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [ProPresenter](https://renewedvision.com/propresenter/)
- [ProPresenter API Documentation](https://jeffmikels.github.io/ProPresenter-API/)
