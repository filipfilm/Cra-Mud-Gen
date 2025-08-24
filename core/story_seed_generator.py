"""
Story Seed Generation System for Cra-mud-gen
Handles seed creation through sliders, text, or randomization with LLM self-iteration
"""
import json
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class StorySeed:
    """Represents a complete story seed for dungeon generation"""
    
    # Basic narrative elements
    theme: str = ""
    setting: str = ""
    conflict: str = ""
    mood: str = ""
    
    # Character and NPC elements
    main_characters: List[str] = None
    antagonist: str = ""
    supporting_npcs: List[str] = None
    
    # Story structure
    story_beats: List[str] = None
    plot_hooks: List[str] = None
    custom_elements: List[str] = None
    
    # Slider values (1-10 scale)
    danger_level: int = 5
    discovery_factor: int = 5
    scary_factor: int = 5
    mystery_level: int = 5
    comedy_level: int = 1
    
    # Generation metadata
    generation_method: str = ""  # 'sliders', 'text_only', 'random', 'custom'
    custom_text: str = ""
    iteration_count: int = 0
    created_at: str = ""
    
    def __post_init__(self):
        # Initialize empty lists if None
        if self.main_characters is None:
            self.main_characters = []
        if self.supporting_npcs is None:
            self.supporting_npcs = []
        if self.story_beats is None:
            self.story_beats = []
        if self.plot_hooks is None:
            self.plot_hooks = []
        if self.custom_elements is None:
            self.custom_elements = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StorySeed':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class NarrativeState:
    """Tracks the current state of story progression during gameplay"""
    
    seed: StorySeed
    current_beat: int = 0
    completed_beats: List[str] = None
    active_npcs: List[str] = None
    story_flags: Dict[str, bool] = None
    player_choices: Dict[str, List] = None
    narrative_tension: float = 0.5  # 0.0 to 1.0
    
    def __post_init__(self):
        if self.completed_beats is None:
            self.completed_beats = []
        if self.active_npcs is None:
            self.active_npcs = []
        if self.story_flags is None:
            self.story_flags = {}
        if self.player_choices is None:
            self.player_choices = {}
    
    def advance_beat(self):
        """Move to the next story beat"""
        if self.current_beat < len(self.seed.story_beats) - 1:
            self.completed_beats.append(self.seed.story_beats[self.current_beat])
            self.current_beat += 1
            return True
        return False
    
    def add_story_flag(self, flag_name: str, value: bool = True):
        """Set a story flag for tracking plot progression"""
        self.story_flags[flag_name] = value
    
    def get_current_beat(self) -> Optional[str]:
        """Get the current story beat"""
        if self.current_beat < len(self.seed.story_beats):
            return self.seed.story_beats[self.current_beat]
        return None


