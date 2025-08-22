"""
Theme management system for the MUD game
"""
from typing import Dict, List

class ThemeManager:
    """
    Manages game themes and theme-appropriate content generation
    """
    
    def __init__(self):
        # Define themes and their characteristics
        self.themes = {
            "fantasy": {
                "name": "Fantasy",
                "description": "A mystical world of magic, dragons, and ancient artifacts",
                "adjectives": ["mystical", "ancient", "enchanted", "magical"],
                "nouns": ["castle", "forest", "dragon", "wizard", "elf", "sword", "potion"],
                "verbs": ["wanders", "casts", "summons", "fights", "heals"],
                "items": ["magic staff", "potion of healing", "ancient scroll", "sword of light"],
                "npcs": ["wizard", "elf", "dragon", "orc", "goblin", "knight"],
                "rooms": ["chamber", "hallway", "cavern", "temple", "tower"]
            },
            "sci-fi": {
                "name": "Sci-Fi",
                "description": "A futuristic world of technology, space, and advanced AI",
                "adjectives": ["futuristic", "cybernetic", "holographic", "mechanical"],
                "nouns": ["spaceship", "robot", "laser", "hologram", "neural interface"],
                "verbs": ["scans", "analyzes", "hacks", "launches", "connects"],
                "items": ["laser pistol", "energy cell", "holographic display", "data chip"],
                "npcs": ["alien", "robot", "space explorer", "hacker", "engineer"],
                "rooms": ["bridge", "corridor", "lab", "cockpit", "control room"]
            },
            "horror": {
                "name": "Horror",
                "description": "A dark and terrifying world of monsters and supernatural threats",
                "adjectives": ["dark", "ominous", "creepy", "haunted"],
                "nouns": ["shadows", "ghost", "monster", "cursed object", "blood"],
                "verbs": ["whispers", "creeps", "screams", "hides", "attacks"],
                "items": ["flashlight", "broken mirror", "blood-stained knife", "cursed artifact"],
                "npcs": ["ghost", "monster", "cursed entity", "zombie", "vampire"],
                "rooms": ["basement", "attic", "cellar", "crypt", "haunted room"]
            },
            "cyberpunk": {
                "name": "Cyberpunk",
                "description": "A neon-lit dystopian future with advanced technology and corporate power",
                "adjectives": ["neon", "synthetic", "digital", "cybernetic"],
                "nouns": ["neon sign", "synth", "cybernetic arm", "data chip", "hologram"],
                "verbs": ["hacks", "blinks", "connects", "scans", "upgrades"],
                "items": ["cybernetic arm", "neural interface", "data chip", "holographic display"],
                "npcs": ["hacker", "synth", "corporate agent", "street samurai", "ai"],
                "rooms": ["neon-lit street", "cybernetics lab", "data center", "underground bar"]
            }
        }
    
    def get_theme_names(self) -> List[str]:
        """
        Get list of available theme names
        """
        return list(self.themes.keys())
    
    def get_theme_info(self, theme_name: str) -> Dict:
        """
        Get complete information about a specific theme
        """
        return self.themes.get(theme_name.lower(), self.themes["fantasy"])
    
    def get_theme_adjectives(self, theme_name: str) -> List[str]:
        """
        Get adjectives appropriate for a theme
        """
        theme = self.get_theme_info(theme_name)
        return theme.get("adjectives", ["mysterious"])
    
    def get_theme_nouns(self, theme_name: str) -> List[str]:
        """
        Get nouns appropriate for a theme
        """
        theme = self.get_theme_info(theme_name)
        return theme.get("nouns", ["object"])
    
    def get_theme_items(self, theme_name: str) -> List[str]:
        """
        Get items appropriate for a theme
        """
        theme = self.get_theme_info(theme_name)
        return theme.get("items", ["item"])
    
    def get_theme_npcs(self, theme_name: str) -> List[str]:
        """
        Get NPCs appropriate for a theme
        """
        theme = self.get_theme_info(theme_name)
        return theme.get("npcs", ["creature"])
    
    def get_theme_room_types(self, theme_name: str) -> List[str]:
        """
        Get room types appropriate for a theme
        """
        theme = self.get_theme_info(theme_name)
        return theme.get("rooms", ["room"])
    
    def get_theme_description(self, theme_name: str) -> str:
        """
        Get the description of a theme
        """
        theme = self.get_theme_info(theme_name)
        return theme.get("description", "A mysterious world")
    
    def get_theme_name(self, theme_name: str) -> str:
        """
        Get the human-readable name of a theme
        """
        theme = self.get_theme_info(theme_name)
        return theme.get("name", "Unknown")