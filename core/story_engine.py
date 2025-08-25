"""
Dynamic Story Engine
Generates emergent narratives and quest lines based on player choices and world state
"""
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class StoryTone(Enum):
    HEROIC = "heroic"
    DARK = "dark"
    MYSTERIOUS = "mysterious"
    COMEDIC = "comedic"
    TRAGIC = "tragic"
    EPIC = "epic"


class ConsequenceType(Enum):
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    CASCADING = "cascading"
    PERMANENT = "permanent"


@dataclass
class StoryThread:
    """Represents an ongoing narrative thread"""
    id: str
    title: str
    description: str
    theme: str
    tone: StoryTone
    complexity: int  # 1-10
    player_choices: List[Dict] = field(default_factory=list)
    consequences: List[Dict] = field(default_factory=list)
    npcs_involved: List[str] = field(default_factory=list)
    locations_involved: List[str] = field(default_factory=list)
    is_active: bool = True
    completion_percentage: float = 0.0


@dataclass
class WorldEvent:
    """Dynamic events that occur based on player actions"""
    id: str
    name: str
    description: str
    trigger_condition: Dict
    consequences: List[Dict]
    probability: float  # 0.0 to 1.0
    cooldown_turns: int = 0
    has_triggered: bool = False


class StoryEngine:
    """Manages dynamic story generation and player choice consequences"""
    
    def __init__(self, llm=None, fallback_mode=False):
        self.llm = llm
        self.fallback_mode = fallback_mode
        self.story_threads: List[StoryThread] = []
        self.world_events: List[WorldEvent] = []
        self.player_history: Dict[str, Any] = {
            "choices": [],
            "moral_alignment": 0,  # -100 to 100 (evil to good)
            "reputation": {},  # faction -> reputation score
            "story_beats": [],
            "character_arc": "unknown"
        }
        self.world_state: Dict[str, Any] = {
            "tension_level": 0,  # 0-100
            "chaos_factor": 0,   # 0-100  
            "mystery_depth": 0,  # 0-100
            "time_pressure": 0   # 0-100
        }
        self.narrative_memory: List[str] = []
        
    def initialize_story_arc(self, theme: str, player_background: Optional[Dict] = None) -> StoryThread:
        """Generate initial overarching story arc"""
        if not self.llm:
            if self.fallback_mode:
                return self._generate_fallback_story_arc(theme)
            else:
                raise RuntimeError("LLM is required for story arc generation (fallback mode disabled)")
        
        prompt = self._create_story_arc_prompt(theme, player_background)
        
        try:
            # Check if llm is the interface or the actual LLM
            if hasattr(self.llm, 'llm'):
                response = self.llm.llm.generate_response(prompt)
            else:
                response = self.llm.generate_response(prompt)
            return self._parse_story_arc_response(response, theme)
        except Exception as e:
            print(f"Story generation failed: {e}")
            if self.fallback_mode:
                return self._generate_fallback_story_arc(theme)
            else:
                raise RuntimeError(f"Story arc generation failed and fallback mode disabled: {e}")
    
    def _create_story_arc_prompt(self, theme: str, background: Optional[Dict]) -> str:
        """Create prompt for main story arc generation"""
        background_text = ""
        if background:
            background_text = f"Player background: {background.get('description', 'Unknown adventurer')}"
        
        return f"""Generate a dynamic story arc for a {theme} adventure game.

{background_text}

Create a multi-layered story with:
1. An overarching conflict/mystery
2. Personal stakes for the player
3. Multiple potential paths and endings
4. Opportunities for moral choices
5. Escalating tension and complexity

Format your response as:
TITLE: compelling story title
DESCRIPTION: 2-3 sentence story hook
TONE: [heroic/dark/mysterious/comedic/tragic/epic]
COMPLEXITY: [1-10 scale]
MAIN_CONFLICT: central tension or problem
PERSONAL_STAKES: why this matters to the player character
POTENTIAL_PATHS: path1 | path2 | path3
MORAL_DILEMMAS: dilemma1 | dilemma2 | dilemma3
KEY_NPCS: npc1 (role) | npc2 (role) | npc3 (role)

Example for fantasy:
TITLE: The Shattered Crown of Echoes
DESCRIPTION: Ancient magic is failing across the realm, and whispers speak of a lost crown that could restore balance - or destroy everything. You alone can hear the crown's call, but each step toward it awakens darker powers.
TONE: mysterious
COMPLEXITY: 7
MAIN_CONFLICT: The balance between order and chaos hangs on finding the crown before it falls into wrong hands
PERSONAL_STAKES: You're the only one who can hear the crown's voice - ignoring it means watching the world die
POTENTIAL_PATHS: Unite the fractured kingdoms | Embrace the dark power | Destroy the crown forever
MORAL_DILEMMAS: Save many by sacrificing few | Trust ancient magic vs. new technology | Power for justice vs. power corrupts
KEY_NPCS: Lyra the Last Mage (guide) | Darkborn Kael (rival) | Queen Morwyn (authority)"""

    def _parse_story_arc_response(self, response: str, theme: str) -> StoryThread:
        """Parse LLM story arc response"""
        data = {}
        lines = response.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip().upper()] = value.strip()
        
        return StoryThread(
            id="main_arc",
            title=data.get("TITLE", "The Adventure Begins"),
            description=data.get("DESCRIPTION", "Your journey starts here..."),
            theme=theme,
            tone=StoryTone(data.get("TONE", "heroic").lower()),
            complexity=int(data.get("COMPLEXITY", "5"))
        )
    
    def _generate_fallback_story_arc(self, theme: str) -> StoryThread:
        """Fallback story generation"""
        fallback_stories = {
            "fantasy": StoryThread(
                id="main_arc",
                title="The Awakening Shadow",
                description="Dark forces stir in the depths while ancient powers call to you. Your choices will shape the realm's fate.",
                theme=theme,
                tone=StoryTone.MYSTERIOUS,
                complexity=6
            ),
            "sci-fi": StoryThread(
                id="main_arc", 
                title="Signal in the Void",
                description="A mysterious transmission from deep space leads you into a conspiracy that threatens all known worlds.",
                theme=theme,
                tone=StoryTone.DARK,
                complexity=7
            ),
            "horror": StoryThread(
                id="main_arc",
                title="The Watchers in Stone",
                description="Reality fractures around ancient monuments, and you're the only one who sees the truth lurking beneath.",
                theme=theme,
                tone=StoryTone.TRAGIC,
                complexity=8
            ),
            "cyberpunk": StoryThread(
                id="main_arc",
                title="Ghost in the Machine",
                description="Corporate secrets and digital souls collide as you uncover who's really pulling the strings in the net.",
                theme=theme,
                tone=StoryTone.DARK,
                complexity=7
            )
        }
        
        return fallback_stories.get(theme, fallback_stories["fantasy"])
    
    def process_player_choice(self, choice: str, context: Dict) -> Dict[str, Any]:
        """Process player choice and generate consequences"""
        choice_data = {
            "choice": choice,
            "context": context,
            "location": context.get("location", "unknown"),
            "npcs_present": context.get("npcs", []),
            "timestamp": len(self.player_history["choices"])
        }
        
        self.player_history["choices"].append(choice_data)
        
        # Analyze choice for moral implications
        moral_impact = self._analyze_moral_impact(choice, context)
        self.player_history["moral_alignment"] += moral_impact
        
        # Generate immediate consequences
        immediate_consequences = self._generate_immediate_consequences(choice, context)
        
        # Plan delayed consequences
        delayed_consequences = self._plan_delayed_consequences(choice, context)
        
        # Update world state
        self._update_world_state_from_choice(choice, context)
        
        # Generate narrative response
        narrative_response = self._generate_choice_narrative(choice, context, immediate_consequences)
        
        return {
            "narrative": narrative_response,
            "immediate_consequences": immediate_consequences,
            "delayed_consequences": delayed_consequences,
            "moral_impact": moral_impact,
            "world_state_changes": self._get_world_state_changes()
        }
    
    def _analyze_moral_impact(self, choice: str, context: Dict) -> int:
        """Analyze moral implications of player choice"""
        choice_lower = choice.lower()
        
        # Positive moral actions
        if any(word in choice_lower for word in ["help", "save", "protect", "heal", "give", "share"]):
            return random.randint(5, 15)
        
        # Negative moral actions  
        elif any(word in choice_lower for word in ["attack", "steal", "lie", "betray", "kill", "harm"]):
            return random.randint(-15, -5)
        
        # Neutral actions
        else:
            return random.randint(-2, 2)
    
    def _generate_immediate_consequences(self, choice: str, context: Dict) -> List[Dict]:
        """Generate immediate consequences for player choice"""
        consequences = []
        
        # Simple pattern-based consequences
        choice_lower = choice.lower()
        
        if "attack" in choice_lower:
            consequences.append({
                "type": "combat_initiated",
                "description": "Your aggressive action has started a fight!",
                "severity": "high"
            })
        
        elif "help" in choice_lower:
            consequences.append({
                "type": "reputation_gain",
                "description": "Your helpful nature is noticed by those around you.",
                "severity": "low"
            })
        
        elif "steal" in choice_lower:
            consequences.append({
                "type": "reputation_loss",
                "description": "Your thievery might have consequences...",
                "severity": "medium"
            })
        
        return consequences
    
    def _plan_delayed_consequences(self, choice: str, context: Dict) -> List[Dict]:
        """Plan consequences that will manifest later"""
        delayed = []
        
        # Major choices create delayed consequences
        if any(word in choice.lower() for word in ["betray", "promise", "swear", "vow"]):
            delayed.append({
                "type": "delayed_reaction",
                "trigger_after_turns": random.randint(5, 15),
                "description": "Your words today may echo in unexpected ways...",
                "choice_reference": choice
            })
        
        return delayed
    
    def _update_world_state_from_choice(self, choice: str, context: Dict):
        """Update world state based on player choice"""
        choice_lower = choice.lower()
        
        # Violence increases tension
        if any(word in choice_lower for word in ["attack", "fight", "kill"]):
            self.world_state["tension_level"] = min(100, self.world_state["tension_level"] + 10)
            self.world_state["chaos_factor"] = min(100, self.world_state["chaos_factor"] + 5)
        
        # Investigation increases mystery
        elif any(word in choice_lower for word in ["examine", "investigate", "search", "explore"]):
            self.world_state["mystery_depth"] = min(100, self.world_state["mystery_depth"] + 3)
    
    def _generate_choice_narrative(self, choice: str, context: Dict, consequences: List[Dict]) -> str:
        """Generate narrative response to player choice"""
        if not self.llm:
            if self.fallback_mode:
                return f"You {choice.lower()}. The world shifts around your decision."
            else:
                raise RuntimeError("LLM is required for choice narrative generation (fallback mode disabled)")
        
        prompt = f"""The player chose: "{choice}"

Context: {context.get('situation', 'general situation')}
Location: {context.get('location', 'unknown')}
NPCs present: {', '.join(context.get('npcs', []))}
Theme: {context.get('theme', 'fantasy')}

Current world state:
- Tension: {self.world_state['tension_level']}/100
- Chaos: {self.world_state['chaos_factor']}/100  
- Mystery: {self.world_state['mystery_depth']}/100

Player's moral alignment: {self.player_history['moral_alignment']}

Generate a dramatic, immersive response (2-3 sentences) that:
1. Describes the immediate result of their action
2. Hints at potential consequences
3. Maintains narrative tension
4. Reflects the world's current mood

Keep it engaging and consequence-focused."""
        
        try:
            # Check if llm is the interface or the actual LLM
            if hasattr(self.llm, 'llm'):
                return self.llm.llm.generate_response(prompt).strip()
            else:
                return self.llm.generate_response(prompt).strip()
        except Exception as e:
            if self.fallback_mode:
                return f"You {choice.lower()}, and the consequences ripple outward like stones cast into still water."
            else:
                raise RuntimeError(f"Choice narrative generation failed and fallback mode disabled: {e}")
    
    def _get_world_state_changes(self) -> Dict:
        """Get current world state for reporting"""
        return self.world_state.copy()
    
    def generate_dynamic_encounter(self, location: str, theme: str) -> Optional[Dict]:
        """Generate dynamic encounters based on player history and world state"""
        if not self.llm:
            if self.fallback_mode:
                return self._generate_fallback_encounter(location, theme)
            else:
                raise RuntimeError("LLM is required for dynamic encounter generation (fallback mode disabled)")
        
        # Consider player's story so far
        recent_choices = self.player_history["choices"][-3:] if self.player_history["choices"] else []
        
        prompt = f"""Generate a dynamic encounter for location: {location} (theme: {theme})

Player's recent choices: {[c['choice'] for c in recent_choices]}
Moral alignment: {self.player_history['moral_alignment']}
World tension: {self.world_state['tension_level']}/100
World chaos: {self.world_state['chaos_factor']}/100

Create an encounter that:
1. Reflects consequences of recent player choices
2. Offers meaningful moral/strategic decisions
3. Advances or complicates the ongoing story
4. Matches the current world tension level

Format as:
TYPE: [combat/social/puzzle/mystery/moral_dilemma]
DESCRIPTION: vivid encounter description
CHOICES: choice1 | choice2 | choice3
STAKES: what's at risk
NPC_INVOLVED: name (motivation)"""
        
        try:
            # Check if llm is the interface or the actual LLM
            if hasattr(self.llm, 'llm'):
                response = self.llm.llm.generate_response(prompt)
            else:
                response = self.llm.generate_response(prompt)
            return self._parse_encounter_response(response)
        except Exception as e:
            if self.fallback_mode:
                return self._generate_fallback_encounter(location, theme)
            else:
                raise RuntimeError(f"Dynamic encounter generation failed and fallback mode disabled: {e}")
    
    def _parse_encounter_response(self, response: str) -> Dict:
        """Parse LLM encounter response"""
        data = {}
        lines = response.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip().upper()] = value.strip()
        
        choices = data.get('CHOICES', 'Continue | Leave | Investigate').split('|')
        
        return {
            "type": data.get('TYPE', 'social'),
            "description": data.get('DESCRIPTION', 'Something interesting happens...'),
            "choices": [c.strip() for c in choices],
            "stakes": data.get('STAKES', 'Unknown consequences await'),
            "npc": data.get('NPC_INVOLVED', 'Stranger (unknown)')
        }
    
    def _generate_fallback_encounter(self, location: str, theme: str) -> Dict:
        """Fallback encounter generation"""
        encounters = {
            "fantasy": [
                {
                    "type": "moral_dilemma",
                    "description": "A wounded traveler begs for help, but pursuing bandits approach rapidly.",
                    "choices": ["Help the traveler", "Hide and avoid trouble", "Confront the bandits"],
                    "stakes": "A life hangs in the balance, and your choice defines who you are.",
                    "npc": "Wounded Merchant (desperate for survival)"
                },
                {
                    "type": "mystery",
                    "description": "Strange runes pulse with otherworldly light on an ancient wall.",
                    "choices": ["Touch the runes", "Study them carefully", "Leave immediately"],
                    "stakes": "Ancient magic rarely awakens without reason.",
                    "npc": "Echo of the Past (seeking resolution)"
                }
            ]
        }
        
        theme_encounters = encounters.get(theme, encounters["fantasy"])
        return random.choice(theme_encounters)
    
    def get_story_status(self) -> Dict:
        """Get current story status and active threads"""
        return {
            "active_threads": len([t for t in self.story_threads if t.is_active]),
            "player_alignment": self.player_history["moral_alignment"],
            "world_state": self.world_state,
            "choices_made": len(self.player_history["choices"]),
            "character_arc": self._determine_character_arc()
        }
    
    def _determine_character_arc(self) -> str:
        """Determine player's character arc based on choices"""
        alignment = self.player_history["moral_alignment"]
        
        if alignment > 50:
            return "Hero's Journey"
        elif alignment < -50:
            return "Fall from Grace"
        elif self.world_state["mystery_depth"] > 60:
            return "Seeker of Truth"
        elif self.world_state["chaos_factor"] > 60:
            return "Agent of Chaos"
        else:
            return "Complex Wanderer"