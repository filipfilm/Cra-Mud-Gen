# Cra-mud-gen

An AI-powered text adventure game that creates unique narrative-driven dungeons using local LLM integration. Features dynamic story generation, intelligent quest systems, and spatially consistent dungeon exploration.

## Features

### Core Gameplay
- **Text-based adventure** with natural language commands
- **Procedurally generated dungeons** with logical spatial navigation
- **Multiple game themes** (Fantasy, Sci-Fi, Horror, Cyberpunk) with theme-appropriate content
- **Dynamic story seed generation** - AI creates unique story concepts with characters, conflicts, and narrative beats
- **Player progression** - health, inventory, experience, leveling system
- **Turn-based tactical combat** with status effects and enemy AI

### AI-Powered Systems
- **Story seed generation** - LLM creates unique narrative premises with characters and plot
- **Quest system** - Fully LLM-driven quest generation from story beats (no hardcoded content)
- **Dynamic content generation** - Rooms, items, NPCs, and descriptions created by AI
- **Intelligent puzzles** - LLM-generated riddles and challenges that fit the theme
- **Contextual conversations** - NPCs with AI-driven personalities and dialogue

### Advanced Features
- **Spatial navigation** - Logically consistent dungeon layout (north/south/east/west work properly)
- **ASCII map system** - Visual dungeon mapping with exploration tracking  
- **Save/load system** - Complete game state persistence including quest progress
- **Crafting system** - Item creation with skill progression
- **Economy system** - Dynamic market with merchants, haggling, and economic events
- **Narrative choice system** - Meaningful story decisions with consequences

## Technology Stack

- **Python 3.8+** - Primary development language
- **Ollama** - Local LLM integration (supports Mistral, Llama, Qwen, etc.)
- **Requests** - HTTP client for Ollama API communication
- **JSON** - Data persistence and save system

## Project Structure

```
cra-mud-gen/
├── main.py                      # Main entry point with model selection
├── requirements.txt             # Minimal dependencies (only requests)
├── README.md                    # This file
├── core/
│   ├── mud_engine.py           # Main game engine and loop
│   ├── player.py               # Player state and progression
│   ├── world.py                # World generation with spatial consistency
│   ├── room.py                 # Room representation
│   ├── spatial_navigator.py    # Logical navigation system (NEW)
│   ├── story_seed_generator.py # AI story concept generation
│   ├── quest_system.py         # LLM-driven quest generation
│   ├── puzzle_system.py        # Dynamic puzzle creation
│   ├── crafting_system.py      # Item crafting with skills
│   ├── economy_system.py       # Market simulation with merchants
│   ├── combat_system.py        # Turn-based combat mechanics
│   ├── conversation_system.py  # NPC dialogue system
│   ├── save_system.py          # Game state persistence
│   ├── map_system.py           # ASCII dungeon mapping
│   ├── command_processor.py    # Command parsing and execution
│   ├── theme_manager.py        # Theme handling and content
│   ├── dynamic_content_generator.py # LLM content generation
│   └── context_manager.py      # Context tracking for AI
├── ui/
│   ├── terminal_ui.py          # Main terminal interface
│   ├── combat_ui.py            # Combat-specific UI
│   ├── seed_ui.py              # Story seed generation interface
│   ├── contextual_effects.py   # Dynamic UI effects
│   └── colors.py               # Terminal colors and styling
├── llm/
│   ├── llm_interface.py        # LLM integration layer
│   └── ollama_llm.py           # Ollama-specific implementation
└── saves/                      # Save game directory (auto-created)
```

## Getting Started

### Prerequisites
- **Python 3.8+**
- **Ollama** - For local LLM support
  ```bash
  # Install Ollama (macOS/Linux)
  curl -fsSL https://ollama.ai/install.sh | sh
  
  # Install a model (choose one)
  ollama pull mistral           # 7B - Good for storytelling
  ollama pull llama3.1          # 8B - Great general purpose  
  ollama pull gemma2:2b         # 2B - Fast and lightweight
  
  # Start Ollama server
  ollama serve
  ```

### Installation
```bash
# Clone or download the project
cd cra-mud-gen

# Install minimal dependencies
pip install -r requirements.txt
```