class StorySeedGenerator:
    """Main class for generating story seeds with LLM iteration"""
    
    def __init__(self, llm_interface=None):
        """
        Initialize the story seed generator
        
        Args:
            llm_interface: Optional LLM interface for seed iteration
        """
        self.llm_interface = llm_interface
        self.max_iterations = 3
        
        # Predefined theme templates for random generation
        self.theme_templates = {
            'fantasy': {
                'settings': ['ancient castle', 'mystical forest', 'dragon\'s lair', 'wizard tower', 'underground caverns'],
                'conflicts': ['evil sorcerer threat', 'ancient curse awakening', 'kingdom under siege', 'magical artifact hunt'],
                'characters': ['brave knight', 'wise wizard', 'cunning rogue', 'noble paladin', 'mysterious ranger']
            },
            'sci-fi': {
                'settings': ['space station', 'alien planet', 'generation ship', 'research facility', 'orbital colony'],
                'conflicts': ['alien invasion', 'system malfunction', 'corporate conspiracy', 'AI rebellion'],
                'characters': ['space marine', 'scientist', 'engineer', 'pilot', 'android']
            },
            'horror': {
                'settings': ['abandoned mansion', 'creepy hospital', 'isolated cabin', 'dark forest', 'haunted asylum'],
                'conflicts': ['supernatural presence', 'serial killer stalking', 'ancient evil awakening', 'psychological terror'],
                'characters': ['investigator', 'survivor', 'local guide', 'skeptic', 'medium']
            },
            'cyberpunk': {
                'settings': ['megacity streets', 'corporate tower', 'underground network', 'virtual reality', 'black market'],
                'conflicts': ['corporate espionage', 'data theft mission', 'resistance movement', 'identity crisis'],
                'characters': ['hacker', 'street samurai', 'corporate agent', 'netrunner', 'fixer']
            }
        }
    
    def generate_from_sliders(self, slider_values: Dict[str, int], custom_text: str = "") -> StorySeed:
        """
        Generate a story seed from slider values and optional custom text
        
        Args:
            slider_values: Dictionary with danger, discovery, scary, mystery, comedy levels (1-10)
            custom_text: Optional custom text to incorporate
            
        Returns:
            StorySeed object
        """
        seed = StorySeed(
            danger_level=slider_values.get('danger', 5),
            discovery_factor=slider_values.get('discovery', 5),
            scary_factor=slider_values.get('scary', 5),
            mystery_level=slider_values.get('mystery', 5),
            comedy_level=slider_values.get('comedy', 1),
            custom_text=custom_text,
            generation_method='sliders'
        )
        
        # Determine theme based on highest slider values
        theme_scores = {
            'horror': slider_values.get('scary', 0),
            'mystery': slider_values.get('mystery', 0),
            'action': slider_values.get('danger', 0),
            'exploration': slider_values.get('discovery', 0),
            'comedy': slider_values.get('comedy', 0)
        }
        
        primary_theme = max(theme_scores, key=theme_scores.get)
        seed.theme = primary_theme
        
        # Generate basic elements based on sliders
        seed = self._populate_seed_from_theme(seed, primary_theme)
        
        # If LLM is available, iterate to improve the seed
        if self.llm_interface:
            seed = self._iterate_seed_with_llm(seed)
        
        return seed
    
    def generate_from_text(self, custom_text: str) -> StorySeed:
        """
        Generate a story seed purely from custom text input
        
        Args:
            custom_text: The user's story description
            
        Returns:
            StorySeed object
        """
        seed = StorySeed(
            custom_text=custom_text,
            generation_method='text_only'
        )
        
        # Extract theme hints from text
        theme_keywords = {
            'fantasy': ['magic', 'wizard', 'dragon', 'castle', 'knight', 'sword'],
            'sci-fi': ['space', 'alien', 'robot', 'future', 'technology', 'ship'],
            'horror': ['scary', 'ghost', 'haunted', 'terror', 'fear', 'dark'],
            'cyberpunk': ['cyber', 'hacker', 'corporate', 'neon', 'virtual']
        }
        
        detected_theme = 'fantasy'  # Default
        max_matches = 0
        
        text_lower = custom_text.lower()
        for theme, keywords in theme_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > max_matches:
                max_matches = matches
                detected_theme = theme
        
        seed.theme = detected_theme
        
        # If LLM is available, use it to create full seed from text
        if self.llm_interface:
            seed = self._iterate_seed_with_llm(seed)
        else:
            # Fallback: populate with template data
            seed = self._populate_seed_from_theme(seed, detected_theme)
        
        return seed
    
    def generate_random(self, theme_preference: Optional[str] = None) -> StorySeed:
        """
        Generate a completely random story seed
        
        Args:
            theme_preference: Optional theme to prefer, otherwise random
            
        Returns:
            StorySeed object
        """
        theme = theme_preference or random.choice(list(self.theme_templates.keys()))
        
        # Random slider values
        seed = StorySeed(
            danger_level=random.randint(3, 9),
            discovery_factor=random.randint(3, 9),
            scary_factor=random.randint(1, 8),
            mystery_level=random.randint(2, 8),
            comedy_level=random.randint(1, 4),
            theme=theme,
            generation_method='random'
        )
        
        # Populate with theme-based content
        seed = self._populate_seed_from_theme(seed, theme)
        
        # Add some randomization
        seed.custom_text = f"Random {theme} adventure with dynamic elements"
        
        # If LLM is available, iterate to improve
        if self.llm_interface:
            seed = self._iterate_seed_with_llm(seed)
        
        return seed
    
    def _populate_seed_from_theme(self, seed: StorySeed, theme: str) -> StorySeed:
        """
        Populate a seed with theme-based template data
        
        Args:
            seed: The StorySeed to populate
            theme: The theme to use
            
        Returns:
            Updated StorySeed
        """
        if theme not in self.theme_templates:
            theme = 'fantasy'  # Fallback
        
        template = self.theme_templates[theme]
        
        seed.setting = random.choice(template['settings'])
        seed.conflict = random.choice(template['conflicts'])
        seed.main_characters = [random.choice(template['characters'])]
        
        # Generate basic story beats
        seed.story_beats = [
            f"Introduction to {seed.setting}",
            f"Discovery of {seed.conflict}",
            "First challenge or obstacle",
            "Character development or revelation",
            "Climax and resolution"
        ]
        
        # Generate plot hooks
        seed.plot_hooks = [
            f"Strange activity in {seed.setting}",
            f"Rumors about {seed.conflict}",
            "A mysterious message or clue"
        ]
        
        return seed
    
    def _iterate_seed_with_llm(self, seed: StorySeed) -> StorySeed:
        """
        Use LLM to iterate and improve the story seed (1-3 iterations)
        
        Args:
            seed: The initial seed
            
        Returns:
            Improved StorySeed
        """
        if not self.llm_interface:
            return seed
        
        current_seed = seed
        
        for iteration in range(self.max_iterations):
            try:
                # Create prompt for LLM iteration
                prompt = self._create_iteration_prompt(current_seed, iteration)
                
                # Get LLM response
                response = self.llm_interface.generate_text(prompt, max_tokens=800)
                
                # Parse response and update seed
                current_seed = self._parse_llm_response(current_seed, response, iteration)
                current_seed.iteration_count = iteration + 1
                
                # Add some variety - don't always do all 3 iterations
                if iteration > 0 and random.random() < 0.3:
                    break
                    
            except Exception as e:
                print(f"LLM iteration {iteration + 1} failed: {e}")
                break
        
        return current_seed
    
    def _create_iteration_prompt(self, seed: StorySeed, iteration: int) -> str:
        """
        Create appropriate prompt for each iteration level
        
        Args:
            seed: Current seed state
            iteration: Which iteration (0, 1, or 2)
            
        Returns:
            Prompt string for LLM
        """
        base_info = f"""
Theme: {seed.theme}
Setting: {seed.setting}
Custom text: {seed.custom_text}
Danger level: {seed.danger_level}/10
Mystery level: {seed.mystery_level}/10
Scary factor: {seed.scary_factor}/10
"""
        
        if iteration == 0:
            # Basic story from input
            return f"""Create a compelling story concept based on these elements:
{base_info}

Generate a brief story concept that incorporates these elements. Focus on:
- A clear setting and atmosphere
- The main conflict or challenge
- 1-2 key characters
- The overall mood and tone

Keep it concise but engaging (2-3 sentences).
"""
        
        elif iteration == 1:
            # Add complexity and stakes
            return f"""Enhance this story concept with more complexity:

Current story: {seed.conflict} in {seed.setting}
{base_info}

Add depth by including:
- Higher stakes or consequences
- Character motivations and backgrounds  
- Secondary conflicts or complications
- Specific details that make it unique

Expand to 4-5 sentences with richer detail.
"""
        
        else:  # iteration == 2
            # Add specific details and hooks
            return f"""Create the final, detailed story concept:

Current story elements:
Setting: {seed.setting}
Conflict: {seed.conflict}
Characters: {', '.join(seed.main_characters) if seed.main_characters else 'TBD'}
{base_info}

Create a rich, specific story concept that includes:
- Named characters with clear roles
- Specific organizations, locations, or entities
- Concrete story hooks and mysteries
- Clear progression path for the adventure

Make it detailed and immersive (6-8 sentences).
"""
    
    def _parse_llm_response(self, seed: StorySeed, response: str, iteration: int) -> StorySeed:
        """
        Parse LLM response and update seed accordingly
        
        Args:
            seed: Current seed to update
            response: LLM response text
            iteration: Current iteration number
            
        Returns:
            Updated StorySeed
        """
        # Clean up the response
        response = response.strip()
        
        # Update basic elements based on iteration
        if iteration == 0:
            # Basic story extraction
            seed.mood = response
            # Try to extract key elements
            if "character" in response.lower():
                # Simple character extraction
                words = response.split()
                potential_chars = [w.capitalize() for w in words if len(w) > 3 and w.isalpha()]
                if potential_chars:
                    seed.main_characters = potential_chars[:2]
        
        elif iteration == 1:
            # Enhanced story with complexity
            seed.conflict = response
            # Extract potential story beats
            sentences = response.split('. ')
            if len(sentences) >= 3:
                seed.story_beats = sentences[:5]
        
        else:  # iteration == 2
            # Final detailed story
            seed.conflict = response
            # Extract detailed elements
            seed.plot_hooks = [response]  # The whole response becomes the main hook
            
            # Try to extract names (capitalized words that might be characters/places)
            import re
            proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', response)
            if proper_nouns:
                seed.main_characters.extend(proper_nouns[:3])
                seed.supporting_npcs.extend(proper_nouns[3:6])
        
        return seed
    
    def validate_seed(self, seed: StorySeed) -> Tuple[bool, List[str]]:
        """
        Validate a story seed for completeness and quality
        
        Args:
            seed: StorySeed to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not seed.theme:
            issues.append("Missing theme")
        
        if not seed.setting:
            issues.append("Missing setting")
        
        if not seed.conflict and not seed.custom_text:
            issues.append("Missing conflict or custom text")
        
        if not seed.story_beats:
            issues.append("No story beats defined")
        
        # Check slider values are in valid range
        for attr in ['danger_level', 'discovery_factor', 'scary_factor', 'mystery_level', 'comedy_level']:
            value = getattr(seed, attr)
            if not (1 <= value <= 10):
                issues.append(f"Invalid {attr}: {value} (should be 1-10)")
        
        return len(issues) == 0, issues
    
    def export_seed(self, seed: StorySeed, filepath: str) -> bool:
        """
        Export seed to JSON file
        
        Args:
            seed: StorySeed to export
            filepath: Path to save file
            
        Returns:
            Success boolean
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(seed.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to export seed: {e}")
            return False
    
    def import_seed(self, filepath: str) -> Optional[StorySeed]:
        """
        Import seed from JSON file
        
        Args:
            filepath: Path to seed file
            
        Returns:
            StorySeed if successful, None if failed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return StorySeed.from_dict(data)
        except Exception as e:
            print(f"Failed to import seed: {e}")
            return None