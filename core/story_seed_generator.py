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
            seed = self._populate_seed_from_theme_dynamically(seed, detected_theme)
        
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
        seed = self._populate_seed_from_theme_dynamically(seed, theme)
        
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
    
    def _populate_seed_from_theme_dynamically(self, seed: StorySeed, theme: str) -> StorySeed:
        """
        Populate a seed with dynamically generated theme-based content using GenerativeNameEngine
        
        Args:
            seed: The StorySeed to populate
            theme: The theme to use
            
        Returns:
            Updated StorySeed
        """
        # Import LLMNameEngine locally to avoid circular imports
        from core.llm_name_engine import LLMNameEngine
        name_engine = LLMNameEngine(llm=self.llm_interface.llm if self.llm_interface else None, fallback_mode=True)
        
        # Generate dynamic setting (location name)
        seed.setting = name_engine.generate_location_name("dungeon", theme)
        
        # Generate dynamic conflict
        conflict_types = {
            "fantasy": ["curse", "threat", "siege", "hunt"],
            "sci-fi": ["invasion", "malfunction", "conspiracy", "rebellion"],
            "horror": ["presence", "terror", "evil", "nightmare"],
            "cyberpunk": ["espionage", "theft", "uprising", "crisis"]
        }
        conflict_type = random.choice(conflict_types.get(theme, conflict_types["fantasy"]))
        
        # Create more dynamic conflict descriptions
        if theme == "fantasy":
            adjectives = ["ancient", "dark", "mysterious", "forgotten"]
            entities = ["sorcerer", "curse", "evil", "artifact"]
        elif theme == "sci-fi":
            adjectives = ["alien", "system", "corporate", "AI"]
            entities = ["invasion", "malfunction", "conspiracy", "rebellion"]
        elif theme == "horror":
            adjectives = ["supernatural", "ancient", "cursed", "nightmare"]
            entities = ["presence", "evil", "terror", "entity"]
        else:  # cyberpunk
            adjectives = ["corporate", "data", "neural", "digital"]
            entities = ["espionage", "theft", "uprising", "warfare"]
        
        adj = random.choice(adjectives)
        entity = random.choice(entities)
        seed.conflict = f"{adj} {entity} {conflict_type}"
        
        # Generate dynamic main character
        character_roles = {
            "fantasy": ["knight", "wizard", "rogue", "paladin", "ranger"],
            "sci-fi": ["marine", "scientist", "engineer", "pilot", "explorer"],
            "horror": ["investigator", "survivor", "medium", "hunter"],
            "cyberpunk": ["hacker", "runner", "agent", "samurai", "operative"]
        }
        
        role = random.choice(character_roles.get(theme, character_roles["fantasy"]))
        character_name = name_engine.generate_dynamic_name(theme, role, "full")
        seed.main_characters = [character_name]
        
        # Generate dynamic story beats
        seed.story_beats = [
            f"Introduction to {seed.setting}",
            f"Discovery of {seed.conflict}",
            "First challenge or obstacle",
            "Character development or revelation",
            "Climax and resolution"
        ]
        
        # Generate plot hooks using dynamic content
        seed.plot_hooks = [
            f"Explore the mysteries of {seed.setting}",
            f"Confront the {seed.conflict}",
            f"Ally with or challenge {character_name}"
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
                response = self.llm_interface.llm.generate_response(prompt)
                
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
            return f"""Create the final, detailed story concept with complete details:

Current story elements:
Setting: {seed.setting}
Conflict: {seed.conflict}
Characters: {', '.join(seed.main_characters) if seed.main_characters else 'TBD'}
{base_info}

Write a rich, complete story concept that includes:
- Named characters with full names and clear roles (e.g., "Sir Marcus Blackwood, veteran knight")
- Specific organizations, locations, or entities with descriptive names
- Concrete story hooks and mysteries that drive the plot forward
- A clear progression path showing how the adventure unfolds step by step

Write 6-8 complete sentences. Ensure each sentence is fully finished without cutting off mid-thought. Include specific character names, place names, and plot details that bring the story to life.
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
            # Generate actionable story progression separately
            seed.story_beats = self._generate_story_progression(seed)
        
        else:  # iteration == 2
            # Final detailed story
            seed.conflict = response
            # Extract detailed elements
            seed.plot_hooks = [response]  # The whole response becomes the main hook
            
            # Try to extract names (capitalized words that might be characters/places)
            import re
            
            # Look for clear character patterns first
            character_patterns = [
                r'\b(Sir|Lady|Lord|Captain|General|Master|Doctor|Professor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b',  # First Last name patterns
                r'\b([A-Z][a-z]{3,})\s+(the|of|from)\b',  # Names with titles
            ]
            
            found_characters = []
            for pattern in character_patterns:
                matches = re.findall(pattern, response)
                for match in matches:
                    if isinstance(match, tuple):
                        name = ' '.join(m for m in match if m and not m.lower() in ['the', 'of', 'from'])
                    else:
                        name = match
                    
                    if name and len(name) > 2:
                        found_characters.append(name)
            
            # Fallback to proper nouns but filter out common words
            if not found_characters:
                proper_nouns = re.findall(r'\b[A-Z][a-z]{3,}\b', response)
                common_words = {'You', 'The', 'This', 'That', 'They', 'There', 'Your', 'Their', 'Heart', 'Sanctum', 'Temple', 'Chasm', 'Echo', 'Echoes', 'Magic', 'Order', 'past', 'Past', 'Time', 'Space'}
                found_characters = [noun for noun in proper_nouns if noun not in common_words]
            
            if found_characters:
                # Clear existing characters first to avoid duplication
                existing = set(seed.main_characters)
                new_chars = [char for char in found_characters[:3] if char not in existing]
                seed.main_characters.extend(new_chars[:3])
                
                remaining = [char for char in found_characters[3:] if char not in existing and char not in new_chars]
                seed.supporting_npcs.extend(remaining[:3])
        
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
    
    def _generate_story_progression(self, seed: StorySeed) -> List[str]:
        """
        Generate meaningful story progression beats that serve actual gameplay purposes
        """
        if not self.llm_interface:
            raise ValueError("LLM interface is required for story progression generation")
        
        # Try LLM generation with fallback
        try:
            prompt = f"""Create 5 actionable story progression beats for a {seed.theme} adventure.

Setting: {seed.setting}
Danger Level: {seed.danger_level}/10
Mystery Level: {seed.mystery_level}/10
Discovery Factor: {seed.discovery_factor}/10

Requirements:
- Each beat should be a specific, actionable objective or challenge
- Progression should escalate in difficulty and stakes
- Include concrete goals like "find X", "defeat Y", "solve Z puzzle"
- Avoid vague atmospheric descriptions
- Focus on what the player needs to DO, not just what they see
- Each beat should lead logically to the next

Format as numbered list. Examples:
1. Locate the ancient key hidden in the eastern chambers
2. Solve the riddle of the three stone guardians
3. Navigate through the maze of mirrors without triggering traps
4. Confront and defeat the corrupted guardian of the inner sanctum
5. Retrieve the artifact and escape before the temple collapses

Generate 5 progression beats now:"""

            response = self.llm_interface.llm.generate_long_content(prompt, {"theme": seed.theme}, max_tokens=600)
            
            # Check for LLM error responses
            error_indicators = [
                "narrative threads take time", "storytelling forces", "creative energies",
                "ancient magic remains silent", "mystical energies", "forces stir but remain"
            ]
            
            is_error_response = any(indicator in response.lower() for indicator in error_indicators)
            
            if is_error_response or len(response.strip()) < 50:
                # LLM failed, use fallback
                return self._generate_fallback_progression(seed)
            
            # Parse the numbered list
            beats = []
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering and clean up
                    clean_beat = line.split('.', 1)[-1].strip()
                    if self._is_valid_story_beat(clean_beat, beats):
                        beats.append(clean_beat)
            
            # Require sufficient beats
            if len(beats) >= 3:  # Accept if we got at least 3 good beats
                return beats[:5]
            else:
                # Not enough valid beats found, use fallback
                return self._generate_fallback_progression(seed)
                    
        except Exception as e:
            # Any other error, use fallback
            return self._generate_fallback_progression(seed)
    
    def _generate_fallback_progression(self, seed: StorySeed) -> List[str]:
        """
        Generate basic fallback story progression when LLM is unavailable or fails
        """
        theme_progressions = {
            'fantasy': [
                f"Explore the entrance to {seed.setting}",
                f"Find a way to overcome the first guardian or obstacle",
                f"Solve a puzzle or riddle to progress deeper",
                f"Confront the main challenge or boss enemy",
                f"Complete the quest and escape safely"
            ],
            'sci-fi': [
                f"Access the {seed.setting} facility",
                f"Navigate through security systems and defenses",
                f"Locate and activate key systems or terminals",
                f"Battle or evade hostile forces or AI",
                f"Complete the mission and extract successfully"
            ],
            'horror': [
                f"Enter the cursed {seed.setting}",
                f"Survive the first supernatural encounter",
                f"Uncover clues about the dark history",
                f"Face the source of evil or terror",
                f"Escape before becoming trapped forever"
            ],
            'cyberpunk': [
                f"Infiltrate the {seed.setting} complex",
                f"Hack through digital security barriers",
                f"Gather critical data or disable systems",
                f"Evade corporate security forces",
                f"Complete the run and disappear into the network"
            ]
        }
        
        base_progression = theme_progressions.get(seed.theme, theme_progressions['fantasy'])
        
        # Customize based on danger level
        if seed.danger_level >= 7:
            base_progression[3] = base_progression[3].replace("Confront the main challenge", "Battle through multiple dangerous challenges")
        elif seed.danger_level <= 3:
            base_progression[3] = base_progression[3].replace("Confront", "Carefully approach")
            
        return base_progression
    
    def _is_valid_story_beat(self, beat: str, existing_beats: List[str]) -> bool:
        """
        Validate that a story beat is meaningful and unique
        """
        if not beat or len(beat) < 15:
            return False
        
        # Check for actionable verbs
        actionable_verbs = [
            "find", "locate", "discover", "collect", "gather", "retrieve",
            "solve", "decode", "decipher", "unlock", "activate", "repair",
            "defeat", "confront", "battle", "survive", "escape", "evade",
            "navigate", "traverse", "explore", "investigate", "search",
            "protect", "defend", "rescue", "deliver", "obtain", "acquire"
        ]
        
        beat_lower = beat.lower()
        has_action = any(verb in beat_lower for verb in actionable_verbs)
        
        if not has_action:
            return False
        
        # Check for purely vague/atmospheric words that indicate description rather than action
        # Only reject beats that are PRIMARILY descriptive, not those that use atmospheric language
        purely_descriptive_phrases = [
            "you see", "you notice", "you feel", "you hear", "you sense",
            "the air is", "the atmosphere", "feeling of", "sense of"
        ]
        
        is_purely_descriptive = any(phrase in beat_lower for phrase in purely_descriptive_phrases)
        
        # Additional check: if the beat contains actionable verbs but also descriptive language,
        # allow it if it has more action than description
        if is_purely_descriptive:
            return False
        
        # Check for uniqueness (avoid similar beats)
        for existing in existing_beats:
            similarity = self._calculate_similarity(beat.lower(), existing.lower())
            if similarity > 0.7:  # Too similar
                return False
        
        return True
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple similarity between two text strings"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
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