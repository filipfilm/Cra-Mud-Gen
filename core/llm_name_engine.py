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
        
        # Retry logic for better name generation
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Check if llm is the interface or the actual LLM
                if hasattr(self.llm, 'llm'):
                    response = self.llm.llm.generate_response(prompt)
                else:
                    response = self.llm.generate_response(prompt)
                name = self._parse_name_response(response, name_type)
                if name:  # Valid name generated
                    return name
                # If empty name, continue to next attempt
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    if self.fallback_mode:
                        return self._generate_fallback_name(theme, role, name_type)
                    else:
                        raise RuntimeError(f"LLM name generation failed and fallback mode disabled: {e}")
        
        # All attempts failed, use fallback
        if self.fallback_mode:
            return self._generate_fallback_name(theme, role, name_type)
        else:
            raise RuntimeError("LLM name generation failed after multiple attempts and fallback mode disabled")
    
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

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Check if llm is the interface or the actual LLM
                if hasattr(self.llm, 'llm'):
                    response = self.llm.llm.generate_response(prompt)
                else:
                    response = self.llm.generate_response(prompt)
                name = response.strip().strip('"').strip("'")
                if name:  # Valid name generated
                    return name
                # If empty name, continue to next attempt
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    if self.fallback_mode:
                        return self._generate_fallback_item(item_type, theme, rarity)
                    else:
                        raise RuntimeError(f"LLM item name generation failed and fallback mode disabled: {e}")
        
        # All attempts failed, use fallback
        if self.fallback_mode:
            return self._generate_fallback_item(item_type, theme, rarity)
        else:
            raise RuntimeError("LLM item name generation failed after multiple attempts and fallback mode disabled")
    
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
        
        # Add variety to prevent repetitive generation
        variety_prompts = [
            "Generate a unique and original",
            "Create a distinctive", 
            "Invent a memorable",
            "Design an evocative"
        ]
        
        variety_instructions = [
            "FORBIDDEN WORDS: Never use 'Whispering', 'Shadow', 'Dark', 'Abyss', 'Heart', 'Echo', 'Void'. Create something completely different.",
            "AVOID CLICHÉS: Do not use overused fantasy words like 'Iron', 'Dragon', 'Storm', 'Flame', 'Frost', 'Blood'. Be creative.", 
            "BE ORIGINAL: Invent new fantasy terminology instead of using common tropes. Think of unusual materials, colors, or phenomena.",
            "NO REPETITION: Create something that sounds completely different from typical dungeon names. Use unexpected combinations."
        ]
        
        prompt_start = random.choice(variety_prompts)
        variety_instruction = random.choice(variety_instructions)
        
        prompt = f"""{prompt_start} {location_type} name for a {theme} setting.

Requirements:
- Make it atmospheric and memorable
- Fit the {theme} theme perfectly
- Be 1-3 words typically
- Sound authentic and immersive
- {variety_instruction}

Examples for reference (avoid copying these exactly):
Fantasy: "Moonstone Citadel", "Goldleaf Sanctuary", "Sunrise Valley"
Sci-fi: "Nexus Station", "Quantum Labs", "Solar Outpost"  
Horror: "Blackwood Asylum", "Ravencroft Manor", "The Bone Chapel"
Cyberpunk: "Neon District", "Chrome Tower", "The Underground"

Generate just the location name, nothing else:"""

        try:
            # Check if llm is the interface or the actual LLM
            if hasattr(self.llm, 'llm'):
                response = self.llm.llm.generate_response(prompt)
            else:
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

Examples for reference (create something original, don't copy these):
Fantasy warrior: "Aldwin", "Brenna", "Corvin"  
Sci-fi engineer: "Zara", "Marcus", "Nova"
Horror investigator: "Vincent", "Elena", "Magnus"
Cyberpunk hacker: "Jax", "Kira", "Blade"

Generate just the name, nothing else:"""
            
        elif name_type == "full":
            # Add variety and forbidden terms for full names too
            full_name_variety = [
                "FORBIDDEN SURNAMES: Never use names ending in 'heart', 'wind', 'blade', 'shadow', 'storm'. Be completely original.",
                "AVOID CLICHÉS: Do not use overused fantasy surnames like 'Ironforge', 'Blackthorn', 'Goldleaf', 'Brightspear'.",
                "BE CREATIVE: Invent unique surname combinations that sound fresh and haven't been overused.",
                "NO REPETITION: Create something distinctive that doesn't sound like every other fantasy character."
            ]
            
            full_name_instruction = random.choice(full_name_variety)
            
            prompt = f"""Generate a full name with title for a {role} in a {theme} setting.

Requirements:
- Include appropriate title/rank for the role
- Make it pronounceable and memorable  
- Fit the {theme} genre perfectly
- Format: "Title FirstName LastName" or similar
- {full_name_instruction}

Examples for reference (avoid copying these patterns):
Fantasy: "Captain Lysander Goldmane", "Dame Vivienne Rosethorne", "Baron Felix Copperfield"
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
        # Safely get first non-empty line
        name = ""
        for line in lines:
            clean_line = line.strip()
            if clean_line:
                name = clean_line
                break
        
        # If no valid line found, return empty (will trigger retry)
        if not name:
            return ""
        
        # Remove common prefixes the LLM might add
        prefixes_to_remove = ["Name:", "Generated name:", "Character:", "Full name:"]
        for prefix in prefixes_to_remove:
            if name.startswith(prefix):
                name = name[len(prefix):].strip()
        
        return name
    
    def _generate_fallback_name(self, theme: str, role: str, name_type: str) -> str:
        """Fallback name generation disabled - LLM generation required"""
        raise RuntimeError("Fallback name generation disabled - LLM generation required")
    
    def _generate_fallback_item(self, item_type: str, theme: str, rarity: str) -> str:
        """Fallback item name generation disabled - LLM generation required"""
        raise RuntimeError("Fallback item name generation disabled - LLM generation required")
    
    def _generate_fallback_location(self, location_type: str, theme: str) -> str:
        """Fallback location name generation disabled - LLM generation required"""
        raise RuntimeError("Fallback location name generation disabled - LLM generation required")