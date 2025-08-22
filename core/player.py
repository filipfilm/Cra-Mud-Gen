"""
Player class to manage player state and information
"""
from typing import List, Dict, Any

class Player:
    """
    Represents the player in the MUD game
    """
    
    def __init__(self):
        self.location = "start_room"
        self.current_room_id = "start_room"
        self.health = 100
        self.inventory: List[str] = []
        self.theme = "fantasy"  # Default theme
        self.stats: Dict[str, Any] = {
            "level": 1,
            "experience": 0,
            "gold": 0
        }
        
        # Exploration tracking
        self.visited_rooms = set()
        self.rooms_discovered = 0
        self.exploration_points = 0
        self.visited_rooms.add("start_room")  # Mark starting room as visited
        
    def add_to_inventory(self, item: str) -> bool:
        """
        Add an item to the player's inventory
        Returns True if successful, False if inventory is full
        """
        if len(self.inventory) >= 20:  # Max inventory size
            return False
        self.inventory.append(item)
        return True
        
    def remove_from_inventory(self, item: str) -> bool:
        """
        Remove an item from the player's inventory
        Returns True if item was found and removed
        """
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
            
    def has_item(self, item: str) -> bool:
        """
        Check if player has an item (case-insensitive, partial match)
        """
        item = item.lower()
        return any(item in inv_item.lower() or inv_item.lower() in item for inv_item in self.inventory)
    
    def find_item(self, item_name: str) -> str:
        """
        Find an item in inventory by partial name match (case-insensitive)
        Returns the full item name if found, None otherwise
        """
        item_name = item_name.lower()
        for item in self.inventory:
            if item_name in item.lower() or item.lower() in item_name:
                return item
        return None
        
    def get_status(self) -> str:
        """
        Get a string representation of player status
        """
        inventory_count = len(self.inventory)
        return f"Health: {self.health}, Level: {self.stats['level']}, Gold: {self.stats['gold']}, Items: {inventory_count}/20"
    
    def get_inventory_description(self) -> str:
        """
        Get a formatted description of inventory contents
        """
        if not self.inventory:
            return "Your inventory is empty."
        
        return f"You are carrying: {', '.join(self.inventory)}"
    
    def move_to_location(self, new_location: str):
        """
        Move the player to a new location and track exploration
        """
        # Track exploration
        if new_location not in self.visited_rooms:
            self.visited_rooms.add(new_location)
            self.rooms_discovered += 1
            self.exploration_points += 10  # Reward for exploring new areas
        
        self.location = new_location
        self.current_room_id = new_location
    
    def get_exploration_stats(self) -> Dict[str, Any]:
        """
        Get exploration statistics
        """
        return {
            "rooms_visited": len(self.visited_rooms),
            "exploration_points": self.exploration_points,
            "current_location": self.location,
            "visited_rooms": list(self.visited_rooms)
        }