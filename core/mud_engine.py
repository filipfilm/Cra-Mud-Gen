"""
Main Cra-mud-gen Engine class that orchestrates the game flow
"""
import sys
import os
import random
from typing import Optional, Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.player import Player
from core.world import World
from ui.terminal_ui import TerminalUI
from ui.combat_ui import CombatUI
from core.command_processor import CommandProcessor
from core.combat_system import CombatSystem
from core.conversation_system import ConversationSystem
from core.story_engine import StoryEngine
from core.choice_processor import ChoiceProcessor
from llm.llm_interface import LLMIntegrationLayer
from core.map_system import MapSystem
from core.context_manager import ContextManager
from core.save_system import SaveSystem
from core.narrative_engine import NarrativeEngine
from core.story_seed_generator import StorySeed
from core.crafting_system import CraftingSystem
from core.economy_system import EconomySystem

class GameEngine:
    """
    Main game engine that manages the game loop, state, and interactions
    """
    
    def __init__(self, story_seed: Optional[StorySeed] = None, llm_interface=None, fallback_mode=False):
        self.context_manager = ContextManager()  # Initialize context manager first
        self.player = Player()
        self.ui = TerminalUI(fallback_mode=fallback_mode)
        self.combat_ui = CombatUI()
        self.fallback_mode = fallback_mode
        
        # Use provided LLM interface or create new one
        if llm_interface:
            self.llm = llm_interface
        else:
            # Fallback to old behavior for backward compatibility
            selected_model = self._select_model()
            self.llm = LLMIntegrationLayer(model_name=selected_model)
        
        self.world = World(self.context_manager, self.llm.llm, fallback_mode=fallback_mode)  # Pass LLM to world for ASCII art
        self.command_processor = CommandProcessor()
        self.combat_system = CombatSystem()
        self.conversation_system = ConversationSystem(self.world, self.llm.llm, fallback_mode=fallback_mode)  # Pass world and LLM
        self.story_engine = StoryEngine(self.llm.llm, fallback_mode=fallback_mode)
        self.choice_processor = ChoiceProcessor(self.story_engine, self.llm.llm)
        self.map_system = MapSystem()  # Initialize mapping system
        self.save_system = SaveSystem()  # Initialize save system
        
        # Initialize narrative engine with story seed
        self.narrative_engine = NarrativeEngine(self.llm.llm)
        self.story_seed = story_seed
        self.narrative_state = None
        
        # Initialize crafting system
        self.crafting_system = CraftingSystem(self.llm.llm)
        
        # Initialize economy system
        self.economy_system = EconomySystem(self.llm.llm)
        self._setup_merchant_rooms()
        
        if self.story_seed:
            print(f"Initializing narrative with {self.story_seed.theme} theme...")
            self.narrative_state = self.narrative_engine.initialize_narrative(self.story_seed)
            
            # Pass narrative context to world generation
            self.world.set_narrative_context(self.narrative_state)
        
        self.game_over = False
        
        # Combat state
        self.in_combat = False
        self.current_enemies = []
        self.turn_counter = 0  # For autosave functionality
        
        # Display control
        self.suppress_room_display = False
    
    def _select_model(self) -> str:
        """
        Let user select which Ollama model to use
        """
        # Import here to avoid circular imports
        from llm.ollama_llm import OllamaLLM
        
        try:
            available_models = OllamaLLM.get_available_models()
            if available_models:
                return self.ui.get_model_selection(available_models)
            else:
                print("\n❌ No Ollama models found!")
                print("Please install a model first. Popular options:")
                print("  • ollama pull mistral           (7B - Good for storytelling)")
                print("  • ollama pull llama3.1          (8B - Great general purpose)")
                print("  • ollama pull gemma2:2b         (2B - Fast and lightweight)")
                print("\nAfter installing a model, restart the game.")
                sys.exit(0)
        except Exception as e:
            print(f"❌ Error connecting to Ollama: {e}")
            print("Make sure Ollama is running: ollama serve")
            sys.exit(0)
        
    def run(self):
        """
        Main game loop that runs until the game is over
        """
        try:
            # Initialize game
            self._initialize_game()
            
            # Main game loop
            while not self.game_over:
                # Display current room state (unless suppressed)
                if not self.suppress_room_display:
                    current_room = self.world.get_room(self.player.location)
                    if current_room and not self.game_over:
                        # Enhance room description with Mistral if available
                        self._enhance_room_description(current_room)
                        # Update map with room exits
                        self.map_system.discover_room_exits(self.player.location, current_room.connections)
                        self.ui.display_room(current_room, self.player, self.llm)
                    
                    # Occasionally show ambient atmospheric effects
                    self.ui.maybe_ambient_effect(self.player.theme, self.llm)
                else:
                    # Reset the suppression flag
                    self.suppress_room_display = False
                
                # Get user input
                user_input = self.ui.get_input()
                
                # Process command
                if user_input.strip():
                    # Create context for choice processing
                    current_context = self._build_current_context()
                    
                    # First check if it's a conversation
                    conversation_result = self.conversation_system.parse_conversation_input(user_input)
                    
                    if conversation_result["type"] != "not_conversation":
                        self._handle_conversation(conversation_result)
                        self.suppress_room_display = True
                    else:
                        # Process through choice processor for story significance
                        choice_analysis = self.choice_processor.analyze_player_input(user_input, current_context)
                        
                        if choice_analysis["type"] == "significant_choice":
                            self._handle_significant_choice(choice_analysis)
                        else:
                            # Handle as regular command
                            result = self.command_processor.parse(user_input, self.player, self.world)
                            self._process_command_result(result, current_context)
                
        except KeyboardInterrupt:
            print("\nGame interrupted by user.")
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()
    
    def _initialize_game(self):
        """
        Initialize the game by setting up theme and generating world
        """
        self.ui.display_welcome()
        
        # Use theme from story seed if available
        if self.story_seed and self.story_seed.theme:
            theme = self.story_seed.theme
            print(f"🎨 Using theme from story seed: {theme.title()}")
        else:
            # Fallback to manual selection if no story seed theme
            theme = self.ui.get_theme_selection()
        
        self.player.theme = theme
        self.world.theme = theme
        
        # Generate dungeon
        self.world.generate_dungeon(theme)
        
        # Set player to start room
        self.player.location = "start"
        self.player.current_room_id = "start"
        
        # Initialize story arc
        main_story = self.story_engine.initialize_story_arc(theme)
        print(f"\n🎭 {main_story.title}")
        print(f"📖 {main_story.description}\n")
    
    def _process_command_result(self, result, context=None):
        """
        Process the result of a command execution
        """
        # Commands that should trigger room redisplay
        redisplay_commands = {"movement", "look"}
        
        if result["type"] == "exit":
            self.game_over = True
            self.ui.display_goodbye()
        elif result["type"] == "movement":
            # Save old location before moving
            old_location = self.player.location
            
            # Generate new room if needed with spatial context
            if result["new_location"] not in self.world.rooms:
                new_room = self.world.generate_room(
                    result["new_location"], 
                    self.player.theme, 
                    from_room=old_location,
                    direction=result["direction"]
                )
                self.world.rooms[result["new_location"]] = new_room
            
            # Update player location using the new method that tracks exploration
            self.player.move_to_location(result["new_location"])
            
            # Update map system
            self.map_system.move_player(result["new_location"])
            
            # Add movement to context manager
            self.context_manager.add_movement(
                old_location,
                result["new_location"], 
                result["direction"],
                f"moved {result['direction']} from {old_location}"
            )
            
            # Generate and display spatially aware movement message
            movement_text = self.world.generate_movement_description(
                old_location, result["new_location"], result["direction"]
            )
            self.ui.display_message(movement_text)
            
            # Check for enemy encounters in new room
            self._check_for_enemies(result["new_location"])
        elif result["type"] == "look":
            current_room = self.world.get_room(self.player.location)
            if current_room:
                # Just display the room (already enhanced in main loop)
                self.ui.display_room(current_room, self.player)
        elif result["type"] == "inventory":
            inventory_display = self._get_inventory_display()
            self.ui.display_message(inventory_display)
        elif result["type"] == "help":
            self.ui.display_help(result["message"])
        elif result["type"] == "map":
            # Display the ASCII map
            map_display = self.map_system.generate_ascii_map()
            self.ui.display_message(map_display)
        elif result["type"] == "stats":
            # Display exploration statistics
            stats = self.map_system.get_exploration_stats()
            player_stats = self.player.get_exploration_stats()
            
            stats_message = f"""
EXPLORATION STATISTICS
======================
Current Location: {stats['current_location']}
Rooms Discovered: {stats['rooms_discovered']}
Rooms Visited: {stats['rooms_visited']}
Exploration: {stats['exploration_percentage']:.1f}%
Exploration Points: {player_stats['exploration_points']}

Type 'map' to see your dungeon map!
            """
            self.ui.display_message(stats_message.strip())
        elif result["type"] == "take":
            # Handle taking items from the room
            take_result = self._handle_take_item(result["item"])
            self.ui.display_message(take_result)
        elif result["type"] == "drop":
            # Handle dropping items in the room
            drop_result = self._handle_drop_item(result["item"])
            self.ui.display_message(drop_result)
        elif result["type"] == "use":
            # Handle using items from inventory
            use_result = self._handle_use_item(result["item"])
            self.ui.display_message(use_result)
        elif result["type"] == "examine":
            # Handle examining items with ASCII art and effects
            examine_result = self._handle_examine_item(result["item"])
            self.ui.display_examine_result(examine_result, result["item"], self.player.theme)
        elif result["type"] == "combat_action":
            # Handle combat actions
            if self.in_combat:
                self._handle_combat_action(result)
            else:
                self.ui.display_error("You are not in combat!")
        elif result["type"] == "narrative":
            # Send narrative commands to LLM for immersive responses
            narrative_response = self._generate_narrative_response(result["command"])
            self.ui.display_message(narrative_response)
        elif result["type"] == "save":
            self._handle_save_game(result.get("save_name"))
        elif result["type"] == "load":
            self._handle_load_game(result.get("save_name"))
        elif result["type"] == "quicksave":
            self._handle_quicksave()
        elif result["type"] == "quickload":
            self._handle_quickload()
        elif result["type"] == "list_saves":
            self._handle_list_saves()
        elif result["type"] == "craft":
            self._handle_craft_item(result["recipe"])
        elif result["type"] == "recipes":
            self._handle_show_recipes()
        elif result["type"] == "skills":
            self._handle_show_skills()
        elif result["type"] == "enhance":
            self._handle_enhance_item(result["item"])
        elif result["type"] == "salvage":
            self._handle_salvage_item(result["item"])
        elif result["type"] == "trade":
            self._handle_trade()
        elif result["type"] == "buy":
            self._handle_buy_item(result["item"])
        elif result["type"] == "sell":
            self._handle_sell_item(result["item"])
        elif result["type"] == "haggle":
            self._handle_haggle_item(result["item"])
        elif result["type"] == "shop":
            self._handle_browse_shop()
        elif result["type"] == "prices":
            self._handle_show_prices()
        elif result["type"] == "invalid":
            self.ui.display_error(result["message"])
        
        # Suppress room display for all commands except those that should redisplay
        if result["type"] not in redisplay_commands:
            self.suppress_room_display = True
        
        # Auto-save every 10 turns (not for save/load commands)
        if result["type"] not in ["save", "load", "quicksave", "quickload", "list_saves"]:
            self.turn_counter += 1
            if self.turn_counter % 10 == 0:
                self.save_system.autosave(
                    self.player, self.world, self.story_engine,
                    self.combat_system, self.conversation_system
                )
    
    def _display_game_state(self):
        """
        Display the current game state
        """
        # In a more complete implementation, this would show status bar, etc.
        pass
    
    def _cleanup(self):
        """
        Clean up resources when game ends
        """
        if not self.game_over:
            self.ui.display_goodbye()
    
    def _enhance_room_description(self, room):
        """
        Use Mistral to enhance room descriptions
        """
        if room and self.llm and hasattr(self.llm.llm, 'generate_room_description'):
            # Only enhance if we haven't already enhanced this room
            if not room.enhanced_description:
                try:
                    # Use Mistral's specialized room description method
                    enhanced = self.llm.llm.generate_room_description(
                        room.base_description, 
                        self.player.theme
                    )
                    
                    # Only add if we got a good response
                    if enhanced and "silent" not in enhanced.lower():
                        room.set_enhanced_description(enhanced)
                except:
                    # Fallback to original method
                    context = {
                        "theme": self.player.theme,
                        "room_description": room.base_description,
                        "player_location": room.room_id,
                        "player_health": self.player.health,
                        "inventory": self.player.inventory
                    }
                    
                    prompt = f"Enhance this room description: {room.base_description}"
                    enhanced = self.llm.generate_game_response(prompt, context)
                    
                    if enhanced and "silent" not in enhanced.lower():
                        room.set_enhanced_description(enhanced)
    
    def _generate_movement_text(self, direction):
        """
        Generate enhanced movement descriptions using Mistral
        """
        if self.llm and hasattr(self.llm.llm, 'generate_movement_text'):
            try:
                # Use Mistral's specialized movement text method
                movement_text = self.llm.llm.generate_movement_text(
                    direction, 
                    self.player.theme
                )
                
                # Return enhanced text if we got a good response
                if movement_text and "silent" not in movement_text.lower():
                    return movement_text
            except:
                pass
        
        # Fallback to simple message
        return f"You move {direction}..."
    
    def _generate_narrative_response(self, command):
        """
        Generate narrative responses for unknown commands using Mistral
        """
        if self.llm and hasattr(self.llm.llm, 'generate_response'):
            try:
                # Get current room for context
                current_room = self.world.get_room(self.player.location)
                room_items = current_room.items if current_room else []
                room_npcs = current_room.npcs if current_room else []
                
                # Build rich context with spatial awareness
                player_data = {
                    "theme": self.player.theme,
                    "health": self.player.health,
                    "inventory": self.player.inventory,
                    "inventory_description": self.player.get_inventory_description()
                }
                
                context = self.context_manager.get_llm_context(self.player.location, player_data)
                context.update({
                    "room_items": room_items,
                    "room_npcs": room_npcs,
                    "command": command
                })
                
                # Create a narrative prompt for Mistral
                prompt = f"The player tries to '{command}' in this {self.player.theme} setting. Generate an atmospheric response that fits the world and describes what happens."
                
                # Use Mistral to generate the response
                response = self.llm.llm.generate_response(prompt, context)
                
                # Return enhanced response if we got something good
                if response and "silent" not in response.lower() and "mystical forces" not in response.lower():
                    return response
                    
            except Exception as e:
                print(f"Error generating narrative response: {e}")
        
        # Fallback response for unknown commands
        return f"You try to {command}, but nothing obvious happens."
    
    def _handle_take_item(self, item_name: str) -> str:
        """
        Handle taking an item from the current room
        """
        current_room = self.world.get_room(self.player.location)
        if not current_room:
            return "You can't take anything here."
        
        # Find the item in the room (case-insensitive, partial match)
        item_found = None
        for item in current_room.items:
            if item_name.lower() in item.lower() or item.lower() in item_name.lower():
                item_found = item
                break
        
        if not item_found:
            # Use LLM for narrative response if item not found
            if self.llm:
                context = {
                    "theme": self.player.theme,
                    "room_description": current_room.description,
                    "room_items": current_room.items,
                    "inventory": self.player.inventory,
                    "command": f"take {item_name}"
                }
                
                prompt = f"The player tries to take '{item_name}' but it's not available in the room. The available items are: {', '.join(current_room.items) if current_room.items else 'none'}."
                response = self.llm.llm.generate_response(prompt, context) if hasattr(self.llm, 'llm') else None
                
                if response and "silent" not in response.lower():
                    return response
            
            available = ', '.join(current_room.items) if current_room.items else "nothing"
            return f"There is no '{item_name}' here. Available items: {available}"
        
        # Try to add to inventory
        if self.player.add_to_inventory(item_found):
            current_room.items.remove(item_found)
            
            # Generate narrative response with LLM
            if self.llm and hasattr(self.llm.llm, 'generate_response'):
                try:
                    context = {
                        "theme": self.player.theme,
                        "inventory": self.player.inventory,
                        "item": item_found,
                        "room_description": current_room.description
                    }
                    
                    prompt = f"The player picks up '{item_found}' in a {self.player.theme} setting. Describe this action."
                    response = self.llm.llm.generate_response(prompt, context)
                    
                    if response and "silent" not in response.lower():
                        return f"You take the {item_found}.\n\n{response}"
                except:
                    pass
            
            return f"You take the {item_found}."
        else:
            return "Your inventory is full! Drop something first."
    
    def _handle_drop_item(self, item_name: str) -> str:
        """
        Handle dropping an item in the current room
        """
        # Find the item in inventory
        item_found = self.player.find_item(item_name)
        
        if not item_found:
            return f"You don't have '{item_name}' in your inventory."
        
        # Remove from inventory and add to room
        if self.player.remove_from_inventory(item_found):
            current_room = self.world.get_room(self.player.location)
            if current_room:
                current_room.items.append(item_found)
            
            # Generate narrative response with LLM
            if self.llm and hasattr(self.llm.llm, 'generate_response'):
                try:
                    context = {
                        "theme": self.player.theme,
                        "inventory": self.player.inventory,
                        "item": item_found,
                        "room_description": current_room.description if current_room else "unknown location"
                    }
                    
                    prompt = f"The player drops '{item_found}' in a {self.player.theme} setting. Describe this action."
                    response = self.llm.llm.generate_response(prompt, context)
                    
                    if response and "silent" not in response.lower():
                        return f"You drop the {item_found}.\n\n{response}"
                except:
                    pass
            
            return f"You drop the {item_found}."
        
        return "Something went wrong trying to drop the item."
    
    def _handle_use_item(self, item_name: str) -> str:
        """
        Handle using an item from inventory
        """
        item_found = self.player.find_item(item_name)
        
        if not item_found:
            return f"You don't have '{item_name}' in your inventory."
        
        # Generate narrative response with LLM for using items
        if self.llm and hasattr(self.llm.llm, 'generate_response'):
            try:
                current_room = self.world.get_room(self.player.location)
                context = {
                    "theme": self.player.theme,
                    "inventory": self.player.inventory,
                    "item": item_found,
                    "room_description": current_room.description if current_room else "unknown location",
                    "player_health": self.player.health
                }
                
                prompt = f"The player uses '{item_found}' in a {self.player.theme} setting. What happens when they use this item?"
                response = self.llm.llm.generate_response(prompt, context)
                
                if response and "silent" not in response.lower():
                    return f"You use the {item_found}.\n\n{response}"
            except:
                pass
        
        return f"You use the {item_found}, but nothing obvious happens."
    
    def _handle_examine_item(self, item_name: str) -> str:
        """
        Handle examining an item or environmental feature
        """
        current_room = self.world.get_room(self.player.location)
        
        # Check if item is in inventory or room
        item_found = self.player.find_item(item_name)
        if not item_found and current_room:
            # Check room items
            for item in current_room.items:
                if item_name.lower() in item.lower() or item.lower() in item_name.lower():
                    item_found = item
                    break
        
        # If no item found, check environmental features
        if not item_found and current_room:
            if current_room.has_environmental_feature(item_name):
                return self._examine_environmental_feature(item_name, current_room)
        
        if not item_found:
            # Show what's available to examine
            available_inventory = ', '.join(self.player.inventory) if self.player.inventory else "nothing"
            available_room = ', '.join(current_room.items) if current_room and current_room.items else "nothing"
            available_features = ', '.join(current_room.get_environmental_features()) if current_room else "nothing"
            
            return f"There is no '{item_name}' here or in your inventory.\nInventory: {available_inventory}\nRoom items: {available_room}\nYou can examine: {available_features}"
        
        # Generate ASCII art for the item
        ascii_art = self.world.generate_item_ascii_art(item_found, self.player.theme)
        
        # Generate description using dynamic content generator
        description = self.world.content_generator.get_item_description(item_found, self.player.theme)
        
        return f"{ascii_art}\n\n{description}"
    
    def _examine_environmental_feature(self, feature_name: str, room) -> str:
        """
        Handle examining environmental features in the room
        """
        # Generate detailed description of the environmental feature
        if self.llm and hasattr(self.llm.llm, 'generate_response'):
            try:
                context = {
                    "theme": self.player.theme,
                    "room_description": room.get_description(),
                    "feature": feature_name,
                    "room_type": "dungeon room"
                }
                
                prompt = f"The player examines the {feature_name} in this {self.player.theme} dungeon room. Describe what they see in detail, focusing on the {feature_name}. Keep it atmospheric and immersive."
                
                response = self.llm.llm.generate_response(prompt, context)
                
                if response and "silent" not in response.lower():
                    return f"You examine the {feature_name}:\n\n{response}"
            except Exception as e:
                print(f"Error generating environmental description: {e}")
        
        # Fallback descriptions for common features
        fallback_descriptions = {
            "carvings": f"The ancient carvings are weathered but still visible, depicting scenes from a bygone era of this {self.player.theme} realm.",
            "walls": f"The walls are made of old stone, showing signs of age and the passage of countless adventurers.",
            "ceiling": f"The ceiling looms overhead, decorated in the style typical of {self.player.theme} architecture.",
            "floor": f"The floor is worn smooth by countless footsteps, with small cracks and imperfections telling stories of age.",
            "shadows": f"The shadows dance mysteriously in the flickering light, creating an atmosphere of {self.player.theme} mystery.",
            "doorway": f"The doorway is constructed in classic {self.player.theme} style, sturdy and built to last centuries.",
            "entrance": f"The entrance shows signs of heavy use over the years, with subtle details that speak to its {self.player.theme} origins."
        }
        
        description = fallback_descriptions.get(feature_name.lower(), f"You examine the {feature_name}. It appears to be a typical {self.player.theme} {feature_name}.")
        
        return f"You examine the {feature_name}:\n\n{description}"
    
    def _get_inventory_display(self) -> str:
        """
        Get a formatted display of the player's inventory
        """
        if not self.player.inventory:
            return "\nYour inventory is empty."
        
        inventory_display = f"\nYOUR INVENTORY ({len(self.player.inventory)}/20):\n"
        inventory_display += "=" * 30 + "\n"
        
        for i, item in enumerate(self.player.inventory, 1):
            inventory_display += f"{i:2d}. {item}\n"
        
        inventory_display += "=" * 30
        inventory_display += "\nType 'use <item>' to use an item, 'drop <item>' to drop it."
        
        return inventory_display
    
    def _check_for_enemies(self, room_id: str):
        """Check for enemies when entering a new room"""
        current_room = self.world.get_room(room_id)
        if not current_room:
            return
            
        # Check if player has been in this room before
        has_been_visited = room_id in self.player.visited_rooms
        
        # Spawn enemies if appropriate
        enemies = self.world.spawn_enemies_in_room(current_room, self.player.level, has_been_visited)
        
        if enemies:
            self.current_enemies = enemies
            self.in_combat = True
            self.combat_ui.display_combat_start(enemies, self.player.name)
            self._run_combat()
    
    def _run_combat(self):
        """Main combat loop"""
        combat_result = self.combat_system.start_combat(self.player, self.current_enemies)
        
        while self.in_combat and not self.game_over:
            # Display combat status
            self.combat_ui.display_combat_status(self.player, self.current_enemies)
            self.combat_ui.display_combat_actions()
            
            # Get player action
            action_input = self.combat_ui.prompt_combat_action(
                [e for e in self.current_enemies if not e.is_dead]
            )
            
            # Process player action
            player_result = self._process_player_combat_action(action_input)
            
            if "flee_success" in player_result.get("effects", []):
                self._end_combat(fled=True)
                return
            
            # Check if combat is over
            is_over, outcome = self.combat_system.is_combat_over(self.player, self.current_enemies)
            if is_over:
                self._end_combat(outcome)
                return
            
            # Enemy turns
            for enemy in self.current_enemies:
                if not enemy.is_dead and not self.game_over:
                    self._process_enemy_turn(enemy)
                    
                    # Check if player died
                    is_over, outcome = self.combat_system.is_combat_over(self.player, self.current_enemies)
                    if is_over:
                        self._end_combat(outcome)
                        return
    
    def _process_player_combat_action(self, action_input: str) -> Dict:
        """Process player's combat action"""
        # Parse the action using command processor
        result = self.command_processor.parse(action_input, self.player, self.world)
        
        if result["type"] == "combat_action":
            return self._handle_combat_action(result)
        else:
            self.ui.display_error("Invalid combat action!")
            return {"effects": []}
    
    def _handle_combat_action(self, result: Dict):
        """Handle a combat action"""
        from core.combat_system import ActionType, CombatAction
        
        action_type = result["action"]
        
        if action_type == "attack":
            target_name = result.get("target", "")
            target = self._find_enemy_by_name(target_name)
            
            if target:
                action = CombatAction(ActionType.ATTACK, target.name)
                combat_result = self.combat_system.execute_turn(
                    self.player, action, self.current_enemies
                )
                
                # Display attack result
                if combat_result["damage_dealt"] > 0:
                    is_critical = "critical" in combat_result.get("effects", [])
                    self.combat_ui.display_attack_result(
                        self.player.name, target.name, combat_result["damage_dealt"], is_critical
                    )
                    
                    if target.is_dead:
                        self.combat_ui.display_death(target.name, False)
                
                return combat_result
            else:
                self.ui.display_error(f"Cannot find enemy: {target_name}")
                return {"effects": []}
                
        elif action_type == "defend":
            action = CombatAction(ActionType.DEFEND, "self")
            combat_result = self.combat_system.execute_turn(
                self.player, action, []
            )
            self.ui.display_message(f"{self.player.name} takes a defensive stance!")
            return combat_result
            
        elif action_type == "flee":
            action = CombatAction(ActionType.FLEE, "self") 
            combat_result = self.combat_system.execute_turn(
                self.player, action, []
            )
            if "flee_success" in combat_result.get("effects", []):
                self.combat_ui.display_flee_success()
            else:
                self.combat_ui.display_flee_failure()
            return combat_result
            
        elif action_type == "heal":
            # Check for healing items in inventory
            healing_items = [item for item in self.player.inventory if "potion" in item.lower()]
            if healing_items:
                item_name = healing_items[0]
                from core.combat_system import HealthSystem
                healing, description = HealthSystem.use_healing_item(item_name, self.player.level)
                
                actual_healing = self.player.heal(healing)
                self.player.remove_from_inventory(item_name)
                
                self.combat_ui.display_healing(self.player.name, actual_healing)
                return {"effects": ["healing"]}
            else:
                self.ui.display_error("You don't have any healing potions!")
                return {"effects": []}
    
    def _process_enemy_turn(self, enemy):
        """Process an enemy's combat turn"""
        from core.combat_system import ActionType, CombatAction
        
        # Enemy AI chooses action
        action_type = enemy.choose_action(self.player.current_health, self.player.level)
        
        if action_type == ActionType.ATTACK:
            action = CombatAction(ActionType.ATTACK, self.player.name)
            combat_result = self.combat_system.execute_turn(enemy, action, [self.player])
            
            # Display attack result
            if combat_result["damage_dealt"] > 0:
                is_critical = "critical" in combat_result.get("effects", [])
                self.combat_ui.display_attack_result(
                    enemy.name, self.player.name, combat_result["damage_dealt"], is_critical
                )
                
                if self.player.is_dead:
                    self.combat_ui.display_death(self.player.name, True)
                    
        elif action_type == ActionType.DEFEND:
            action = CombatAction(ActionType.DEFEND, "self")
            self.combat_system.execute_turn(enemy, action, [])
            self.ui.display_message(f"{enemy.name} takes a defensive stance!")
            
        elif action_type == ActionType.FLEE:
            # Enemy attempts to flee
            if random.random() < 0.3:  # 30% chance for enemy to flee
                self.ui.display_message(f"{enemy.name} flees from combat!")
                enemy.is_dead = True  # Remove from combat
    
    def _find_enemy_by_name(self, target_name: str):
        """Find enemy by name (case-insensitive partial match)"""
        target_name_lower = target_name.lower()
        for enemy in self.current_enemies:
            if not enemy.is_dead and target_name_lower in enemy.name.lower():
                return enemy
        return None
    
    def _end_combat(self, outcome: str = "victory", fled: bool = False):
        """End combat and handle rewards/consequences"""
        self.in_combat = False
        
        if fled:
            self.ui.display_message("You have fled from combat!")
        elif outcome == "victory":
            # Calculate rewards
            defeated_enemies = [e for e in self.current_enemies if e.is_dead]
            rewards = self.combat_system.calculate_rewards(defeated_enemies, self.player.level)
            
            # Apply rewards
            self.player.stats["experience"] += rewards["experience"]
            self.player.stats["gold"] += rewards["gold"]
            
            for item in rewards["loot"]:
                if self.player.add_to_inventory(item):
                    pass  # Successfully added
                else:
                    self.ui.display_message(f"Inventory full! {item} left behind.")
            
            # Check for level up
            level_up_result = self.player.level_up_if_ready()
            if level_up_result["leveled_up"]:
                self.combat_ui.display_level_up(
                    self.player.name,
                    level_up_result["old_level"], 
                    level_up_result["new_level"],
                    [f"Health increased by {level_up_result['health_gained']}!"]
                )
            
            # Display rewards
            self.combat_ui.display_combat_victory(rewards)
            
        elif outcome == "defeat":
            self.combat_ui.display_combat_defeat()
            self.game_over = True
        
        # Clear combat state
        self.current_enemies = []
    
    def _handle_conversation(self, conversation_result: Dict):
        """Handle conversation with NPCs"""
        if conversation_result["type"] == "start_conversation":
            npc_name = conversation_result["npc"]
            message = conversation_result["message"]
            
            # Start conversation
            response = self.conversation_system.start_conversation(npc_name, message)
            self.ui.display_message(response)
            
        elif conversation_result["type"] == "continue_conversation":
            message = conversation_result["message"]
            
            # Continue existing conversation
            current_npc = self.conversation_system.context.current_npc
            if current_npc:
                # Find the NPC object to continue conversation
                npc_key = None
                for key, npc in self.conversation_system.npcs.items():
                    if npc.name == current_npc:
                        npc_key = key
                        break
                
                if npc_key:
                    response = self.conversation_system._process_conversation(
                        self.conversation_system.npcs[npc_key], 
                        message
                    )
                    self.ui.display_message(response)
                else:
                    # NPC not found - check if it's a dynamic NPC
                    npc_dialogue = self.world.get_npc_dialogue_data(current_npc)
                    if npc_dialogue:
                        dynamic_npc = self.conversation_system._create_dynamic_npc_personality(current_npc, npc_dialogue)
                        response = self.conversation_system._process_conversation(dynamic_npc, message)
                        self.ui.display_message(response)
                    else:
                        # End the conversation and process the command normally
                        self.conversation_system._end_conversation()
                        result = self.command_processor.parse(message, self.player, self.world)
                        self._process_command_result(result, self._build_current_context())
            else:
                # End the conversation and process the command normally
                self.conversation_system._end_conversation()
                result = self.command_processor.parse(message, self.player, self.world)
                self._process_command_result(result, self._build_current_context())
    
    def _build_current_context(self) -> Dict[str, Any]:
        """Build current context for story/choice processing"""
        current_room = self.world.get_room(self.player.location)
        
        context = {
            "location": self.player.location,
            "theme": self.player.theme,
            "npcs": current_room.npcs if current_room else [],
            "items": current_room.items if current_room else [],
            "player_health": self.player.current_health,
            "player_level": self.player.level,
            "inventory": self.player.inventory,
            "in_combat": self.in_combat,
            "world_tension": self.story_engine.world_state["tension_level"],
            "moral_alignment": self.story_engine.player_history["moral_alignment"],
            "story_complexity": len(self.story_engine.story_threads)
        }
        
        # Add situational flags
        if current_room and current_room.npcs:
            context["combat_possible"] = True
        
        if self.in_combat:
            context["dangerous_situation"] = True
        
        return context
    
    def _handle_significant_choice(self, choice_analysis: Dict):
        """Handle a significant story choice"""
        story_result = choice_analysis["story_result"]
        
        # Display narrative response
        if story_result.get("narrative"):
            self.ui.display_message(story_result["narrative"])
        
        # Handle immediate consequences
        for consequence in story_result.get("immediate_consequences", []):
            self._apply_consequence(consequence)
        
        # Show world state changes if significant
        world_changes = story_result.get("world_state_changes", {})
        if any(change > 10 for change in world_changes.values()):
            self._display_world_state_change(world_changes)
        
        # Check for dynamic encounters triggered by choice
        if story_result.get("moral_impact", 0) != 0:
            self._maybe_trigger_dynamic_encounter()
        
        self.suppress_room_display = True
    
    def _apply_consequence(self, consequence: Dict):
        """Apply an immediate consequence"""
        consequence_type = consequence["type"]
        
        if consequence_type == "combat_initiated":
            # Generate enemies for combat
            current_room = self.world.get_room(self.player.location)
            if current_room:
                enemies = self.world.spawn_enemies_in_room(current_room, self.player.level, False)
                if enemies:
                    self.current_enemies = enemies
                    self.in_combat = True
                    self.combat_ui.display_combat_start(enemies, self.player.name)
                    
        elif consequence_type == "reputation_gain":
            self.ui.display_message(f"✨ {consequence['description']}")
            
        elif consequence_type == "reputation_loss":
            self.ui.display_message(f"💀 {consequence['description']}")
    
    def _display_world_state_change(self, changes: Dict):
        """Display significant world state changes"""
        messages = []
        
        if changes.get("tension_level", 0) > 10:
            messages.append("⚡ The air grows thick with tension...")
            
        if changes.get("chaos_factor", 0) > 10:
            messages.append("🌪️ Chaos spreads through the realm...")
            
        if changes.get("mystery_depth", 0) > 10:
            messages.append("🔮 The mysteries deepen around you...")
        
        for message in messages:
            self.ui.display_message(message)
    
    def _maybe_trigger_dynamic_encounter(self):
        """Maybe trigger a dynamic encounter based on story state"""
        if random.random() < 0.3:  # 30% chance
            current_room = self.world.get_room(self.player.location)
            if current_room:
                encounter = self.story_engine.generate_dynamic_encounter(
                    self.player.location,
                    self.player.theme
                )
                
                if encounter:
                    self._present_dynamic_encounter(encounter)
    
    def _present_dynamic_encounter(self, encounter: Dict):
        """Present a dynamic encounter to the player"""
        print(f"\n🎪 {encounter['description']}")
        print(f"⚖️ Stakes: {encounter['stakes']}")
        
        if encounter.get('npc'):
            print(f"👤 {encounter['npc']}")
        
        print(f"\n💭 What do you choose?")
        for i, choice in enumerate(encounter['choices'], 1):
            print(f"  {i}. {choice}")
        
        print()  # Add spacing
    
    def _handle_save_game(self, save_name: str = None):
        """Handle saving the game"""
        success = self.save_system.save_game(
            self.player, self.world, self.story_engine, 
            self.combat_system, self.conversation_system, save_name
        )
        if success:
            self.ui.display_message("💾 Game saved successfully!")
        else:
            self.ui.display_error("❌ Failed to save game!")
    
    def _handle_load_game(self, save_name: str = None):
        """Handle loading a saved game"""
        if save_name:
            # Load specific save
            save_data = self.save_system.load_game(save_name)
        else:
            # Show save list if no name specified
            saves = self.save_system.list_saves()
            if not saves:
                self.ui.display_message("No saved games found.")
                return
            
            self.ui.display_message("📁 Available saves:")
            for i, save in enumerate(saves[:10], 1):  # Show up to 10 saves
                timestamp = save['timestamp'][:19] if save['timestamp'] != 'Unknown' else 'Unknown'
                self.ui.display_message(f"{i}. {save['display_name']} - Level {save['player_level']} - {timestamp}")
            
            try:
                choice = input("\nEnter save number to load (or 'cancel'): ").strip()
                if choice.lower() == 'cancel':
                    self.ui.display_message("Load cancelled.")
                    return
                
                save_index = int(choice) - 1
                if 0 <= save_index < len(saves):
                    save_data = self.save_system.load_game(saves[save_index]['filename'])
                else:
                    self.ui.display_error("Invalid save number!")
                    return
            except (ValueError, KeyboardInterrupt):
                self.ui.display_message("Load cancelled.")
                return
        
        if save_data:
            self._restore_game_state(save_data)
            self.ui.display_message("📂 Game loaded successfully!")
        else:
            self.ui.display_error("❌ Failed to load game!")
    
    def _handle_quicksave(self):
        """Handle quick save"""
        success = self.save_system.quick_save(
            self.player, self.world, self.story_engine,
            self.combat_system, self.conversation_system
        )
        if success:
            self.ui.display_message("⚡ Quick save completed!")
        else:
            self.ui.display_error("❌ Quick save failed!")
    
    def _handle_quickload(self):
        """Handle quick load"""
        save_data = self.save_system.quick_load()
        if save_data:
            self._restore_game_state(save_data)
            self.ui.display_message("⚡ Quick load completed!")
        else:
            self.ui.display_error("❌ No quick save found!")
    
    def _handle_list_saves(self):
        """Handle listing all save files"""
        saves = self.save_system.list_saves()
        if not saves:
            self.ui.display_message("No saved games found.")
            return
        
        self.ui.display_message(f"📁 Found {len(saves)} saved games:")
        for i, save in enumerate(saves, 1):
            timestamp = save['timestamp'][:19] if save['timestamp'] != 'Unknown' else 'Unknown'
            self.ui.display_message(f"{i:2}. {save['display_name']}")
            self.ui.display_message(f"    Level {save['player_level']} at {save['location']} - {timestamp}")
    
    def _restore_game_state(self, save_data: Dict[str, Any]):
        """Restore game state from save data"""
        try:
            # Restore player state
            player_data = save_data['player']
            self.player.location = player_data['location']
            self.player.current_room_id = player_data['current_room_id']
            self.player.theme = player_data['theme']
            self.player.inventory = player_data['inventory'].copy()
            self.player.stats = player_data['stats'].copy()
            
            # Restore combat stats if available
            if 'combat_stats' in player_data:
                self.player.combat_stats = player_data['combat_stats'].copy()
            if 'health' in player_data:
                self.player.current_health = player_data['health']
            if 'max_health' in player_data:
                self.player.max_health = player_data['max_health']
            if 'level' in player_data:
                self.player.level = player_data['level']
            
            # Restore world state
            world_data = save_data['world']
            self.world.theme = world_data['theme']
            
            # Restore rooms
            self.world.rooms.clear()
            for room_id, room_data in world_data['rooms'].items():
                from core.room import Room
                room = Room(
                    room_id=room_data['room_id'],
                    description=room_data['description'],
                    items=room_data['items'].copy(),
                    npcs=room_data['npcs'].copy(),
                    connections=room_data['connections'].copy()
                )
                room.visited = room_data.get('visited', False)
                room.depth = room_data.get('depth', 0)
                self.world.rooms[room_id] = room
            
            # Restore other world data
            if 'room_counter' in world_data:
                self.world.room_counter = world_data['room_counter']
            if 'generated_depth' in world_data:
                self.world.generated_depth = world_data['generated_depth']
            
            # Restore story engine state if available
            if 'story' in save_data and save_data['story']:
                story_data = save_data['story']
                if 'player_history' in story_data:
                    self.story_engine.player_history = story_data['player_history'].copy()
                if 'world_state' in story_data:
                    self.story_engine.world_state = story_data['world_state'].copy()
                if 'narrative_memory' in story_data:
                    self.story_engine.narrative_memory = story_data['narrative_memory'].copy()
            
            # Restore conversation state if available
            if 'conversation' in save_data and save_data['conversation']:
                conv_data = save_data['conversation']
                if 'context' in conv_data:
                    context = conv_data['context']
                    self.conversation_system.context.current_npc = context.get('current_npc')
                    self.conversation_system.context.conversation_history = context.get('conversation_history', []).copy()
                    self.conversation_system.context.npc_memory = context.get('npc_memory', {}).copy()
                    self.conversation_system.context.last_topic = context.get('last_topic')
                    self.conversation_system.context.conversation_active = context.get('conversation_active', False)
            
            # Update map system with current player location
            self.map_system.set_player_location(self.player.location)
            
            print(f"Restored to Level {self.player.stats.get('level', 1)} at {self.player.location}")
            
        except Exception as e:
            self.ui.display_error(f"Error restoring game state: {e}")
            print(f"Restore error: {e}")  # Debug info
    
    def _handle_craft_item(self, recipe_name: str):
        """Handle crafting an item"""
        # Check if recipe is known
        if recipe_name not in self.player.crafting.discovered_recipes:
            self.ui.display_error(f"You don't know how to craft '{recipe_name}'")
            return
        
        # Attempt to craft the item
        success, crafted_item, message = self.crafting_system.craft_item(
            recipe_name, 
            self.player.crafting.skill_levels,
            station=None,  # Could check current room for crafting stations
            luck_bonus=0.0
        )
        
        if success:
            # Add to inventory and give experience
            if crafted_item:
                self.player.inventory.append(crafted_item.get_display_name())
                recipe = self.crafting_system.recipes[recipe_name]
                self.player.crafting.gain_experience(recipe.skill, recipe.experience_reward)
                self.player.crafting.crafted_items_history.append(crafted_item.name)
                
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
    
    def _handle_show_recipes(self):
        """Show all discovered recipes"""
        if not self.player.crafting.discovered_recipes:
            print("You haven't discovered any recipes yet.")
            print("Try examining items, talking to NPCs, or reading books to learn recipes!")
            return
        
        print("=== Known Recipes ===")
        for recipe_name in self.player.crafting.discovered_recipes:
            if recipe_name in self.crafting_system.recipes:
                recipe = self.crafting_system.recipes[recipe_name]
                skill_level = self.player.crafting.skill_levels.get(recipe.skill, 0)
                can_craft = "✓" if skill_level >= recipe.skill_level_required else "✗"
                print(f"{can_craft} {recipe.name} ({recipe.skill.value} {recipe.skill_level_required})")
    
    def _handle_show_skills(self):
        """Show crafting skill levels and experience"""
        print("=== Crafting Skills ===")
        from core.crafting_system import CraftingSkill
        
        for skill in CraftingSkill:
            level = self.player.crafting.skill_levels[skill]
            exp = self.player.crafting.skill_experience[skill]
            next_exp = self.player.crafting.get_exp_for_next_level(skill)
            
            print(f"{skill.value.title()}: Level {level} ({exp}/{next_exp} XP)")
            
        # Show achievements
        if self.player.crafting.crafting_achievements:
            print("\n=== Achievements ===")
            for achievement in self.player.crafting.crafting_achievements:
                print(f"🏆 {achievement.replace('_', ' ').title()}")
    
    def _handle_enhance_item(self, item_name: str):
        """Handle enhancing an existing item"""
        # For now, show available enhancement options
        enhancements = {
            "sharpen": "Increase damage (needs whetstone)",
            "reinforce": "Increase durability (needs metal plates)",
            "enchant_fire": "Add fire damage (needs fire crystal + enchanting dust)",
            "soul_bind": "Bind to your soul (needs soul gem)"
        }
        
        print(f"=== Enhancement Options for '{item_name}' ===")
        for enhancement, description in enhancements.items():
            print(f"• {enhancement}: {description}")
        print("\nUse 'enhance <item> <type>' to enhance (not yet implemented)")
    
    def _handle_salvage_item(self, item_name: str):
        """Handle salvaging materials from an item"""
        # Check if item is in inventory
        item_found = None
        for item in self.player.inventory:
            if item_name.lower() in item.lower():
                item_found = item
                break
        
        if not item_found:
            print(f"You don't have '{item_name}' in your inventory.")
            return
        
        # For now, give some basic materials
        print(f"Salvaging '{item_found}'...")
        print("You recover some basic materials.")
        print("Note: Full salvaging system not yet implemented.")
        
        # Remove item from inventory
        self.player.inventory.remove(item_found)
    
    def _handle_trade(self):
        """Handle talking to a merchant in current room"""
        merchant = self.economy_system.get_merchant_in_room(self.player.location)
        
        if not merchant:
            print("There's no merchant here to trade with.")
            print("Try looking for shops in places like 'market_square', 'forge', or 'dark_alley'.")
            return
        
        # Check if merchant is open
        if not merchant.is_open(datetime.now()):
            schedule = merchant.schedule.get("weekday", (8, 20))
            print(f"{merchant.name} is currently closed.")
            print(f"Shop hours: {schedule[0]}:00 - {schedule[1]}:00")
            return
        
        # Display merchant greeting based on personality
        if merchant.personality.get("friendly"):
            greeting = f"{merchant.name} greets you warmly: 'Welcome to my shop!'"
        elif merchant.personality.get("gruff"):
            greeting = f"{merchant.name} grunts: 'What do you want?'"
        elif merchant.personality.get("mysterious"):
            greeting = f"{merchant.name} speaks softly: 'Looking for something... special?'"
        else:
            greeting = f"{merchant.name}: 'How can I help you?'"
        
        print(greeting)
        print(f"Your gold: {self.player.stats['gold']}")
        print("Use 'shop' to see items, 'buy <item>' to purchase, 'sell <item>' to sell.")
        
        # Show reputation if significant
        if merchant.reputation_with_player != 0:
            rep_desc = "likes" if merchant.reputation_with_player > 0 else "dislikes"
            print(f"({merchant.name} {rep_desc} you)")
    
    def _handle_browse_shop(self):
        """Browse merchant's inventory"""
        merchant = self.economy_system.get_merchant_in_room(self.player.location)
        
        if not merchant:
            print("There's no merchant here.")
            return
        
        if not merchant.inventory:
            print(f"{merchant.name} has nothing for sale right now.")
            return
        
        print(f"=== {merchant.name}'s Shop ===")
        print(f"Your gold: {self.player.stats['gold']}")
        print()
        
        for i, item in enumerate(merchant.inventory, 1):
            price = merchant.get_selling_price(item, merchant.reputation_with_player)
            can_afford = "✓" if self.player.stats['gold'] >= price else "✗"
            rarity_color = {
                "common": "",
                "uncommon": "🟢",
                "rare": "🔵", 
                "epic": "🟣",
                "legendary": "🟡"
            }.get(item.rarity, "")
            
            print(f"{can_afford} {i}. {rarity_color}{item.name} - {price} gold ({item.rarity})")
        
        print()
        print("Use 'buy <item name>' to purchase an item.")
        if merchant.haggle_skill > 30:
            print("You can try to 'haggle <item name>' for a better price.")
    
    def _handle_buy_item(self, item_name: str):
        """Handle buying an item from merchant"""
        merchant = self.economy_system.get_merchant_in_room(self.player.location)
        
        if not merchant:
            print("There's no merchant here to buy from.")
            return
        
        # Find item in merchant's inventory
        item = self.economy_system.find_item_in_merchant(merchant, item_name)
        if not item:
            print(f"{merchant.name} doesn't have '{item_name}'.")
            return
        
        # Conduct trade
        success, message, gold_change = self.economy_system.conduct_trade(
            merchant, item, True, self.player.stats['gold']
        )
        
        if success:
            # Add item to player inventory and deduct gold
            self.player.inventory.append(item.name)
            self.player.stats['gold'] += gold_change  # gold_change is negative for buying
            print(f"✓ {message}")
            
            # Improve reputation slightly
            merchant.reputation_with_player += 2
        else:
            print(f"✗ {message}")
    
    def _handle_sell_item(self, item_name: str):
        """Handle selling an item to merchant"""
        merchant = self.economy_system.get_merchant_in_room(self.player.location)
        
        if not merchant:
            print("There's no merchant here to sell to.")
            return
        
        # Find item in player inventory
        item_found = None
        for inv_item in self.player.inventory:
            if item_name.lower() in inv_item.lower():
                item_found = inv_item
                break
        
        if not item_found:
            print(f"You don't have '{item_name}' to sell.")
            return
        
        # Convert to TradeGood (simplified - would normally look up in economy system)
        from core.economy_system import TradeGood
        trade_item = TradeGood(item_found, 50, "common", "common")  # Default values
        
        # Check if merchant is interested
        price = merchant.get_buying_price(trade_item, merchant.reputation_with_player)
        
        if price < 1:
            print(f"{merchant.name} isn't interested in that item.")
            return
        
        # Conduct trade
        success, message, gold_change = self.economy_system.conduct_trade(
            merchant, trade_item, False, self.player.stats['gold']
        )
        
        if success:
            # Remove item from player inventory and add gold
            self.player.inventory.remove(item_found)
            self.player.stats['gold'] += gold_change  # gold_change is positive for selling
            print(f"✓ {message}")
            
            # Improve reputation slightly
            merchant.reputation_with_player += 1
        else:
            print(f"✗ {message}")
    
    def _handle_haggle_item(self, item_name: str):
        """Handle haggling with merchant"""
        merchant = self.economy_system.get_merchant_in_room(self.player.location)
        
        if not merchant:
            print("There's no merchant here to haggle with.")
            return
        
        # Find item in merchant's inventory
        item = self.economy_system.find_item_in_merchant(merchant, item_name)
        if not item:
            print(f"{merchant.name} doesn't have '{item_name}' to haggle over.")
            return
        
        # Attempt to haggle (using player level as crude charisma substitute)
        player_charisma = self.player.stats.get('level', 1)
        success, final_price, message = self.economy_system.haggle(
            merchant, item, True, player_charisma
        )
        
        print(message)
        
        if success:
            print(f"New price: {final_price} gold")
            print("Use 'buy {item_name}' to purchase at the haggled price.")
        
        # Store haggled price temporarily (simplified implementation)
        if not hasattr(merchant, 'haggled_prices'):
            merchant.haggled_prices = {}
        merchant.haggled_prices[item.name] = final_price
    
    def _handle_show_prices(self):
        """Show current market prices and economic events"""
        print("=== Market Report ===")
        
        # Show active economic events
        if self.economy_system.economic_events:
            print("📈 Current Economic Events:")
            for event_data in self.economy_system.economic_events:
                event = event_data["event"]
                remaining = event_data["duration"] - (self.economy_system.current_tick - event_data["started"])
                print(f"  • {event.value.title()} (expires in {remaining} days)")
            print()
        
        # Show sample prices
        print("💰 Sample Market Prices:")
        sample_items = ["health_potion", "iron_sword", "leather_armor", "iron_ore"]
        
        modifiers = self.economy_system._get_economic_modifiers()
        for item_name in sample_items:
            if item_name in self.economy_system.base_goods:
                item = self.economy_system.base_goods[item_name]
                current_price = item.get_current_price(modifiers)
                base_price = item.base_price
                
                if current_price > base_price:
                    trend = "📈"
                elif current_price < base_price:
                    trend = "📉"
                else:
                    trend = "➡️"
                    
                print(f"  {trend} {item.name}: {current_price}g (base: {base_price}g)")
        
        print()
        print("Visit merchants to see their specific prices and inventory!")
        
        # Simulate one economic tick
        self.economy_system.simulate_economy_tick()
    
    def _setup_merchant_rooms(self):
        """Create special merchant rooms in the world"""
        from core.room import Room
        
        # Market Square - General merchant
        market_square = Room(
            room_id="market_square",
            description="A bustling market square filled with the sounds of commerce. Wooden stalls line the cobblestone plaza, and merchants hawk their wares to passing travelers. The air is thick with the scent of spices and fresh bread.",
            items=["merchant_sign", "coin_purse"],
            npcs=["Marcus the Trader"],
            connections=["start_room"]
        )
        market_square.visited = False
        market_square.depth = 1
        self.world.rooms["market_square"] = market_square
        
        # Forge - Weaponsmith
        forge = Room(
            room_id="forge",
            description="A sweltering smithy filled with the ring of hammer on anvil. Glowing embers dance in the forge's heart while weapons and armor hang from the walls. The air shimmers with heat.",
            items=["anvil", "hammer", "cooling_barrel"],
            npcs=["Thorin Ironforge"],
            connections=["market_square"]
        )
        forge.visited = False
        forge.depth = 2
        self.world.rooms["forge"] = forge
        
        # Dark Alley - Black market
        dark_alley = Room(
            room_id="dark_alley",
            description="A shadowy alley where few dare to tread. Whispers echo from hidden alcoves, and the air carries hints of danger and forbidden dealings. Cloaked figures move in the darkness.",
            items=["hooded_cloak", "mysterious_package"],
            npcs=["Shadow"],
            connections=["market_square"]
        )
        dark_alley.visited = False
        dark_alley.depth = 2
        self.world.rooms["dark_alley"] = dark_alley
        
        # Add connections back to starting room
        if "start_room" in self.world.rooms:
            start_room = self.world.rooms["start_room"]
            start_room.connections.extend(["market_square"])
        
        # Stock merchants with initial inventory
        for merchant_id, merchant in self.economy_system.merchants.items():
            if merchant_id != "traveling":  # Traveling merchant appears randomly
                self.economy_system._restock_merchants()