# Dec207Hub Configuration

## Environment Variables

```bash
# Ollama Configuration
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=qwen3:7b

# Backend Configuration
BACKEND_HOST=localhost
BACKEND_PORT=8000
API_PREFIX=/api/v1

# Frontend Configuration
FRONTEND_PORT=3000
WEBSOCKET_URL=ws://localhost:8000/ws

# MCP Configuration
MCP_SERVERS_DIR=./mcp-servers
BLENDER_MCP_PORT=8001
UNITY_MCP_PORT=8002

# Database Configuration
DATABASE_URL=sqlite:///./dec207hub.db

# Audio Configuration
TTS_ENGINE=web-speech-api
STT_ENGINE=web-speech-api
AUDIO_SAMPLE_RATE=16000

# Security
API_SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:3000"]
```

## Model Configuration

```json
{
  "models": {
    "primary": {
      "name": "qwen3:7b",
      "temperature": 0.7,
      "max_tokens": 2000,
      "top_p": 0.9
    },
    "fallback": {
      "name": "llama3.1:8b",
      "temperature": 0.5,
      "max_tokens": 1000
    }
  },
  "mcp": {
    "enabled": true,
    "servers": ["blender-mcp", "unity-mcp"],
    "timeout": 30
  }
}
```

## Development Settings

```json
{
  "development": {
    "debug": true,
    "auto_reload": true,
    "log_level": "DEBUG"
  },
  "production": {
    "debug": false,
    "auto_reload": false,
    "log_level": "INFO"
  }
}
```
