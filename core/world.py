"""
World class to manage the game world and dungeon generation
"""
import sys
import os
from typing import Dict, List, Optional, Any
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.room import Room
from core.theme_manager import ThemeManager
from core.enemy_spawner import EnemySpawner
from core.dynamic_content_generator import DynamicContentGenerator
from core.spatial_navigation import SpatialNavigation

class World:
    """
    Represents the game world including dungeon layout and rooms
    """
    
    def __init__(self, context_manager=None, llm=None, fallback_mode=False):
        self.rooms: Dict[str, Room] = {}
        self.theme = "fantasy"
        self.theme_manager = ThemeManager()
        self.enemy_spawner = EnemySpawner()
        self.content_generator = DynamicContentGenerator(llm, fallback_mode=fallback_mode)
        self.spatial_nav = SpatialNavigation(llm, fallback_mode=fallback_mode)
        self.dungeon_layout = []
        self.context_manager = context_manager
        self.llm = llm  # LLM instance for ASCII art generation
        self.fallback_mode = fallback_mode
        
        # Narrative integration
        self.narrative_state = None
        self.narrative_engine = None
    
    def set_narrative_context(self, narrative_state):
        """
        Set the narrative context for the world
        
        Args:
            narrative_state: The NarrativeState object to use
        """
        self.narrative_state = narrative_state
        if narrative_state:
            # Update theme based on story seed
            self.theme = narrative_state.seed.theme
            print(f"World narrative context set: {self.theme} theme with {len(narrative_state.seed.story_beats)} story beats")
        
    def generate_dungeon(self, theme: str = None):
        """
        Initialize the dungeon with just the starting room
        """
        # Use theme from narrative state if available, otherwise use provided theme
        if self.narrative_state:
            self.theme = self.narrative_state.seed.theme
        elif theme:
            self.theme = theme
        else:
            self.theme = "fantasy"  # Default fallback
        
        # Create only the starting room - everything else generated on demand
        start_room = self.generate_starting_room()
        self.rooms["start"] = start_room
    
    def generate_starting_room(self, theme: str = None) -> Room:
        """
        Generate the starting room with dynamic exits and narrative context
        """
        current_theme = theme or self.theme
        
        # Base description with narrative enhancement
        if self.narrative_state and self.narrative_state.seed.setting:
            description = f"You stand at the entrance of {self.narrative_state.seed.setting}. The air is thick with mystery and adventure awaits."
        else:
            description = f"You stand at the entrance of a {current_theme} dungeon. The air is thick with mystery and adventure awaits."
        
        # Add story-specific atmosphere if available
        if self.narrative_state and self.narrative_state.seed.custom_text:
            description += f" {self.narrative_state.seed.custom_text[:100]}..."
        
        # Starting room has 2-3 exits randomly
        available_directions = ["north", "east", "south", "west"]
        num_exits = random.randint(2, 3)
        exits = random.sample(available_directions, num_exits)
        
        # Convert to room IDs
        connections = [f"{direction}_1" for direction in exits]
        
        # Add ASCII art for starting room
        if random.random() < 0.5:  # 50% chance for starting room art
            ascii_art = self._generate_room_ascii_art("entrance", current_theme, "mysterious", "doorway")
            if ascii_art:
                description = f"{ascii_art}\n\n{description}"
        
        room = Room(
            room_id="start",
            description=description,
            items=self._get_room_items("entrance", current_theme),
            npcs=[],  # No NPCs in starting room
            connections=connections
        )
        
        return room
        
    def generate_room(self, room_id: str, theme: str, from_room: str = None, direction: str = None) -> Room:
        """
        Generate a single room procedurally with dynamic exits and narrative integration
        """
        # Parse room depth from ID (e.g., "north_3" means 3rd room north)
        depth = self._get_room_depth(room_id)
        
        # Check for narrative triggers at this depth
        narrative_trigger = None
        if self.narrative_state and hasattr(self.narrative_state, 'seed') and self.narrative_state.seed.story_beats:
            beat_index = min(depth // 3, len(self.narrative_state.seed.story_beats) - 1)
            if beat_index < len(self.narrative_state.seed.story_beats):
                narrative_trigger = self.narrative_state.seed.story_beats[beat_index]
        
        # Get spatially-aware room type, influenced by narrative
        if self.context_manager and from_room:
            room_type = self.context_manager.suggest_room_type(room_id, from_room, direction)
        else:
            # Use spatial navigation to suggest appropriate room types
            from_room_obj = self.get_room(from_room) if from_room else None
            if from_room_obj:
                from_env = self.spatial_nav._classify_environment(from_room, from_room_obj.description, theme)
                suggestions = self.spatial_nav.suggest_logical_connections(from_env, theme)
                suggested_env = suggestions.get(direction, "chamber")
                
                # Map environment back to room type
                env_to_type_map = {
                    "chamber": "chamber", "large_chamber": "chamber", "cavern": "cavern",
                    "hallway": "hallway", "tunnel": "tunnel", "library": "library",
                    "stairwell": "stairwell", "forest": "forest", "field": "chamber"
                }
                room_type = env_to_type_map.get(suggested_env, "chamber")
            else:
                room_types = self.theme_manager.get_theme_room_types(theme)
                room_type = random.choice(room_types) if room_types else "chamber"
        
        # Modify room type based on narrative trigger
        if narrative_trigger and depth > 0:
            if "library" in narrative_trigger.lower() or "knowledge" in narrative_trigger.lower():
                room_type = "library"
            elif "shrine" in narrative_trigger.lower() or "altar" in narrative_trigger.lower() or "sacred" in narrative_trigger.lower():
                room_type = "shrine"
            elif "armory" in narrative_trigger.lower() or "weapon" in narrative_trigger.lower():
                room_type = "armory"
        
        # Get theme information
        adjectives = self.theme_manager.get_theme_adjectives(theme)
        nouns = self.theme_manager.get_theme_nouns(theme)
        
        # Select elements that make spatial sense
        adjective = self._get_spatial_adjective(room_type, theme, adjectives)
        noun = self._get_spatial_noun(room_type, theme, nouns)
        
        # Generate dynamic exits first so we can reference them in description
        connections = self._generate_dynamic_exits(room_id, depth, direction, from_room)
        
        # Create spatially-consistent description with narrative enhancement and vertical hints
        description = self._create_spatial_description(room_type, adjective, noun, theme, from_room, direction, connections)
        
        # Add narrative trigger description if present
        if narrative_trigger and depth > 0:
            description += f" {narrative_trigger}"
        
        # Generate dynamic content using LLM with narrative context
        narrative_context = None
        if self.narrative_state:
            narrative_context = {
                "theme": self.narrative_state.seed.theme,
                "setting": self.narrative_state.seed.setting,
                "conflict": self.narrative_state.seed.conflict,
                "mood": self.narrative_state.seed.mood,
                "danger_level": self.narrative_state.seed.danger_level,
                "mystery_level": self.narrative_state.seed.mystery_level,
                "current_beat": narrative_trigger
            }
        
        dynamic_content = self.content_generator.generate_room_contents(description, theme, depth, narrative_context)
        items = dynamic_content.get("items", [])
        npcs = [npc["name"] for npc in dynamic_content.get("npcs", [])]
        
        # Store NPC dialogue data for conversation system with narrative awareness
        self._store_npc_dialogues(dynamic_content.get("npcs", []), dynamic_content.get("npc_dialogues", {}), theme, narrative_context)
        
        # Add special items at certain depths to encourage deep exploration
        if depth > 0 and depth % 5 == 0:  # Every 5th depth level
            special_items = self._get_depth_reward_items(depth, theme)
            items.extend(special_items)
        
        # Rare chance of finding something very special in deep areas
        if depth > 15 and random.random() < 0.1:
            rare_items = self._get_rare_items(theme)
            items.extend(rare_items)
        
        # Connections already generated above for description
        
        room = Room(
            room_id=room_id,
            description=description,
            items=items,
            npcs=npcs,
            connections=connections
        )
        
        # Add to context manager if available
        if self.context_manager:
            self.context_manager.add_room_context(room_id, description, items, npcs, theme, room_type)
        
        return room
    
    def spawn_enemies_in_room(self, room: Room, player_level: int, has_been_visited: bool = False) -> List:
        """
        Spawn enemies in a room based on theme, room type, and player level
        """
        room_type = self._infer_room_type_from_description(room.description)
        depth = self._get_room_depth(room.room_id)
        
        # Check if enemies should spawn
        if self.enemy_spawner.should_spawn_enemy(has_been_visited, depth, player_level):
            enemies = self.enemy_spawner.spawn_encounter(room_type, self.theme, player_level, depth)
            return enemies
        
        return []
    
    def _get_spatial_adjective(self, room_type: str, theme: str, adjectives: List[str]) -> str:
        """Get an adjective that fits the room type and theme"""
        
        type_adjectives = {
            "chamber": ["grand", "vast", "spacious", "echoing"],
            "hallway": ["long", "narrow", "winding", "shadowy"],
            "cavern": ["deep", "damp", "mysterious", "cavernous"],
            "tunnel": ["narrow", "dark", "twisting", "confined"],
            "library": ["quiet", "dusty", "ancient", "scholarly"],
            "stairwell": ["steep", "spiraling", "stone", "ascending"],
            "shrine": ["sacred", "holy", "blessed", "divine"],
            "armory": ["organized", "martial", "steel-lined", "weapon-filled"]
        }
        
        # Get room-type specific adjectives first
        type_specific = type_adjectives.get(room_type, [])
        if type_specific:
            return random.choice(type_specific)
        
        # Fall back to theme adjectives
        return random.choice(adjectives) if adjectives else "mysterious"
    
    def _get_spatial_noun(self, room_type: str, theme: str, nouns: List[str]) -> str:
        """Get a noun that fits the room type"""
        
        type_nouns = {
            "chamber": ["pillar", "statue", "altar", "brazier"],
            "hallway": ["torch", "banner", "archway", "door"],
            "cavern": ["stalactite", "crystal", "pool", "echo"],
            "tunnel": ["support beam", "root", "stone", "passage"],
            "library": ["book", "scroll", "tome", "manuscript"],
            "stairwell": ["step", "railing", "landing", "torch"],
            "shrine": ["offering", "candle", "relic", "prayer"],
            "armory": ["weapon", "armor", "shield", "blade"]
        }
        
        type_specific = type_nouns.get(room_type, [])
        if type_specific:
            return random.choice(type_specific)
        
        return random.choice(nouns) if nouns else "object"
    
    def _create_spatial_description(self, room_type: str, adjective: str, noun: str, 
                                  theme: str, from_room: str, direction: str, connections: List[str] = None) -> str:
        """Create a description that makes spatial sense"""
        
        base_descriptions = {
            "chamber": f"You are in a {adjective} {room_type}. {noun.capitalize()}s line the walls.",
            "hallway": f"You are in a {adjective} {room_type}. {noun.capitalize()}s illuminate the path ahead.",
            "cavern": f"You are in a {adjective} {room_type}. {noun.capitalize()}s hang from the ceiling above.",
            "tunnel": f"You are in a {adjective} {room_type}. {noun.capitalize()}s mark your passage.",
            "library": f"You are in a {adjective} {room_type}. {noun.capitalize()}s fill countless shelves.",
            "stairwell": f"You are in a {adjective} {room_type}. {noun.capitalize()}s guide your way.",
            "shrine": f"You are in a {adjective} {room_type}. {noun.capitalize()}s rest upon the altar.",
            "armory": f"You are in a {adjective} {room_type}. {noun.capitalize()}s are displayed on racks."
        }
        
        base_description = base_descriptions.get(room_type, f"You are in a {adjective} {room_type}. {noun.capitalize()}s are scattered around.")
        
        # Add vertical movement hints based on connections
        if connections:
            up_connections = [conn for conn in connections if conn.startswith('up')]
            down_connections = [conn for conn in connections if conn.startswith('down')]
            
            vertical_hints = []
            if up_connections:
                up_hints = {
                    "fantasy": ["A stone stairway winds upward", "Wooden stairs creak above", "Ancient steps lead to higher chambers"],
                    "sci-fi": ["A metal ladder extends upward", "An elevator shaft opens above", "Maintenance tunnels lead upward"],
                    "horror": ["Rotting stairs disappear into darkness above", "A rickety ladder vanishes into shadow", "Creaking steps echo from above"]
                }
                hints = up_hints.get(theme, up_hints["fantasy"])
                vertical_hints.append(random.choice(hints))
                
            if down_connections:
                down_hints = {
                    "fantasy": ["Stone steps descend into darkness", "A wooden trapdoor reveals stairs below", "Ancient passages lead downward"],
                    "sci-fi": ["A maintenance shaft descends below", "An elevator platform waits below", "Metal grating covers a descent"],
                    "horror": ["Decaying steps sink into black depths", "A gaping hole reveals horrors below", "Broken stairs spiral into the abyss"]
                }
                hints = down_hints.get(theme, down_hints["fantasy"])
                vertical_hints.append(random.choice(hints))
            
            if vertical_hints:
                base_description += f" {' '.join(vertical_hints)}."
        
        # Randomly add ASCII art to room descriptions (30% chance)
        if random.random() < 0.3:
            ascii_art = self._generate_room_ascii_art(room_type, theme, adjective, noun)
            if ascii_art:
                base_description = f"{ascii_art}\n\n{base_description}"
        
        return base_description
    
    def _get_room_items(self, room_type: str, theme: str) -> List[str]:
        """Get items appropriate for the room type"""
        
        # OLD HARDCODED APPROACH REMOVED - NOW USING DYNAMIC GENERATION
        
        # REPLACED WITH DYNAMIC GENERATION - NO MORE HARDCODED ITEMS
        # Import LLMNameEngine locally to avoid circular imports
        from core.llm_name_engine import LLMNameEngine
        name_engine = LLMNameEngine(llm=self.llm, fallback_mode=self.fallback_mode)
        
        # Determine item types based on room type
        room_item_types = {
            "chamber": ["weapon", "armor", "potion", "scroll"],
            "hallway": ["weapon", "potion", "scroll"],
            "cavern": ["potion", "weapon", "armor"],
            "tunnel": ["weapon", "potion"],
            "library": ["scroll", "potion"],
            "stairwell": ["weapon", "scroll"],
            "shrine": ["potion", "scroll", "armor"],
            "armory": ["weapon", "armor"]
        }
        
        # Generate 0-2 items dynamically
        dynamic_num_items = random.randint(0, 2)
        dynamic_items = []
        
        for _ in range(dynamic_num_items):
            # Get appropriate item types for this room
            possible_types = room_item_types.get(room_type, ["weapon", "armor", "potion", "scroll"])
            item_type = random.choice(possible_types)
            
            # Determine rarity (mostly common, some uncommon)
            rarity = "common" if random.random() < 0.8 else "uncommon"
            
            # Generate unique item name
            item_name = name_engine.generate_item_name(item_type, theme, rarity)
            dynamic_items.append(item_name)
        
        return dynamic_items
    
    def _get_room_npcs(self, room_type: str, theme: str) -> List[str]:
        """Generate dynamic NPCs appropriate for the room type using LLMNameEngine"""
        
        # Import LLMNameEngine locally to avoid circular imports
        from core.llm_name_engine import LLMNameEngine
        name_engine = LLMNameEngine(llm=self.llm, fallback_mode=self.fallback_mode)
        
        # Determine appropriate NPC roles based on room type
        room_npc_roles = {
            "library": ["sage", "scholar", "keeper"],
            "shrine": ["priest", "guardian", "devotee"],
            "armory": ["guard", "warrior", "smith"],
            "chamber": ["noble", "mage", "advisor"],
            "forge": ["smith", "craftsman"],
            "tent": ["merchant", "traveler"],
            "workshop": ["craftsman", "artisan"]
        }
        
        # 40% chance of generating an NPC
        if random.random() < 0.4:
            # Get appropriate roles for this room type
            possible_roles = room_npc_roles.get(room_type, ["guard", "wanderer", "keeper"])
            npc_role = random.choice(possible_roles)
            
            # Generate dynamic NPC name with role-appropriate title
            npc_name = name_engine.generate_dynamic_name(theme, npc_role, "full")
            return [npc_name]
        
        return []
        
    def get_room(self, room_id: str) -> Optional[Room]:
        """
        Get a room by its ID
        """
        return self.rooms.get(room_id)
    
    def validate_room_connections(self) -> Dict[str, Any]:
        """Validate that all room connections point to valid destinations"""
        issues = {
            "dangling_connections": [],
            "invalid_formats": [],
            "missing_rooms": []
        }
        
        for room_id, room in self.rooms.items():
            for connection in room.connections:
                # Check connection format
                if "_" not in connection:
                    issues["invalid_formats"].append({
                        "room": room_id,
                        "connection": connection,
                        "issue": "Missing underscore separator"
                    })
                    continue
                
                # Extract destination
                parts = connection.split("_", 1)
                if len(parts) != 2:
                    issues["invalid_formats"].append({
                        "room": room_id, 
                        "connection": connection,
                        "issue": "Invalid format"
                    })
                    continue
                
                direction, destination = parts
                
                # Check if destination room exists (only if it should exist)
                # Don't flag rooms that will be generated on demand
                if destination not in self.rooms and not destination.startswith(('north_', 'south_', 'east_', 'west_', 'up_', 'down_')):
                    issues["missing_rooms"].append({
                        "room": room_id,
                        "connection": connection,
                        "destination": destination
                    })
        
        return issues
        
    def get_room_by_location(self, location: str) -> Optional[Room]:
        """
        Get room by location string (alias for get_room)
        """
        return self.get_room(location)
    
    def _get_room_depth(self, room_id: str) -> int:
        """
        Get the depth of a room from its ID (e.g., 'north_3' returns 3)
        """
        if room_id == "start":
            return 0
        try:
            parts = room_id.split("_")
            return int(parts[-1]) if len(parts) > 1 else 1
        except (ValueError, IndexError):
            return 1
    
    def _generate_dynamic_exits(self, room_id: str, depth: int, came_from_direction: str, from_room_id: str = None) -> List[str]:
        """
        Generate dynamic exits based on room depth and procedural rules
        """
        directions = ["north", "south", "east", "west", "up", "down"]
        
        # Always have a way back (opposite of the direction we came from)
        opposite_dir = self._get_opposite_direction(came_from_direction)
        exits = []
        
        # Determine number of exits based on depth and randomness
        # Much longer progression for extended gameplay
        if depth <= 2:
            # Near start, many connections
            num_exits = random.randint(2, 3)
        elif depth <= 5:
            # Early exploration, still well connected
            num_exits = random.randint(2, 3)
        elif depth <= 10:
            # Mid-game, moderate connections
            num_exits = random.randint(1, 3)
        elif depth <= 15:
            # Getting deeper, some dead ends
            num_exits = random.randint(1, 2)
        elif depth <= 25:
            # Deep exploration, more challenging
            num_exits = random.randint(0, 2)
        elif depth <= 40:
            # Very deep, mostly linear paths
            num_exits = random.randint(0, 1)
        else:
            # Ancient depths, rare connections
            num_exits = random.randint(0, 1)
        
        # Reduce dead end chance for better flow
        dead_end_chance = min(0.15, depth * 0.01)  # 1% per depth, max 15%
        if random.random() < dead_end_chance:
            num_exits = 0
        
        if num_exits == 0:
            # Dead end - no exits forward
            return []
        
        # Always include the direction we came from for backtracking
        available_directions = [d for d in directions if d != opposite_dir]
        
        # Select random exits
        exits = random.sample(available_directions, min(num_exits, len(available_directions)))
        
        # Add contextual vertical movement based on room type and depth
        vertical_chance = 0.3  # 30% chance for vertical connections
        if random.random() < vertical_chance:
            # Prefer "up" for surface/shallow areas, "down" for deeper areas
            if depth <= 3:
                # Near surface - more likely to have stairs going up
                if "up" not in exits and "up" in available_directions and random.random() < 0.7:
                    exits.append("up")
            
            if depth >= 2:
                # Deeper areas - more likely to have basements/caverns going down  
                if "down" not in exits and "down" in available_directions and random.random() < 0.6:
                    exits.append("down")
        
        # Add connections
        room_connections = []
        
        # CRITICAL: Add backtrack connection with proper direction_destination format
        if came_from_direction and opposite_dir:
            if from_room_id:
                # Use the actual room we came from for backtracking
                room_connections.append(f"{opposite_dir}_{from_room_id}")
            else:
                # Fallback: Calculate where we came from based on naming conventions
                current_depth = self._get_room_depth(room_id)
                if current_depth > 1:
                    # For rooms like "north_2", create "south_north_1" to go back 
                    prev_depth = current_depth - 1
                    back_room = f"{came_from_direction}_{prev_depth}"
                    room_connections.append(f"{opposite_dir}_{back_room}")
                elif current_depth == 1:
                    # For rooms like "north_1", create "south_start" to go back to start
                    room_connections.append(f"{opposite_dir}_start")
        
        # Add forward connections
        for direction in exits:
            next_depth = self._calculate_next_depth(depth, direction, room_id)
            room_connections.append(f"{direction}_{next_depth}")
        
        # Occasionally add loops back to earlier areas (5% chance)
        if depth > 3 and random.random() < 0.05:
            loop_direction = random.choice(["north", "south", "east", "west"])
            if loop_direction not in [e.split("_")[0] for e in room_connections]:
                # Create a loop back to a shallower depth
                loop_depth = random.randint(1, max(1, depth - 2))
                room_connections.append(f"{loop_direction}_{loop_depth}")
        
        return room_connections
    
    def _calculate_next_depth(self, current_depth: int, direction: str, room_id: str) -> int:
        """
        Calculate next room depth with some variation for interesting paths
        """
        base_depth = current_depth + 1
        
        # 20% chance of staying at same depth (side passages)
        if random.random() < 0.2:
            return current_depth
        
        # 10% chance of going 2 levels deeper (steep descent)
        if random.random() < 0.1:
            return base_depth + 1
        
        # 5% chance of going back one level (ascending passage)
        if current_depth > 1 and random.random() < 0.05:
            return max(1, current_depth - 1)
        
        return base_depth
    
    def _get_opposite_direction(self, direction: str) -> str:
        """
        Get the opposite direction
        """
        if not direction:
            return ""
        
        opposites = {
            "north": "south",
            "south": "north", 
            "east": "west",
            "west": "east",
            "up": "down",
            "down": "up"
        }
        return opposites.get(direction, "")
    
    def generate_room_on_demand(self, room_id: str, from_room_id: str, direction: str) -> Room:
        """
        Generate a room on demand when player tries to move there
        """
        if room_id in self.rooms:
            return self.rooms[room_id]
        
        # Validate room ID length to prevent issues
        if len(room_id) > 50:
            room_id = room_id[:50]  # Truncate overly long room names
        
        # Generate new room
        new_room = self.generate_room(room_id, self.theme, from_room_id, direction)
        self.rooms[room_id] = new_room
        
        return new_room
    
    def _get_depth_reward_items(self, depth: int, theme: str) -> List[str]:
        """
        Get special reward items for reaching certain depths
        """
        depth_rewards = {
            "fantasy": {
                5: ["enchanted compass", "glowing crystal"],
                10: ["ancient map fragment", "magical lantern"],
                15: ["elven cloak", "dwarven hammer"],
                20: ["dragon scale", "phoenix feather"],
                25: ["legendary sword fragment", "crown jewel"],
                30: ["artifact of power", "ancient tome of secrets"],
                35: ["divine relic", "staff of the archmage"],
                40: ["world stone shard", "essence of eternity"]
            },
            "sci-fi": {
                5: ["energy scanner", "data pad"],
                10: ["plasma cell", "neural interface"],
                15: ["quantum core", "gravity manipulator"],
                20: ["alien artifact", "time crystal"],
                25: ["reality anchor", "dimensional key"],
                30: ["consciousness matrix", "universal translator"],
                35: ["stellar engine fragment", "void walker device"],
                40: ["cosmic string", "universe seed"]
            },
            "horror": {
                5: ["cursed locket", "bone charm"],
                10: ["forbidden journal", "ritual dagger"],
                15: ["blood vial", "dark scripture"],
                20: ["soul gem", "necronomicon page"],
                25: ["demon's claw", "wraith essence"],
                30: ["elder sign", "void heart"],
                35: ["nightmare crown", "reality tear"],
                40: ["cosmic horror relic", "sanity shard"]
            },
            "cyberpunk": {
                5: ["neural chip", "encryption key"],
                10: ["AI core fragment", "hologram projector"],
                15: ["black ICE program", "corporate access card"],
                20: ["memory bank", "quantum processor"],
                25: ["consciousness backup", "reality glitch"],
                30: ["system override code", "digital god fragment"],
                35: ["matrix key", "virtual reality engine"],
                40: ["cyber-singularity core", "digital infinity"]
            }
        }
        
        theme_rewards = depth_rewards.get(theme, depth_rewards["fantasy"])
        return theme_rewards.get(depth, [])
    
    def _get_rare_items(self, theme: str) -> List[str]:
        """
        Get very rare items for deep exploration
        """
        rare_items = {
            "fantasy": ["dragon egg", "wish ring", "time turner", "portal stone"],
            "sci-fi": ["singularity device", "wormhole generator", "quantum consciousness", "reality manipulator"],
            "horror": ["elder god essence", "sanity anchor", "nightmare fuel", "cosmic horror ward"],
            "cyberpunk": ["AI singularity", "reality hack", "digital soul", "matrix override"]
        }
        
        theme_rares = rare_items.get(theme, rare_items["fantasy"])
        return [random.choice(theme_rares)] if theme_rares else []
    
    def _generate_room_ascii_art(self, room_type: str, theme: str, adjective: str, noun: str) -> str:
        """
        Generate ASCII art for room descriptions
        """
        if not self.llm or not hasattr(self.llm, 'generate_ascii_art'):
            if self.fallback_mode:
                return self._fallback_room_ascii_art(room_type, theme)
            else:
                raise RuntimeError("LLM with ASCII art capability is required (fallback mode disabled)")
        
        try:
            # Create subjects based on room type and theme
            art_subjects = {
                "chamber": ["grand hall", "throne room", "crystal chamber"],
                "hallway": ["long corridor", "stone passage", "arched hallway"], 
                "cavern": ["mystical cave", "underground cavern", "crystal grotto"],
                "tunnel": ["narrow tunnel", "stone passage", "underground path"],
                "library": ["ancient library", "book chamber", "scroll room"],
                "stairwell": ["spiral staircase", "stone steps", "winding stairs"],
                "shrine": ["sacred altar", "holy shrine", "temple chamber"],
                "armory": ["weapon hall", "armor room", "arsenal chamber"]
            }
            
            subjects = art_subjects.get(room_type, ["mysterious room", "ancient chamber"])
            subject = random.choice(subjects)
            
            # Generate ASCII art with 70% chance for banner, 30% for decoration
            art_type = "banner" if random.random() < 0.7 else "decoration"
            
            # Check if llm is the interface or the actual LLM
            if hasattr(self.llm, 'llm'):
                return self.llm.llm.generate_ascii_art(subject, theme, art_type)
            else:
                return self.llm.generate_ascii_art(subject, theme, art_type)
            
        except Exception as e:
            print(f"Error generating room ASCII art: {e}")
            if self.fallback_mode:
                return self._fallback_room_ascii_art(room_type, theme)
            else:
                raise RuntimeError(f"Room ASCII art generation failed and fallback mode disabled: {e}")
    
    def _fallback_room_ascii_art(self, room_type: str, theme: str) -> str:
        """Fallback ASCII art disabled - LLM generation required"""
        raise RuntimeError("Fallback ASCII art disabled - LLM generation required")
    
    def generate_item_ascii_art(self, item_name: str, theme: str) -> str:
        """
        Generate ASCII art for items (called when items are examined)
        """
        if not self.llm or not hasattr(self.llm, 'generate_ascii_art'):
            if self.fallback_mode:
                return self._fallback_item_ascii_art(item_name, theme)
            else:
                # Instead of failing, return empty string - ASCII art is optional
                return ""
        
        try:
            # Generate object-type ASCII art for items
            # Check if llm is the interface or the actual LLM
            if hasattr(self.llm, 'llm'):
                return self.llm.llm.generate_ascii_art(item_name, theme, "object")
            else:
                return self.llm.generate_ascii_art(item_name, theme, "object")
        except Exception as e:
            print(f"Error generating item ASCII art: {e}")
            if self.fallback_mode:
                return self._fallback_item_ascii_art(item_name, theme)
            else:
                raise RuntimeError(f"Item ASCII art generation failed and fallback mode disabled: {e}")
    
    def _fallback_item_ascii_art(self, item_name: str, theme: str) -> str:
        """Fallback ASCII art disabled - LLM generation required"""
        raise RuntimeError("Fallback item ASCII art disabled - LLM generation required")
    
    def _infer_room_type_from_description(self, description: str) -> str:
        """Infer room type from description text for enemy spawning"""
        description_lower = description.lower()
        
        # Check for specific room type keywords
        if any(word in description_lower for word in ["chamber", "hall", "room"]):
            return "chamber"
        elif any(word in description_lower for word in ["corridor", "hallway", "passage"]):
            return "hallway"  
        elif any(word in description_lower for word in ["cavern", "cave", "grotto"]):
            return "cavern"
        elif any(word in description_lower for word in ["tunnel", "shaft"]):
            return "tunnel"
        elif any(word in description_lower for word in ["library", "study", "archive"]):
            return "library"
        elif any(word in description_lower for word in ["stairs", "stairwell", "steps"]):
            return "stairwell"
        elif any(word in description_lower for word in ["shrine", "altar", "temple"]):
            return "shrine"
        elif any(word in description_lower for word in ["armory", "arsenal", "weapon"]):
            return "armory"
        elif any(word in description_lower for word in ["forest", "woods", "trees"]):
            return "forest"
        elif any(word in description_lower for word in ["grove", "clearing"]):
            return "grove"
        else:
            return "chamber"  # Default fallback
    
    def generate_movement_description(self, from_room_id: str, to_room_id: str, direction: str) -> str:
        """Generate spatially consistent movement description"""
        from_room = self.get_room(from_room_id)
        to_room = self.get_room(to_room_id)
        
        if not from_room or not to_room:
            return f"You move {direction}."
        
        return self.spatial_nav.generate_movement_description(
            from_room_id, to_room_id, direction,
            from_room.description, to_room.description, 
            self.theme
        )
    
    def _store_npc_dialogues(self, npcs: List[Dict], npc_dialogues: Dict, theme: str, narrative_context: Dict = None):
        """Store NPC dialogue data for the conversation system with narrative awareness"""
        for npc in npcs:
            npc_name = npc["name"]
            npc_role = npc["role"]
            
            # Get dialogue data for this NPC
            if npc_name in npc_dialogues:
                dialogue_data = npc_dialogues[npc_name]
            else:
                # Generate dialogue using content generator with narrative context
                if hasattr(self.content_generator, 'create_dynamic_npc_conversation'):
                    if narrative_context:
                        dialogue_data = self.content_generator.create_dynamic_npc_conversation(npc_name, npc_role, theme, narrative_context)
                    else:
                        dialogue_data = self.content_generator.create_dynamic_npc_conversation(npc_name, npc_role, theme)
                else:
                    # Fallback for dialogue generation
                    dialogue_data = {
                        "greeting": f"Hello, traveler. I am {npc_name}.",
                        "topics": ["local area", "dangers ahead", "rumors"],
                        "farewell": "Safe travels!"
                    }
            
            # Store for conversation system
            setattr(self, f'_npc_dialogue_{npc_name.lower().replace(" ", "_")}', dialogue_data)
    
    def get_npc_dialogue_data(self, npc_name: str) -> Optional[Dict]:
        """Get stored dialogue data for an NPC"""
        attr_name = f'_npc_dialogue_{npc_name.lower().replace(" ", "_")}'
        return getattr(self, attr_name, None)
    
    def get_npc_info(self, npc_name: str) -> Optional[Dict]:
        """Get basic NPC info (role, etc.) from room data"""
        for room in self.rooms.values():
            for npc_data in room.npcs:
                if isinstance(npc_data, dict) and npc_data.get("name", "").lower() == npc_name.lower():
                    return npc_data
                elif isinstance(npc_data, str) and npc_data.lower() == npc_name.lower():
                    return {"name": npc_data, "role": "traveler"}
        return None