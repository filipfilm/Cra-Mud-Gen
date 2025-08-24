"""
LLM-Powered Name Generation Engine for Cra-mud-gen
Uses AI to generate high-quality, pronounceable, thematic names
"""
import random
from typing import Dict, List, Optional


class LLMNameEngine:
    """Generates high-quality names using LLM instead of syllable rules"""
    
    def __init__(self, llm=None, fallback_mode=False):
        """
        Initialize LLM name engine
        
        Args:
            llm: LLM interface for name generation
            fallback_mode: Whether to allow fallback to rule-based names
        """
        self.llm = llm
        self.fallback_mode = fallback_mode
    
    def generate_dynamic_name(self, theme: str, role: str, name_type: str = "full") -> str:
        """
        Generate a dynamic name using LLM
        
        Args:
            theme: Theme context (fantasy, sci-fi, horror, cyberpunk)
            role: Character role (warrior, mage, guard, etc.)
            name_type: Type of name ("first", "full", "title")
            
        Returns:
            Generated name string
        """
        if not self.llm:
            if self.fallback_mode:
                return self._generate_fallback_name(theme, role, name_type)
            else:
                raise RuntimeError("LLM is required for name generation (fallback mode disabled)")
        
        prompt = self._create_name_prompt(theme, role, name_type)
        
        try:
            response = self.llm.generate_response(prompt)
            name = self._parse_name_response(response, name_type)
            return name
            
        except Exception as e:
            if self.fallback_mode:
                return self._generate_fallback_name(theme, role, name_type)
            else:
                raise RuntimeError(f"LLM name generation failed and fallback mode disabled: {e}")
    
    def generate_item_name(self, item_type: str, theme: str, rarity: str = "common") -> str:
        """
        Generate an item name using LLM
        
        Args:
            item_type: Type of item (weapon, armor, potion, scroll)
            theme: Theme context
            rarity: Rarity level (common, uncommon, rare, legendary)
            
        Returns:
            Generated item name
        """
        if not self.llm:
            if self.fallback_mode:
                return self._generate_fallback_item(item_type, theme, rarity)
            else:
                raise RuntimeError("LLM is required for item name generation (fallback mode disabled)")
        
        prompt = f"""Generate a {rarity} {item_type} name for a {theme} setting.

Requirements:
- Make it memorable and pronounceable
- Fit the {theme} theme perfectly
- Reflect {rarity} rarity level
- Be 1-4 words maximum
- Sound authentic to the genre

Examples for reference:
Fantasy weapon: "Shadowbane Blade", "Ember Strike"
Sci-fi armor: "Plasma Shield", "Neural Mesh"
Horror potion: "Crimson Elixir", "Soul Draught"
Cyberpunk scroll: "Code Fragment", "Data Shard"

Generate just the name, nothing else:"""

        try:
            response = self.llm.generate_response(prompt)
            return response.strip().strip('"').strip("'")
            
        except Exception as e:
            if self.fallback_mode:
                return self._generate_fallback_item(item_type, theme, rarity)
            else:
                raise RuntimeError(f"LLM item name generation failed and fallback mode disabled: {e}")
    
    def generate_location_name(self, location_type: str, theme: str) -> str:
        """
        Generate a location name using LLM
        
        Args:
            location_type: Type of location (dungeon, chamber, forest, etc.)
            theme: Theme context
            
        Returns:
            Generated location name
        """
        if not self.llm:
            if self.fallback_mode:
                return self._generate_fallback_location(location_type, theme)
            else:
                raise RuntimeError("LLM is required for location name generation (fallback mode disabled)")
        
        prompt = f"""Generate a {location_type} name for a {theme} setting.

Requirements:
- Make it atmospheric and memorable
- Fit the {theme} theme perfectly
- Be 1-3 words typically
- Sound authentic and immersive

Examples for reference:
Fantasy: "Shadowmere Keep", "Whispering Caverns", "Thornwood Sanctum"
Sci-fi: "Nexus Station", "Quantum Labs", "Solar Outpost"
Horror: "Blackwood Asylum", "Ravencroft Manor", "The Bone Chapel"
Cyberpunk: "Neon District", "Chrome Tower", "The Underground"

Generate just the location name, nothing else:"""

        try:
            response = self.llm.generate_response(prompt)
            return response.strip().strip('"').strip("'")
            
        except Exception as e:
            if self.fallback_mode:
                return self._generate_fallback_location(location_type, theme)
            else:
                raise RuntimeError(f"LLM location name generation failed and fallback mode disabled: {e}")
    
    def _create_name_prompt(self, theme: str, role: str, name_type: str) -> str:
        """Create LLM prompt for character name generation"""
        
        if name_type == "first":
            prompt = f"""Generate a first name for a {role} in a {theme} setting.

Requirements:
- Make it pronounceable and memorable
- Fit the {theme} genre perfectly
- Be appropriate for the {role} character type
- 1-2 words maximum

Examples for reference:
Fantasy warrior: "Thorin", "Elara", "Gareth"
Sci-fi engineer: "Zara", "Marcus", "Nova"
Horror investigator: "Vincent", "Elena", "Magnus"
Cyberpunk hacker: "Jax", "Kira", "Blade"

Generate just the name, nothing else:"""
            
        elif name_type == "full":
            prompt = f"""Generate a full name with title for a {role} in a {theme} setting.

Requirements:
- Include appropriate title/rank for the role
- Make it pronounceable and memorable  
- Fit the {theme} genre perfectly
- Format: "Title FirstName LastName" or similar

Examples for reference:
Fantasy: "Sir Aldric Stormwind", "Lady Mira Shadowleaf", "Captain Theron Brightblade"
Sci-fi: "Commander Sarah Chen", "Engineer Kai Nakamura", "Pilot Rex Vortex"  
Horror: "Dr. Vincent Cross", "Detective Sarah Mills", "Father Marcus Kane"
Cyberpunk: "Runner Echo", "Ghost Protocol", "Agent Nova"

Generate just the full name with title, nothing else:"""
            
        else:  # title only
            prompt = f"""Generate just a title/rank for a {role} in a {theme} setting.

Requirements:
- Appropriate for the role and theme
- Single word or short phrase
- Authentic to the genre

Examples:
Fantasy: "Sir", "Lady", "Captain", "Elder"
Sci-fi: "Commander", "Engineer", "Pilot", "Doctor"
Horror: "Detective", "Professor", "Father", "Doctor"  
Cyberpunk: "Runner", "Ghost", "Agent", "Operator"

Generate just the title, nothing else:"""
        
        return prompt
    
    def _parse_name_response(self, response: str, name_type: str) -> str:
        """Parse and clean LLM name response"""
        # Clean the response
        name = response.strip().strip('"').strip("'")
        
        # Remove any extra text that might have been added
        lines = name.split('\n')
        name = lines[0].strip()
        
        # Remove common prefixes the LLM might add
        prefixes_to_remove = ["Name:", "Generated name:", "Character:", "Full name:"]
        for prefix in prefixes_to_remove:
            if name.startswith(prefix):
                name = name[len(prefix):].strip()
        
        return name
    
    def _generate_fallback_name(self, theme: str, role: str, name_type: str) -> str:
        """Fallback to simple name generation when LLM unavailable"""
        # Import the old system for fallback
        from core.generative_name_engine import GenerativeNameEngine
        fallback_engine = GenerativeNameEngine()
        return fallback_engine.generate_dynamic_name(theme, role, name_type)
    
    def _generate_fallback_item(self, item_type: str, theme: str, rarity: str) -> str:
        """Fallback item name generation"""
        from core.generative_name_engine import GenerativeNameEngine
        fallback_engine = GenerativeNameEngine()
        return fallback_engine.generate_item_name(item_type, theme, rarity)
    
    def _generate_fallback_location(self, location_type: str, theme: str) -> str:
        """Fallback location name generation"""
        from core.generative_name_engine import GenerativeNameEngine
        fallback_engine = GenerativeNameEngine()
        return fallback_engine.generate_location_name(location_type, theme)