"""
Main MUD Engine class that orchestrates the game flow
"""
import sys
import os
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.player import Player
from core.world import World
from ui.terminal_ui import TerminalUI
from core.command_processor import CommandProcessor
from llm.llm_interface import LLMIntegrationLayer
from core.map_system import MapSystem
from core.context_manager import ContextManager

class GameEngine:
    """
    Main game engine that manages the game loop, state, and interactions
    """
    
    def __init__(self):
        self.context_manager = ContextManager()  # Initialize context manager first
        self.player = Player()
        self.llm = LLMIntegrationLayer()  # Initialize LLM integration
        self.world = World(self.context_manager, self.llm.llm)  # Pass LLM to world for ASCII art
        self.command_processor = CommandProcessor()
        self.ui = TerminalUI()
        self.map_system = MapSystem()  # Initialize mapping system
        self.game_over = False
        
    def run(self):
        """
        Main game loop that runs until the game is over
        """
        try:
            # Initialize game
            self._initialize_game()
            
            # Main game loop
            while not self.game_over:
                # Display current room state
                current_room = self.world.get_room(self.player.location)
                if current_room and not self.game_over:
                    # Enhance room description with Mistral if available
                    self._enhance_room_description(current_room)
                    # Update map with room exits
                    self.map_system.discover_room_exits(self.player.location, current_room.connections)
                    self.ui.display_room(current_room, self.player)
                
                # Get user input
                user_input = self.ui.get_input()
                
                # Process command
                if user_input.strip():
                    result = self.command_processor.parse(user_input, self.player, self.world)
                    self._process_command_result(result)
                
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
        
        # Select theme
        theme = self.ui.get_theme_selection()
        self.player.theme = theme
        self.world.theme = theme
        
        # Generate dungeon
        self.world.generate_dungeon(theme)
        
        # Set player to start room
        self.player.location = "start"
        self.player.current_room_id = "start"
    
    def _process_command_result(self, result):
        """
        Process the result of a command execution
        """
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
            
            # Generate and display enhanced movement message
            movement_text = self._generate_movement_text(result['direction'])
            self.ui.display_message(movement_text)
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
            # Handle examining items with ASCII art
            examine_result = self._handle_examine_item(result["item"])
            self.ui.display_message(examine_result)
        elif result["type"] == "narrative":
            # Send narrative commands to LLM for immersive responses
            narrative_response = self._generate_narrative_response(result["command"])
            self.ui.display_message(narrative_response)
        elif result["type"] == "invalid":
            self.ui.display_error(result["message"])
    
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
        
        # Generate description with LLM
        if self.llm and hasattr(self.llm.llm, 'generate_item_description'):
            try:
                description = self.llm.llm.generate_item_description(item_found, self.player.theme)
                if description and "silent" not in description.lower():
                    return f"{ascii_art}\n\n{description}"
            except:
                pass
        
        # Fallback description
        return f"{ascii_art}\n\nYou examine the {item_found}. It looks like a typical {self.player.theme} {item_found}."
    
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