# OSRS Bot Management UI

A comprehensive web-based interface for managing and controlling Old School RuneScape bots built on the auto_rs framework.

## Features

### 🤖 Bot Management
- **Auto-Discovery**: Automatically discovers and catalogs all available bots from the `bots/` directory
- **Configuration Management**: Web-based interface for configuring bot parameters
- **Process Control**: Start, stop, pause, and resume bots through the web interface
- **Real-time Status**: Monitor bot runtime, status, and performance

### 🎛️ Parameter Configuration
- **RGB Parameters**: Visual color picker with RGB value inputs
- **Range Parameters**: Min/max value configuration with validation
- **Break Configuration**: Configurable break patterns for human-like behavior
- **Item Parameters**: Integration with OSRS item database for item selection
- **Import/Export**: Save and load bot configurations as JSON files

### 📊 Dashboard
- **Live Status**: Real-time overview of all running bots
- **System Status**: Monitor system resources and bot availability
- **Quick Actions**: Start, stop, and configure bots directly from the dashboard

### 🔧 API Integration
- **RESTful API**: Complete REST API for programmatic bot control
- **BotAPI Integration**: Seamless integration with existing BotAPI system
- **Cross-platform**: Works on Windows, Linux, and macOS

## Quick Start

### Prerequisites
- Python 3.10 or higher
- All dependencies from `requirements.txt` installed
- RuneLite client (for bot execution)

### Starting the UI

#### Option 1: Simple Start
```bash
python main.py
```

#### Option 2: Quick Start with Browser Launch
```bash
python start_ui.py
```

#### Option 3: Command Line Bot Manager
```bash
python bot_manager.py
```

### Accessing the Interface
Once started, the web interface will be available at:
- **Main Dashboard**: http://localhost:8080
- **API Endpoints**: http://localhost:8080/api/*

## Directory Structure

```
ui/
├── main.py              # Main Flask application
├── static/
│   ├── css/
│   │   └── style.css    # Custom CSS styles
│   └── js/
│       └── main.js      # JavaScript utilities
└── templates/
    ├── base.html        # Base template with navigation
    ├── index.html       # Dashboard page
    └── bot_detail.html  # Bot configuration page
```

## Configuration

### Bot Discovery
The system automatically discovers bots by scanning the `bots/` directory for Python files containing:
- A `BotConfig` class that inherits from `BotConfigMixin`
- A `BotExecutor` class that inherits from `Bot`

### Parameter Types
The UI supports all parameter types from the configuration system:
- **RGBParam**: Color selection with visual preview
- **RangeParam**: Min/max value ranges
- **BreakCfgParam**: Break duration and frequency settings
- **ItemParam**: OSRS item selection with database integration
- **Basic Types**: String, Integer, Float, Boolean parameters

### API Endpoints

#### Bot Management
- `GET /api/bots` - List all available bots
- `GET /api/bot/<bot_id>/status` - Get bot status
- `POST /api/bot/<bot_id>/start` - Start a bot
- `POST /api/bot/<bot_id>/stop` - Stop a bot
- `POST /api/bot/<bot_id>/control` - Control bot (pause/resume)

#### Configuration
- `GET /api/bot/<bot_id>/config` - Get bot configuration
- `POST /api/bot/<bot_id>/config` - Save bot configuration

## Development

### Adding New Parameter Types
1. Define the parameter type in `bots/core/cfg_types.py`
2. Add UI handling in `ui/templates/bot_detail.html`
3. Update JavaScript configuration gathering in the template

### Customizing the UI
- Modify `ui/static/css/style.css` for styling changes
- Update `ui/static/js/main.js` for JavaScript functionality
- Edit templates in `ui/templates/` for layout changes

### Bot Integration
Ensure your bots follow the standard pattern:
```python
from bots.core import BotConfigMixin
from bots.core.cfg_types import *
from core.bot import Bot

class BotConfig(BotConfigMixin):
    # Configuration parameters
    pass

class BotExecutor(Bot):
    name = "Your Bot Name"
    description = "Bot description"
    
    def __init__(self, config: BotConfig, user=''):
        super().__init__(user, break_cfg=config.break_cfg)
        self.cfg = config
    
    def start(self):
        # Bot implementation
        pass
```

## Troubleshooting

### Common Issues

#### "No bots found"
- Ensure bots are in the `bots/` directory
- Check that bot files contain `BotConfig` and `BotExecutor` classes
- Verify bots don't have syntax errors

#### "Failed to start bot"
- Check that RuneLite is installed and accessible
- Verify no other process is using port 5432 (BotAPI port)
- Review bot logs for specific error messages

#### Web UI not accessible
- Ensure port 8080 is not in use by another application
- Check firewall settings if accessing remotely
- Verify Flask dependencies are installed

### Logs and Debugging
- Bot logs are available through the core logging system
- Web UI logs appear in the console where you started the server
- Individual bot processes log separately

## Security Considerations

### Development Use
This UI is designed for development and personal use. For production deployment:
- Change the Flask secret key
- Enable proper authentication
- Use a production WSGI server (not Flask's development server)
- Implement proper error handling and logging

### Network Access
By default, the server binds to `0.0.0.0`, making it accessible from other machines on your network. To restrict to localhost only, modify the `app.run()` call in `main.py`:
```python
app.run(host='127.0.0.1', port=8080, ...)
```

## Contributing

When contributing to the UI system:
1. Follow the existing code style and patterns
2. Test with multiple bot types to ensure compatibility
3. Update documentation for new features
4. Ensure responsive design for mobile devices

## License

This UI system is part of the auto_rs project and follows the same license terms.