### Running the Game
```bash
python main.py

# Optional: Enable fallback mode if LLM fails
python main.py --fallback-mode
```

## Game Commands

### Movement & Exploration
- `go <direction>` / `north/south/east/west/up/down` - Move around dungeon
- `look` / `l` - Examine current room
- `examine <item>` - Look at specific items or room features
- `map` / `m` - Show ASCII dungeon map
- `stats` - Show exploration statistics

### Inventory & Items
- `inventory` / `i` - Show your items
- `take <item>` / `get <item>` - Pick up items
- `drop <item>` - Drop items in current room
- `use <item>` - Use items from inventory

### Quests & Progress
- `quests` - Show active quest log with objectives and progress
- `hints` - Get hints for current quest objectives

### Combat
- `attack <enemy>` - Attack specific enemy
- `defend` / `guard` - Defensive stance
- `flee` / `run` - Attempt to escape
- `heal` - Use healing potions

### Crafting & Economy
- `craft <recipe>` - Create items (if recipe known)
- `recipes` - Show known crafting recipes
- `skills` - Show crafting skill levels
- `trade` - Talk to merchant in current room
- `shop` - Browse merchant inventory
- `buy <item>` / `sell <item>` - Trade with merchants
- `haggle <item>` - Negotiate prices

### Conversations & NPCs
- `talk to <npc>` - Start conversation
- `hello <npc>` - Greet NPCs

### Save System
- `save [name]` - Save game with optional name
- `load [name]` - Load saved game (shows list if no name)
- `quicksave` - Fast save to dedicated slot
- `quickload` - Fast load from quicksave
- `saves` - List all saved games

### Puzzles
- `solve <answer>` - Attempt to solve active puzzle
- Answer directly - Many puzzle responses work without "solve" prefix

### System Commands
- `help` / `h` - Show available commands
- `quit` / `q` - Exit game
- `debug` - Show spatial navigation debug info

## Themes

Each theme provides unique content, enemies, items, and atmosphere:

1. **Fantasy** - Mystical realms with magic, dragons, and ancient artifacts
2. **Sci-Fi** - Space stations, alien technology, and futuristic conflicts  
3. **Horror** - Dark supernatural environments with terrifying creatures
4. **Cyberpunk** - Neon-lit dystopian cities with hackers and corporations

Themes are automatically detected and applied based on your story seed, or you can select manually.

## Key Features Deep Dive

### Story Seed Generation
The game uses AI to create unique story concepts including:
- **Setting & Theme** - The world and atmosphere
- **Characters** - Key NPCs with backgrounds and motivations
- **Conflict** - Central story tension and plot
- **Story Beats** - Progressive narrative moments that become quests

### Spatial Navigation System  
Unlike many text games, Cra-mud-gen has **logically consistent navigation**:
- Going north then south returns you to the original room
- Maps accurately represent room positions
- No more confusing "the north exit leads to the room south of here" problems

### LLM-Driven Quests
Quests are generated dynamically from story beats with:
- Theme-appropriate objectives (collect data chips in sci-fi, find artifacts in fantasy)
- Contextual hints and descriptions  
- Progress tracking with meaningful rewards
- No hardcoded fantasy-only content

### Save System
Complete persistence of:
- Player progress and stats
- World state and room generation
- Quest progress and completion
- Conversation history and NPC relationships
- Crafting progress and discovered recipes

## Architecture

The game uses a modular architecture with:

1. **Game Engine** (`mud_engine.py`) - Main game loop and state management
2. **Spatial Navigator** (`spatial_navigator.py`) - Logical dungeon layout system
3. **LLM Integration** (`llm/`) - Local language model communication
4. **Content Generation** - AI-driven creation of stories, quests, rooms, items
5. **Save System** - Complete game state persistence
6. **UI Layer** - Terminal-based interface with rich visual effects

## Development

The game is designed to be:
- **Modular** - Easy to extend with new features
- **Theme-agnostic** - Content adapts to any theme automatically
- **LLM-first** - AI generates most content dynamically
- **Spatially consistent** - Logical navigation and mapping

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

---

**Note**: This project emphasizes local LLM usage for privacy and offline play. All AI features work with locally-run models via Ollama.