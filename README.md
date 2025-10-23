# GLM 4.6 ACP Server

An Agent Client Protocol (ACP) server for the GLM 4.6 model from z.ai. This server acts as a bridge between ACP clients (like Toad) and the GLM 4.6 API.

## Prerequisites

- Python 3.8+
- A GLM API key from z.ai
- pip (Python package manager)

## Installation Steps

### Step 1: Clone or Download the Repository

```bash
git clone <repository-url>
cd glm-4.6-acp
```

Or download and extract the files to a directory of your choice.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

### Step 3: Configure Your API Key

Create a `.env` file in the project directory with your GLM API key:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API key:

```
GLM_API_KEY=your_actual_api_key_here
```

**Important**: Get your API key from [z.ai](https://z.ai) by signing up and accessing your API settings.

### Step 4: Verify Installation

Test that the server is working correctly:

```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | glm-4-6-acp
```

You should see a response like:

```json
{"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05", "agentCapabilities": {"loadSession": false, "promptCapabilities": {"audio": false, "embeddedContent": false, "image": false}}, "authMethods": []}}
```

## Usage

### With Toad

Once installed, you can use this server with Toad:

```bash
# Make sure your API key is set
export GLM_API_KEY="your_api_key_here"

# Run with Toad
uv run toad acp "glm-4-6-acp"
```

Or if you have the API key in your `.env` file, simply run:

```bash
uv run toad acp "glm-4-6-acp"
```

### Direct Usage

You can also run the server directly for testing:

```bash
# With API key as environment variable
export GLM_API_KEY="your_api_key_here"
glm-4-6-acp

# Or pass API key as argument
glm-4-6-acp "your_api_key_here"
```

## Features

- **Chat functionality** with GLM 4.6
- **Streaming responses** for better user experience
- **File operations** (read/write) for project integration
- **Session management** with conversation history
- **Error handling** for API failures
- **Environment variable support** for API keys

## API Details

- **Model**: GLM 4.6
- **Provider**: z.ai
- **API Base**: https://open.bigmodel.cn/api/paas/v4/
- **Protocol**: Agent Client Protocol (ACP)

## Configuration Options

### Environment Variables

- `GLM_API_KEY`: Your GLM API key (required)
- Alternatively, create a `.env` file in the project directory

### Server Configuration

The server can be configured through the following parameters:

- **Temperature**: Controls randomness in responses (0.0-1.0, default: 0.7)
- **Max Tokens**: Maximum response length (1-4096, default: 1024)

## Troubleshooting

### Common Issues

1. **"Agent is not ready" error in Toad**
   - Ensure your GLM API key is properly set
   - Check that the `.env` file exists and contains a valid API key
   - Verify the server is installed correctly: `which glm-4-6-acp`

2. **"GLM_API_KEY environment variable not set"**
   - Set the environment variable: `export GLM_API_KEY="your_key"`
   - Or create a `.env` file with your API key

3. **"Command not found: glm-4-6-acp"**
   - Install the package: `pip install -e .`
   - Check the installation: `which glm-4-6-acp`

4. **API errors**
   - Verify your API key is valid and active
   - Check your internet connection
   - Ensure you have sufficient API credits

### Debug Mode

To debug issues, you can run the server directly and send JSON-RPC messages:

```bash
# Test initialization
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | glm-4-6-acp

# Test session creation
echo '{"jsonrpc": "2.0", "id": 2, "method": "session/new", "params": {"projectPath": "/tmp"}}' | glm-4-6-acp
```

## File Structure

```
glm-4.6-acp/
├── glm_acp_server.py    # Main server implementation
├── pyproject.toml       # Project configuration
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── .env                 # Your environment variables (create this)
└── README.md           # This file
```

## Requirements

- Python 3.8+
- httpx>=0.24.0
- A valid GLM API key from z.ai

## Support

For issues related to:
- **GLM API**: Check the [z.ai documentation](https://z.ai)
- **Toad**: Refer to Toad's documentation and support channels
- **This server**: Check the troubleshooting section above

## License

This project is provided as-is for educational and development purposes.# glm-4.6-acp
