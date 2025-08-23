# Procedural MUD Game

A text-based adventure game that runs entirely offline, featuring:
- Procedurally generated dungeons and themes
- Local LLM integration for natural language responses
- Text-to-image generation capabilities
- Multiple theme options (Fantasy, Sci-Fi, Horror, Cyberpunk)
- Turn-based combat system with enemies and experience
- Interactive NPC conversations
- ASCII art generation for rooms and items

## Features

### Core Gameplay
- Text-based adventure with natural language commands
- Procedurally generated dungeon layouts with spatial awareness
- Multiple game themes with unique content and mechanics
- Player character management (health, inventory, experience, leveling)
- Turn-based tactical combat with enemies and status effects
- Exploration tracking with dungeon map visualization

### Interactive Elements
- NPC conversations with dialogue trees and personality systems
- Item examination with ASCII art and descriptions
- Inventory management with item usage and dropping
- Environmental feature examination (walls, doors, etc.)

### Technology Stack
- **Python 3.8+** - Primary development language
- **Local LLMs** - Qwen, Llama, or similar models (via llama-cpp-python)
- **ComfyUI** - Text-to-image generation system (optional)
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
│   ├── theme_manager.py    # Theme handling
│   ├── command_processor.py # Command parsing and execution
│   ├── combat_system.py    # Combat mechanics and turn-based system
│   ├── enemy_spawner.py    # Enemy generation and spawning
│   ├── conversation_system.py # NPC dialogue system
│   ├── context_manager.py  # Context tracking for LLMs
│   └── map_system.py       # Dungeon mapping and exploration tracking
├── ui/
│   ├── terminal_ui.py      # Terminal-based user interface
│   ├── combat_ui.py        # Combat-specific UI elements
│   └── colors.py           # Color and visual effects for terminal
├── llm/
│   ├── llm_interface.py    # LLM integration layer
│   └── ollama_llm.py       # Ollama-specific LLM implementation
├── image_generation/
│   └── image_bridge.py     # ComfyUI integration for image generation
└── procedural/
    └── __init__.py         # Procedural generation utilities (if any)
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

### Basic Movement and Exploration
- `go <direction>` - Move in a direction (north, south, east, west, up, down)
- `look/l` - Look around the current room
- `inventory/i` - Show your inventory
- `take/get <item>` - Take an item from the room
- `use <item>` - Use an item from your inventory
- `help/h` - Show available commands
- `quit/q` - Exit the game

### Combat Commands
- `attack <enemy>` - Attack an enemy in combat
- `defend/guard` - Take defensive stance (reduces damage)
- `flee/run` - Attempt to flee from combat
- `heal` - Use a healing potion if you have one

### Conversation Commands
- `talk to <npc>` - Start a conversation with an NPC
- `hello <npc>` - Greet an NPC
- `goodbye` - End current conversation

### Map and Stats Commands
- `map/m` - Show the dungeon map
- `stats` - Show exploration statistics

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
3. **Procedural Generator** - Creates unique game worlds with spatial awareness
4. **LLM Interface** - Integrates local language models for immersive responses
5. **Image Generator** - Connects to ComfyUI for visual content (optional)
6. **User Interface** - Terminal-based display and input with rich visual effects
7. **Combat System** - Turn-based tactical combat mechanics
8. **Conversation System** - NPC dialogue and personality management

## Combat System

The game features a turn-based combat system with:
- Health management and damage calculation
- Status effects (poison, burn, etc.)
- Experience and leveling progression
- Loot and gold rewards from defeated enemies
- Tactical decision-making for both player and enemies

## NPC Conversations

Interact with NPCs in the game world:
- Weapons Master - Provides information about weapons and armor
- Fortune Teller - Offers mystical insights and predictions
- Other theme-appropriate NPCs with unique dialogue trees

## ASCII Art and Visual Effects

The game includes:
- ASCII art generation for rooms, items, and enemies
- Theme-appropriate visual effects and color schemes
- Status bars and health indicators
- Animated effects for immersive gameplay

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