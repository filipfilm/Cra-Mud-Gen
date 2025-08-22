# Procedural MUD Game

A text-based adventure game that runs entirely offline, featuring:
- Procedurally generated dungeons and themes
- Local LLM integration for natural language responses
- Text-to-image generation capabilities
- Multiple theme options (Fantasy, Sci-Fi, Horror, Cyberpunk)

## Features

### Core Gameplay
- Text-based adventure with natural language commands
- Procedurally generated dungeon layouts
- Multiple game themes with unique content
- Player character management (health, inventory, etc.)

### Technology Stack
- **Python 3.8+** - Primary development language
- **Local LLMs** - Qwen, Llama, or similar models (via llama-cpp-python)
- **ComfyUI** - Text-to-image generation system
- **Rich/Prompt Toolkit** - Terminal UI components (optional)
- **JSON** - Data persistence and configuration

## Project Structure

```
mud_game/
├── main.py                 # Main entry point
├── requirements.txt        # Project dependencies
├── README.md               # This file
├── core/
│   ├── mud_engine.py       # Main game engine
│   ├── player.py           # Player state management
│   ├── world.py            # World and dungeon generation
│   ├── room.py             # Room representation
│   └── theme_manager.py    # Theme handling
├── ui/
│   └── terminal_ui.py      # Terminal-based user interface
├── llm/
│   └── llm_interface.py    # LLM integration layer
└── image_generation/
    └── image_bridge.py     # ComfyUI integration
```

## Getting Started

1. **Prerequisites**:
   - Python 3.8 or higher
   - ComfyUI (for image generation) - optional but recommended

2. **Installation**:
   ```bash
   # Clone the repository (if applicable)
   git clone <repository-url>
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Running the Game**:
   ```bash
   python main.py
   ```

## Game Commands

- `go <direction>` - Move in a direction (north, south, east, west, up, down)
- `look/l` - Look around the current room
- `inventory/i` - Show your inventory
- `take/get <item>` - Take an item from the room
- `use <item>` - Use an item from your inventory
- `help/h` - Show available commands
- `quit/q` - Exit the game

## Themes

The game supports multiple themes:
1. **Fantasy** - Mystical worlds with magic and ancient artifacts
2. **Sci-Fi** - Futuristic settings with technology and space
3. **Horror** - Dark, terrifying environments with supernatural threats
4. **Cyberpunk** - Neon-lit dystopian futures with advanced tech

## Architecture

The game follows a modular architecture:
1. **Engine Core** - Main game loop and state management
2. **Command Processor** - Parses and executes player commands
3. **Procedural Generator** - Creates unique game worlds
4. **LLM Interface** - Integrates local language models
5. **Image Generator** - Connects to ComfyUI for visual content
6. **User Interface** - Terminal-based display and input

## Future Enhancements

- Multiplayer support (local network)
- Save/load game state functionality
- Enhanced theme customization
- Web-based UI alternative
- Sound effects and audio integration
- Advanced LLM features (function calling)
- Dynamic theme progression during gameplay

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.