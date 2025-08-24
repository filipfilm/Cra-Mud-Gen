"""
Player class to manage player state and information
"""
from typing import List, Dict, Any
from .combat_system import Combatant, HealthSystem, ExperienceSystem

class Player(Combatant):
    """
    Represents the player in Cra-mud-gen - now with combat capabilities
    """
    
    def __init__(self):
        # Initialize game-specific attributes first
        self.stats: Dict[str, Any] = {
            "level": 1,
            "experience": 0,
            "gold": 0
        }
        
        # Initialize combat stats 
        super().__init__("Player", 100, 1)
        
        # More game-specific attributes
        self.location = "start_room"
        self.current_room_id = "start_room"
        self.inventory: List[str] = []
        self.theme = "fantasy"  # Default theme
        
        # Combat progression
        self.combat_stats = {
            "enemies_defeated": 0,
            "total_damage_dealt": 0,
            "total_damage_taken": 0,
            "critical_hits": 0,
            "battles_won": 0,
            "battles_fled": 0
        }
        
        # Exploration tracking
        self.visited_rooms = set()
        self.rooms_discovered = 0
        self.exploration_points = 0
        self.visited_rooms.add("start_room")  # Mark starting room as visited
    
    @property
    def health(self) -> int:
        """Get current health for compatibility"""
        return self.current_health
    
    @health.setter
    def health(self, value: int):
        """Set current health for compatibility"""
        self.current_health = max(0, min(value, self.max_health))
    
    @property
    def level(self) -> int:
        """Get player level"""
        return self.stats.get("level", 1)
    
    @level.setter
    def level(self, value: int):
        """Set player level"""
        self.stats["level"] = value
    
    @property  
    def gold(self) -> int:
        """Get player gold"""
        return self.stats.get("gold", 0)
    
    @property
    def experience(self) -> int:
        """Get player experience"""
        return self.stats.get("experience", 0)
    
    def level_up_if_ready(self) -> Dict[str, Any]:
        """Check if player should level up and handle it"""
        current_level = self.stats["level"]
        new_level = ExperienceSystem.calculate_level_from_exp(self.stats["experience"])
        
        if new_level > current_level:
            # Level up!
            self.stats["level"] = new_level
            
            # Update combat stats based on new level
            old_max_health = self.max_health
            self.max_health = HealthSystem.calculate_max_health(new_level)
            health_gained = self.max_health - old_max_health
            
            # Heal on level up
            self.current_health = min(self.current_health + health_gained, self.max_health)
            
            # Increase combat stats
            self.attack = 10 + (new_level * 2)
            self.defense = 5 + new_level
            
            return {
                "leveled_up": True,
                "old_level": current_level,
                "new_level": new_level,
                "health_gained": health_gained,
                "new_max_health": self.max_health
            }
        
        return {"leveled_up": False}
    
    def get_health_percentage(self) -> float:
        """Get health as percentage for UI display"""
        return (self.current_health / self.max_health) * 100
    
    def get_exp_progress(self) -> Dict[str, int]:
        """Get experience progress information"""
        current_exp = self.stats["experience"]
        current_level = self.stats["level"]
        
        progress, needed = ExperienceSystem.exp_progress_to_next_level(current_exp, current_level)
        return {
            "current_exp": current_exp,
            "progress": progress,
            "needed": needed,
            "percentage": int((progress / needed) * 100) if needed > 0 else 100
        }
        
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