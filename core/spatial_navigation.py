"""
Spatial Navigation System
Handles coherent room transitions and movement descriptions
"""
from typing import Dict, Optional, Tuple
import random


class SpatialNavigation:
    """Manages spatially aware movement between rooms"""
    
    def __init__(self, llm=None, fallback_mode=False):
        self.llm = llm
        self.fallback_mode = fallback_mode
        self.room_environment_map = {}  # room_id -> environment type
        self.transition_templates = self._initialize_transition_templates()
        
    def _initialize_transition_templates(self) -> Dict:
        """Initialize templates for different room type transitions"""
        return {
            # FROM -> TO transitions
            ("dungeon_entrance", "cavern"): [
                "You descend deeper into the dungeon, the stone walls giving way to natural rock formations.",
                "You move from the worked stone of the entrance into a natural cavern carved by time.",
                "The dungeon's constructed passages open into a vast underground cavern."
            ],
            ("cavern", "cavern"): [
                "You navigate through the winding cavern passages.",
                "You move deeper into the cave system, following natural rock formations.",
                "The cavern continues, its walls glistening with moisture."
            ],
            ("chamber", "hallway"): [
                "You leave the spacious chamber and enter a narrow corridor.",
                "The grand chamber gives way to a more confined passage.",
                "You step from the open space into a connecting hallway."
            ],
            ("hallway", "chamber"): [
                "The narrow passage opens into a larger chamber.",
                "You emerge from the corridor into a more spacious area.",
                "The confined hallway leads you into an expansive room."
            ],
            ("underground", "surface"): [
                "You ascend from the depths, feeling fresh air on your face.",
                "The underground passages lead you back toward the surface.",
                "You climb upward, leaving the subterranean world behind."
            ],
            ("surface", "underground"): [
                "You descend into the underground depths.",
                "The surface world fades as you venture into the depths below.",
                "You enter the shadowy underground realm."
            ],
            # Generic fallbacks
            ("indoor", "indoor"): [
                "You move through the interconnected passages.",
                "You continue through the structure's interior.",
                "The path leads you to another area of the complex."
            ],
            ("outdoor", "outdoor"): [
                "You travel across the landscape.",
                "Your journey continues through the terrain.",
                "You move onward through the environment."
            ]
        }
    
    def generate_movement_description(self, from_room_id: str, to_room_id: str, 
                                    direction: str, from_room_desc: str, 
                                    to_room_desc: str, theme: str) -> str:
        """Generate contextually appropriate movement description"""
        
        # Determine environment types
        from_env = self._classify_environment(from_room_id, from_room_desc, theme)
        to_env = self._classify_environment(to_room_id, to_room_desc, theme)
        
        # Store for future reference
        self.room_environment_map[from_room_id] = from_env
        self.room_environment_map[to_room_id] = to_env
        
        # Generate movement description
        if self.llm:
            return self._generate_llm_movement(from_env, to_env, direction, theme)
        else:
            if self.fallback_mode:
                return self._generate_template_movement(from_env, to_env, direction)
            else:
                raise RuntimeError("LLM is required for spatial navigation (fallback mode disabled)")
    
    def _classify_environment(self, room_id: str, room_desc: str, theme: str) -> str:
        """Classify room environment type based on description and ID"""
        
        # Check cache first
        if room_id in self.room_environment_map:
            return self.room_environment_map[room_id]
        
        desc_lower = room_desc.lower()
        
        # Specific environment detection
        if any(word in desc_lower for word in ["entrance", "gate", "threshold"]):
            return "dungeon_entrance"
        elif any(word in desc_lower for word in ["cavern", "cave", "grotto", "underground"]):
            return "cavern"
        elif any(word in desc_lower for word in ["chamber", "room", "hall"]):
            if any(word in desc_lower for word in ["vast", "grand", "large", "spacious"]):
                return "large_chamber"
            else:
                return "chamber"
        elif any(word in desc_lower for word in ["corridor", "hallway", "passage"]):
            return "hallway"
        elif any(word in desc_lower for word in ["tunnel", "shaft"]):
            return "tunnel"
        elif any(word in desc_lower for word in ["library", "study"]):
            return "library"
        elif any(word in desc_lower for word in ["stairs", "stairwell"]):
            return "stairwell"
        elif any(word in desc_lower for word in ["forest", "woods", "trees"]):
            return "forest"
        elif any(word in desc_lower for word in ["field", "meadow", "plain"]):
            return "field"
        elif any(word in desc_lower for word in ["tower", "spire"]):
            return "tower"
        elif any(word in desc_lower for word in ["basement", "cellar"]):
            return "basement"
        elif any(word in desc_lower for word in ["attic", "loft"]):
            return "attic"
        
        # Theme-based defaults
        if theme == "fantasy":
            return "chamber" if "start" not in room_id else "dungeon_entrance"
        elif theme == "sci-fi":
            return "corridor"
        elif theme == "horror":
            return "room"
        elif theme == "cyberpunk":
            return "corridor"
        
        return "unknown"
    
    def _generate_llm_movement(self, from_env: str, to_env: str, direction: str, theme: str) -> str:
        """Generate movement description using LLM"""
        
        prompt = f"""Generate a movement description for a {theme} setting.

Player is moving {direction} from a {from_env} to a {to_env}.

Requirements:
- 1-2 sentences maximum
- Describe the transition between environments
- Maintain spatial consistency
- Keep it atmospheric and immersive
- Don't contradict the environment types

Examples:
- Cavern to cavern: "You navigate deeper through the winding stone passages."
- Chamber to hallway: "You leave the spacious chamber and enter a narrow corridor."
- Entrance to cavern: "You descend deeper into the dungeon's natural depths."

Generate the movement description:"""
        
        try:
            response = self.llm.generate_response(prompt)
            if response and len(response.strip()) > 10:
                return response.strip()
        except Exception as e:
            if self.fallback_mode:
                return self._generate_template_movement(from_env, to_env, direction)
            else:
                raise RuntimeError(f"LLM movement description generation failed and fallback mode disabled: {e}")
        
        # If LLM response was too short, fallback or error
        if self.fallback_mode:
            return self._generate_template_movement(from_env, to_env, direction)
        else:
            raise RuntimeError("LLM generated insufficient movement description and fallback mode disabled")
    
    def _generate_template_movement(self, from_env: str, to_env: str, direction: str) -> str:
        """Generate movement description using templates"""
        
        # Direct transition match
        transition_key = (from_env, to_env)
        if transition_key in self.transition_templates:
            templates = self.transition_templates[transition_key]
            return random.choice(templates)
        
        # Generalized matches
        general_transitions = [
            (("dungeon_entrance", "cavern", "chamber", "hallway", "tunnel"), "underground"),
            (("forest", "field"), "outdoor"),
            (("chamber", "hallway", "library", "room"), "indoor")
        ]
        
        from_category = None
        to_category = None
        
        for envs, category in general_transitions:
            if from_env in envs:
                from_category = category
            if to_env in envs:
                to_category = category
        
        if from_category and to_category:
            general_key = (from_category, to_category)
            if general_key in self.transition_templates:
                templates = self.transition_templates[general_key]
                return random.choice(templates)
        
        # Ultimate fallback - direction-based
        direction_templates = {
            "north": "You head north through the interconnected passages.",
            "south": "You travel south, following the path ahead.",
            "east": "You move eastward through the area.",
            "west": "You head west along the available route.",
            "up": "You ascend to the area above.",
            "down": "You descend to the level below."
        }
        
        return direction_templates.get(direction, f"You move {direction}.")
    
    def validate_transition(self, from_env: str, to_env: str, direction: str) -> bool:
        """Validate if a transition makes spatial sense"""
        
        # Impossible transitions
        impossible_transitions = [
            ("surface", "surface", "down"),  # Can't go down from surface to surface
            ("basement", "attic", "north"),  # Can't go horizontally from basement to attic
            ("underground", "tower", "down")  # Can't go down from underground to tower
        ]
        
        transition = (from_env, to_env, direction)
        return transition not in impossible_transitions
    
    def get_environment_info(self, room_id: str) -> Optional[str]:
        """Get cached environment info for a room"""
        return self.room_environment_map.get(room_id)
    
    def suggest_logical_connections(self, room_env: str, theme: str) -> Dict[str, str]:
        """Suggest logical room connections based on environment"""
        
        suggestions = {
            "dungeon_entrance": {
                "north": "chamber", "south": "cavern", 
                "east": "hallway", "west": "hallway"
            },
            "cavern": {
                "north": "cavern", "south": "cavern",
                "east": "tunnel", "west": "chamber",
                "down": "cavern"
            },
            "chamber": {
                "north": "hallway", "south": "hallway",
                "east": "chamber", "west": "chamber"
            },
            "hallway": {
                "north": "chamber", "south": "chamber",
                "east": "chamber", "west": "room"
            },
            "forest": {
                "north": "forest", "south": "field",
                "east": "forest", "west": "forest"
            }
        }
        
        return suggestions.get(room_env, {
            "north": "chamber", "south": "chamber",
            "east": "chamber", "west": "chamber"
        })