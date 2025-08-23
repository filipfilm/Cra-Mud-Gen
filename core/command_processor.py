"""
Command processor to parse and execute player commands
"""
from typing import Dict, Any, Tuple
import re

class CommandProcessor:
    """
    Parses and executes player commands in Dun-Gen
    """
    
    def __init__(self):
        # Define supported commands and their patterns
        self.commands = {
            "go": r"^(go|move)\s+(north|south|east|west|up|down|n|s|e|w|u|d)\s*$",
            "look": r"^(look|l)\s*$",
            "inventory": r"^(inventory|i)\s*$",
            "quit": r"^(quit|exit|q)\s*$",
            "help": r"^(help|h)\s*$",
            "take": r"^(take|get|pickup)\s+(.+)\s*$",
            "drop": r"^(drop|put down|leave)\s+(.+)\s*$",
            "use": r"^(use)\s+(.+)\s*$",
            "examine": r"^(examine|inspect|check)\s+(.+)\s*$",
            "attack": r"^(attack|fight|kill)\s+(.+)\s*$",
            "defend": r"^(defend|guard|block)\s*$", 
            "flee": r"^(flee|run|escape)\s*$",
            "heal": r"^(heal|use potion|drink potion)\s*$",
            "map": r"^(map|show map|read map|view map|m)\s*$",
            "stats": r"^(stats|status|exploration)\s*$"
        }
        
    def parse(self, user_input: str, player, world) -> Dict[str, Any]:
        """
        Parse a user command and return appropriate result
        """
        user_input = user_input.strip().lower()
        
        # Handle empty input
        if not user_input:
            return {"type": "invalid", "message": "Please enter a command."}
            
        # Check for each command type
        if re.match(self.commands["quit"], user_input):
            return {"type": "exit"}
            
        elif re.match(self.commands["help"], user_input):
            return {"type": "help", "message": self._get_help_text()}
            
        elif re.match(self.commands["look"], user_input):
            return {"type": "look", "message": "You look around."}
            
        elif re.match(self.commands["inventory"], user_input):
            return {"type": "inventory", "items": player.inventory}
            
        elif re.match(self.commands["go"], user_input):
            direction = re.match(self.commands["go"], user_input).group(2)
            return self._handle_movement(direction, player, world)
            
        elif re.match(self.commands["take"], user_input):
            item = re.match(self.commands["take"], user_input).group(2)
            return {"type": "take", "item": item}
            
        elif re.match(self.commands["drop"], user_input):
            item = re.match(self.commands["drop"], user_input).group(2)
            return {"type": "drop", "item": item}
            
        elif re.match(self.commands["use"], user_input):
            item = re.match(self.commands["use"], user_input).group(2)
            return {"type": "use", "item": item}
            
        elif re.match(self.commands["examine"], user_input):
            item = re.match(self.commands["examine"], user_input).group(2)
            return {"type": "examine", "item": item}
            
        elif re.match(self.commands["map"], user_input):
            return {"type": "map", "message": "Showing map"}
            
        elif re.match(self.commands["attack"], user_input):
            target = re.match(self.commands["attack"], user_input).group(2)
            return {"type": "combat_action", "action": "attack", "target": target}
            
        elif re.match(self.commands["defend"], user_input):
            return {"type": "combat_action", "action": "defend"}
            
        elif re.match(self.commands["flee"], user_input):
            return {"type": "combat_action", "action": "flee"}
            
        elif re.match(self.commands["heal"], user_input):
            return {"type": "combat_action", "action": "heal"}
            
        elif re.match(self.commands["stats"], user_input):
            return {"type": "stats", "message": "Showing exploration stats"}
            
        else:
            # Send unknown commands to LLM for narrative responses
            return {"type": "narrative", "command": user_input, "message": f"Processing: '{user_input}'"}
    
    def _handle_movement(self, direction: str, player, world) -> Dict[str, Any]:
        """
        Handle movement commands with dynamic room generation
        """
        # Normalize direction
        direction_map = {
            "north": "north", "south": "south", "east": "east", "west": "west",
            "up": "up", "down": "down", 
            "n": "north", "s": "south", "e": "east", "w": "west", "u": "up", "d": "down"
        }
        
        if direction not in direction_map:
            return {
                "type": "invalid", 
                "message": f"You can't go {direction} from here."
            }
        
        full_direction = direction_map[direction]
        current_room = world.get_room(player.location)
        
        if not current_room:
            return {
                "type": "invalid", 
                "message": "You seem to be nowhere. This is a problem."
            }
        
        # Check if this direction is available from current room
        possible_destinations = []
        for connection in current_room.connections:
            if connection.startswith(full_direction):
                possible_destinations.append(connection)
        
        if not possible_destinations:
            return {
                "type": "invalid", 
                "message": f"You can't go {full_direction} from here. There's no passage in that direction."
            }
        
        # For now, take the first valid destination
        # In future, could handle multiple paths in same direction
        new_location = possible_destinations[0]
        
        # Generate room on demand if it doesn't exist
        if new_location not in world.rooms:
            world.generate_room_on_demand(new_location, player.location, full_direction)
        
        return {
            "type": "movement", 
            "new_location": new_location,
            "direction": full_direction
        }
            
    def _get_help_text(self) -> str:
        """
        Get help text with available commands
        """
        return """
Available commands:
  go <direction>     - Move in a direction (north, south, east, west, up, down)
  look/l           - Look around the current room
  inventory/i      - Show your inventory
  take/get <item>  - Take an item from the room
  drop <item>      - Drop an item from your inventory
  use <item>       - Use an item from your inventory
  examine <item>   - Examine an item (with ASCII art!)
  map/m            - Show the dungeon map
  stats            - Show exploration statistics
  
Combat commands:
  attack <enemy>   - Attack an enemy in combat
  defend/guard     - Take defensive stance (reduces damage)
  flee/run         - Attempt to flee from combat
  heal             - Use a healing potion if you have one
  
Conversation commands:
  talk to <npc>    - Start a conversation with an NPC
  hello <npc>      - Greet an NPC
  goodbye          - End current conversation
  
  help/h           - Show this help text
  quit/q           - Exit the game
  
  You can also try narrative commands like: read scroll, examine walls, etc.
        """