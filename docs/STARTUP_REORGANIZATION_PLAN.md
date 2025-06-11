# ZackGPT Startup Reorganization Plan

## Current Problems
- **Port conflicts**: Multiple UIs on ports 3000, 4200, 8000
- **Scattered entry points**: 6 shell scripts + 6 Python startup files
- **Mixed responsibilities**: Scripts handle CLI/Web/Voice inconsistently
- **Poor shutdown handling**: Background processes not cleaned up properly
- **No centralized configuration**: Each script manages its own setup

## Proposed Structure

```
ZackGPT/
├── cli/                           # 🆕 Dedicated CLI directory
│   ├── __init__.py
│   ├── main.py                    # Single CLI entry point
│   ├── commands/                  # CLI command modules
│   │   ├── __init__.py
│   │   ├── chat.py               # Text chat mode
│   │   ├── voice.py              # Voice interaction mode
│   │   ├── dev.py                # Development tools
│   │   └── config.py             # Configuration management
│   ├── utils/                     # CLI utilities
│   │   ├── __init__.py
│   │   ├── interactive.py        # Interactive menus
│   │   └── output.py             # Colored output helpers
│   └── scripts/                  # CLI-specific shell scripts
│       ├── zackgpt-cli.sh        # Main CLI launcher
│       └── setup-env.sh          # Environment setup
│
├── server/                        # 🆕 Web server directory
│   ├── __init__.py
│   ├── main.py                   # Single web server entry point
│   ├── api/                      # API modules (moved from app/)
│   ├── frontend/                 # Frontend builds
│   └── scripts/
│       ├── start-server.sh       # Web server launcher
│       ├── start-dev.sh          # Development server
│       └── build-frontend.sh     # Frontend build script
│
├── launcher/                      # 🆕 Centralized launcher
│   ├── __init__.py
│   ├── main.py                   # Master launcher script
│   ├── config.py                 # Global configuration
│   ├── process_manager.py        # Process lifecycle management
│   └── health_check.py           # Service health monitoring
│
├── scripts/                       # Simplified scripts
│   ├── zackgpt.sh                # 🔄 Simplified master launcher
│   ├── setup/                    # Setup scripts
│   │   ├── install-deps.sh
│   │   ├── setup-docker.sh
│   │   └── create-env.sh
│   └── docker/                   # Docker scripts
│       ├── start.sh
│       ├── stop.sh
│       └── reset.sh
│
└── config/                        # Enhanced configuration
    ├── startup.yaml              # 🆕 Centralized startup config
    ├── ports.yaml                # 🆕 Port management
    └── services.yaml             # 🆕 Service definitions
```

## Port Standardization

| Service | Port | Purpose |
|---------|------|---------|
| Web API | 8000 | FastAPI backend |
| Frontend | 3000 | React development server |
| CLI | N/A | Terminal-based interaction |
| Voice | N/A | CLI with audio I/O |
| Dev Tools | 8001 | Development utilities |

## New Startup Flow

### 1. Master Launcher (`./zackgpt.sh`)
```bash
#!/bin/bash
# Simple menu-driven launcher
echo "🚀 ZackGPT Launcher"
echo "1) CLI Mode"
echo "2) Web Server" 
echo "3) Development Mode"
echo "4) Docker Mode"

# Delegates to appropriate sub-launchers
```

### 2. CLI Mode (`./cli/scripts/zackgpt-cli.sh`)
```bash
#!/bin/bash
# Pure CLI experience - no web services
source cli/scripts/setup-env.sh
python -m cli.main "$@"
```

### 3. Web Mode (`./server/scripts/start-server.sh`)
```bash
#!/bin/bash
# Web server only - clean separation
source scripts/setup/install-deps.sh
python -m server.main
```

### 4. Process Management
- **Centralized PID tracking**: All background processes tracked
- **Graceful shutdown**: Proper cleanup on Ctrl+C
- **Health monitoring**: Service health checks
- **Port conflict detection**: Automatic port availability checking

## Migration Steps

### Phase 1: Create CLI Directory Structure
1. Create `cli/` directory with proper module structure
2. Move `main_text.py`, `main_voice.py`, `dev.py` to `cli/commands/`
3. Create unified `cli/main.py` entry point
4. Create `cli/scripts/zackgpt-cli.sh` launcher

### Phase 2: Create Server Directory Structure  
1. Create `server/` directory
2. Move `main_web.py` and web API code to `server/`
3. Consolidate frontend handling
4. Create `server/scripts/start-server.sh`

### Phase 3: Centralized Launcher
1. Create `launcher/` directory with process management
2. Create `config/startup.yaml` for service definitions
3. Implement health checking and port management
4. Create simplified `zackgpt.sh` master launcher

### Phase 4: Cleanup
1. Remove redundant shell scripts
2. Update documentation
3. Add service dependency management
4. Implement proper logging

## Benefits of This Approach

✅ **Clear Separation**: CLI and Web completely isolated
✅ **Single Entry Points**: One script per mode
✅ **Consistent Shutdown**: Proper process lifecycle management  
✅ **Port Management**: Centralized port allocation and conflict detection
✅ **Modular Design**: Easy to add new interfaces (GUI, API, etc.)
✅ **Better Testing**: Each component can be tested independently
✅ **Simplified Debugging**: Clear responsibility boundaries

## Configuration Examples

### `config/startup.yaml`
```yaml
services:
  cli:
    type: interactive
    entry_point: cli.main
    dependencies: []
    
  web_api:
    type: server  
    entry_point: server.main
    port: 8000
    dependencies: []
    
  frontend:
    type: server
    entry_point: server.frontend
    port: 3000
    dependencies: [web_api]
```

### `config/ports.yaml`
```yaml
reserved_ports:
  web_api: 8000
  frontend: 3000
  dev_tools: 8001

port_ranges:
  development: 8100-8199
  testing: 8200-8299
```

This structure provides clean separation, eliminates port conflicts, and makes the system much more maintainable and debuggable. 