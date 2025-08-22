"""
Room class to represent individual game locations
"""
from typing import List, Dict, Any

class Room:
    """
    Represents a single room or location in the game world
    """
    
    def __init__(self, room_id: str, description: str, items: List[str], npcs: List[str], connections: List[str]):
        self.room_id = room_id
        self.base_description = description  # Original description
        self.description = description       # Current description (can be enhanced)
        self.items = items
        self.npcs = npcs
        self.connections = connections
        self.visited = False
        self.enhanced_description = ""       # LLM-generated enhancement
        self.environmental_features = []     # Examinable features in the room
        # Extract features from base description immediately
        self._extract_environmental_features()
        
    def get_description(self) -> str:
        """
        Get the room description with any enhancements
        """
        if self.enhanced_description:
            return f"{self.base_description}\n\n{self.enhanced_description}"
        return self.base_description
    
    def set_enhanced_description(self, enhancement: str):
        """
        Set the LLM-generated enhancement (replaces any existing enhancement)
        """
        self.enhanced_description = enhancement
        # Extract environmental features from the enhancement
        self._extract_environmental_features()
    
    def _extract_environmental_features(self):
        """
        Extract examinable environmental features from room descriptions
        """
        full_description = self.get_description().lower()
        
        # Common environmental features to look for
        possible_features = [
            "carvings", "carving", "stones", "stone", "walls", "wall", "ceiling", 
            "floor", "shadows", "shadow", "doorway", "door", "entrance", "archway",
            "pillars", "pillar", "statues", "statue", "altar", "throne", "brazier",
            "torch", "torches", "crystals", "crystal", "murals", "mural", "paintings",
            "painting", "runes", "rune", "symbols", "symbol", "markings", "marking",
            "tapestries", "tapestry", "windows", "window", "stairs", "staircase",
            "fountain", "pool", "water", "fire", "flames", "candles", "candle"
        ]
        
        # Find features mentioned in the description
        self.environmental_features = []
        for feature in possible_features:
            if feature in full_description:
                if feature not in self.environmental_features:
                    self.environmental_features.append(feature)
    
    def get_environmental_features(self) -> List[str]:
        """
        Get list of examinable environmental features
        """
        return self.environmental_features
    
    def has_environmental_feature(self, feature_name: str) -> bool:
        """
        Check if a specific environmental feature exists
        """
        feature_name = feature_name.lower()
        return any(feature_name in feature.lower() or feature.lower() in feature_name for feature in self.environmental_features)
        
    def get_items(self) -> List[str]:
        """
        Get list of items in the room
        """
        return self.items
        
    def get_npcs(self) -> List[str]:
        """
        Get list of NPCs in the room
        """
        return self.npcs
        
    def get_exits(self) -> List[str]:
        """
        Get list of possible exits from this room
        """
        return self.connections
        
    def mark_visited(self):
        """
        Mark the room as visited
        """
        self.visited = True
        
    def is_visited(self) -> bool:
        """
        Check if the room has been visited
        """
        return self.visited
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert room to dictionary representation
        """
        return {
            "room_id": self.room_id,
            "description": self.description,
            "items": self.items,
            "npcs": self.npcs,
            "connections": self.connections,
            "visited": self.visited
        }