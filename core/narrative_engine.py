"""
Narrative Engine for Cra-mud-gen
Integrates story seeds with world generation and manages narrative progression
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import random
import json
from .story_seed_generator import StorySeed, NarrativeState


@dataclass
class NarrativeEvent:
    """Represents a significant narrative event in the story"""
    
    event_type: str  # 'discovery', 'conflict', 'character_introduction', 'plot_twist'
    description: str
    room_id: Optional[str] = None
    character_involved: Optional[str] = None
    story_beat_index: int = -1
    triggered: bool = False
    conditions: Dict[str, Any] = None
    consequences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}
        if self.consequences is None:
            self.consequences = {}


class NarrativeEngine:
    """
    Manages story progression and integration with world generation
    """
    
    def __init__(self, llm_interface=None):
        """
        Initialize the narrative engine
        
        Args:
            llm_interface: Optional LLM interface for dynamic content generation
        """
        self.llm_interface = llm_interface
        self.narrative_state: Optional[NarrativeState] = None
        self.narrative_events: List[NarrativeEvent] = []
        self.story_context: Dict[str, Any] = {}
        
        # Cache for generated content to avoid repetition
        self.content_cache = {
            'room_descriptions': {},
            'npc_dialogues': {},
            'item_descriptions': {},
            'event_descriptions': {}
        }
        
    def initialize_narrative(self, story_seed: StorySeed) -> NarrativeState:
        """
        Initialize the narrative state with a story seed
        
        Args:
            story_seed: The StorySeed to base the narrative on
            
        Returns:
            Initialized NarrativeState
        """
        self.narrative_state = NarrativeState(seed=story_seed)
        self.story_context = {
            'theme': story_seed.theme,
            'mood_multipliers': {
                'danger': story_seed.danger_level / 10.0,
                'discovery': story_seed.discovery_factor / 10.0,
                'scary': story_seed.scary_factor / 10.0,
                'mystery': story_seed.mystery_level / 10.0,
                'comedy': story_seed.comedy_level / 10.0
            },
            'active_plot_threads': []
        }
        
        # Generate narrative events from story beats
        self._generate_narrative_events()
        
        return self.narrative_state
    
    def _generate_narrative_events(self):
        """Generate narrative events based on the story seed"""
        if not self.narrative_state:
            return
        
        seed = self.narrative_state.seed
        
        # Create events from story beats
        for i, beat in enumerate(seed.story_beats):
            event_type = self._categorize_story_beat(beat, i)
            
            event = NarrativeEvent(
                event_type=event_type,
                description=beat,
                story_beat_index=i,
                conditions=self._get_beat_conditions(i),
                consequences=self._get_beat_consequences(i, beat)
            )
            
            self.narrative_events.append(event)
        
        # Add random events based on theme and mood
        self._add_theme_specific_events(seed)
    
    def _categorize_story_beat(self, beat: str, index: int) -> str:
        """
        Categorize a story beat into event types
        
        Args:
            beat: The story beat text
            index: Index of the beat
            
        Returns:
            Event type string
        """
        beat_lower = beat.lower()
        
        if index == 0:
            return 'introduction'
        elif 'discover' in beat_lower or 'find' in beat_lower:
            return 'discovery'
        elif 'conflict' in beat_lower or 'battle' in beat_lower or 'fight' in beat_lower:
            return 'conflict'
        elif 'character' in beat_lower or 'meet' in beat_lower:
            return 'character_introduction'
        elif 'reveal' in beat_lower or 'twist' in beat_lower:
            return 'plot_twist'
        elif 'climax' in beat_lower or 'final' in beat_lower:
            return 'climax'
        else:
            return 'progression'
    
    def _get_beat_conditions(self, beat_index: int) -> Dict[str, Any]:
        """
        Get conditions for when a story beat should trigger
        
        Args:
            beat_index: Index of the story beat
            
        Returns:
            Dictionary of conditions
        """
        conditions = {'min_rooms_explored': beat_index * 2}
        
        if beat_index > 0:
            conditions['previous_beat_completed'] = beat_index - 1
        
        # Add random conditions based on beat index
        if beat_index >= 2:
            conditions['min_items_found'] = max(1, beat_index - 1)
        
        if beat_index >= 3:
            conditions['min_npcs_met'] = 1
        
        return conditions
    
    def _get_beat_consequences(self, beat_index: int, beat_description: str) -> Dict[str, Any]:
        """
        Get consequences for completing a story beat
        
        Args:
            beat_index: Index of the story beat
            beat_description: Description of the beat
            
        Returns:
            Dictionary of consequences
        """
        consequences = {
            'narrative_tension_change': random.uniform(-0.2, 0.3),
            'unlock_areas': [],
            'spawn_npcs': [],
            'spawn_items': []
        }
        
        # Add specific consequences based on beat type and content
        if 'discover' in beat_description.lower():
            consequences['spawn_items'].append('mysterious_artifact')
            consequences['narrative_tension_change'] += 0.1
        
        if 'conflict' in beat_description.lower():
            consequences['spawn_npcs'].append('enemy_lieutenant')
            consequences['narrative_tension_change'] += 0.2
        
        return consequences
    
    def _add_theme_specific_events(self, seed: StorySeed):
        """
        Add theme-specific random events
        
        Args:
            seed: The story seed to base events on
        """
        theme_events = {
            'fantasy': [
                'Ancient magic stirs in the depths',
                'A dragon\'s roar echoes through the halls',
                'Mystical runes begin to glow',
                'The spirits of the past whisper warnings'
            ],
            'sci-fi': [
                'System alerts flash across displays',
                'Strange energy readings detected',
                'AI subsystems report anomalies',
                'Atmospheric processors show instability'
            ],
            'horror': [
                'Shadows move where no light falls',
                'Whispers echo from empty rooms',
                'Temperature drops unexpectedly',
                'Strange scratching sounds from the walls'
            ],
            'cyberpunk': [
                'Corporate security drones patrol nearby',
                'Net traffic spikes indicate data breach',
                'Black ICE detected in local systems',
                'Underground contacts report movement'
            ]
        }
        
        events_for_theme = theme_events.get(seed.theme, theme_events['fantasy'])
        
        # Add 2-3 random events
        for _ in range(random.randint(2, 3)):
            event = NarrativeEvent(
                event_type='atmospheric',
                description=random.choice(events_for_theme),
                conditions={'random_chance': 0.3}  # 30% chance per room
            )
            self.narrative_events.append(event)
    
    def check_narrative_triggers(self, game_state: Dict[str, Any]) -> List[NarrativeEvent]:
        """
        Check if any narrative events should trigger based on game state
        
        Args:
            game_state: Current game state including player progress
            
        Returns:
            List of triggered events
        """
        triggered_events = []
        
        if not self.narrative_state:
            return triggered_events
        
        for event in self.narrative_events:
            if event.triggered:
                continue
            
            if self._check_event_conditions(event, game_state):
                triggered_events.append(event)
                event.triggered = True
                self._apply_event_consequences(event, game_state)
        
        return triggered_events
    
    def _check_event_conditions(self, event: NarrativeEvent, game_state: Dict[str, Any]) -> bool:
        """
        Check if an event's conditions are met
        
        Args:
            event: The narrative event to check
            game_state: Current game state
            
        Returns:
            True if conditions are met
        """
        conditions = event.conditions
        
        # Check minimum rooms explored
        if 'min_rooms_explored' in conditions:
            if game_state.get('rooms_explored', 0) < conditions['min_rooms_explored']:
                return False
        
        # Check previous beat completion
        if 'previous_beat_completed' in conditions:
            required_beat = conditions['previous_beat_completed']
            if self.narrative_state.current_beat <= required_beat:
                return False
        
        # Check minimum items found
        if 'min_items_found' in conditions:
            if game_state.get('items_found', 0) < conditions['min_items_found']:
                return False
        
        # Check minimum NPCs met
        if 'min_npcs_met' in conditions:
            if game_state.get('npcs_met', 0) < conditions['min_npcs_met']:
                return False
        
        # Check random chance
        if 'random_chance' in conditions:
            return random.random() < conditions['random_chance']
        
        return True
    
    def _apply_event_consequences(self, event: NarrativeEvent, game_state: Dict[str, Any]):
        """
        Apply the consequences of a triggered event
        
        Args:
            event: The triggered event
            game_state: Current game state to modify
        """
        consequences = event.consequences
        
        # Adjust narrative tension
        if 'narrative_tension_change' in consequences:
            change = consequences['narrative_tension_change']
            self.narrative_state.narrative_tension = max(0.0, min(1.0, 
                self.narrative_state.narrative_tension + change))
        
        # Unlock new areas
        if 'unlock_areas' in consequences:
            for area in consequences['unlock_areas']:
                if 'unlocked_areas' not in game_state:
                    game_state['unlocked_areas'] = []
                if area not in game_state['unlocked_areas']:
                    game_state['unlocked_areas'].append(area)
        
        # Add NPCs to spawn list
        if 'spawn_npcs' in consequences:
            for npc in consequences['spawn_npcs']:
                if 'npcs_to_spawn' not in game_state:
                    game_state['npcs_to_spawn'] = []
                game_state['npcs_to_spawn'].append(npc)
        
        # Add items to spawn list
        if 'spawn_items' in consequences:
            for item in consequences['spawn_items']:
                if 'items_to_spawn' not in game_state:
                    game_state['items_to_spawn'] = []
                game_state['items_to_spawn'].append(item)
    
    def get_contextual_room_description(self, base_description: str, room_id: str, 
                                      game_state: Dict[str, Any]) -> str:
        """
        Enhance room description with narrative context
        
        Args:
            base_description: The base room description
            room_id: Unique room identifier
            game_state: Current game state
            
        Returns:
            Enhanced description with narrative elements
        """
        if not self.narrative_state:
            return base_description
        
        # Check cache first
        cache_key = f"{room_id}_{self.narrative_state.current_beat}"
        if cache_key in self.content_cache['room_descriptions']:
            return self.content_cache['room_descriptions'][cache_key]
        
        enhanced_description = base_description
        
        # Add narrative atmosphere based on current tension
        tension = self.narrative_state.narrative_tension
        seed = self.narrative_state.seed
        
        if tension > 0.7:
            if seed.theme == 'horror':
                enhanced_description += " A sense of dread permeates the air."
            elif seed.theme == 'sci-fi':
                enhanced_description += " Warning lights cast eerie shadows."
            else:
                enhanced_description += " Tension fills the atmosphere."
        
        # Add story-specific elements
        current_beat = self.narrative_state.get_current_beat()
        if current_beat and random.random() < 0.4:  # 40% chance
            if 'discovery' in current_beat.lower():
                enhanced_description += " Something important feels close at hand."
            elif 'conflict' in current_beat.lower():
                enhanced_description += " You sense potential danger ahead."
        
        # Use LLM for more sophisticated enhancement if available
        if self.llm_interface and len(enhanced_description) == len(base_description):
            enhanced_description = self._llm_enhance_description(
                base_description, room_id, game_state
            )
        
        # Cache the result
        self.content_cache['room_descriptions'][cache_key] = enhanced_description
        return enhanced_description
    
    def _llm_enhance_description(self, base_description: str, room_id: str, 
                               game_state: Dict[str, Any]) -> str:
        """
        Use LLM to enhance room description with narrative context
        
        Args:
            base_description: Base description to enhance
            room_id: Room identifier
            game_state: Current game state
            
        Returns:
            LLM-enhanced description
        """
        if not self.llm_interface or not self.narrative_state:
            return base_description
        
        seed = self.narrative_state.seed
        current_beat = self.narrative_state.get_current_beat()
        tension = self.narrative_state.narrative_tension
        
        prompt = f"""Enhance this room description with narrative atmosphere:

Base description: {base_description}

Story context:
- Theme: {seed.theme}
- Current story beat: {current_beat or 'Beginning'}
- Narrative tension: {tension:.2f} (0=calm, 1=intense)
- Danger level: {seed.danger_level}/10
- Mystery level: {seed.mystery_level}/10
- Scary factor: {seed.scary_factor}/10

Add 1-2 sentences that enhance the atmosphere without changing the basic room structure. 
Focus on mood, subtle details, and hints that align with the current story progression.
Keep the enhancement subtle and immersive.
"""
        
        try:
            response = self.llm_interface.generate_text(prompt, max_tokens=150)
            if response and len(response.strip()) > 10:
                return f"{base_description} {response.strip()}"
        except Exception as e:
            print(f"LLM enhancement failed: {e}")
        
        return base_description
    
    def get_npc_dialogue_context(self, npc_name: str, base_personality: str) -> Dict[str, Any]:
        """
        Get narrative context for NPC dialogues
        
        Args:
            npc_name: Name of the NPC
            base_personality: Base personality description
            
        Returns:
            Dictionary with dialogue context
        """
        if not self.narrative_state:
            return {'personality': base_personality}
        
        seed = self.narrative_state.seed
        current_beat = self.narrative_state.get_current_beat()
        
        context = {
            'personality': base_personality,
            'story_awareness': current_beat or "Beginning of the adventure",
            'mood_modifiers': {
                'tension_level': self.narrative_state.narrative_tension,
                'comedy_factor': seed.comedy_level / 10.0,
                'mystery_factor': seed.mystery_level / 10.0
            },
            'plot_knowledge': [],
            'special_dialogue': []
        }
        
        # Add plot knowledge based on story progression
        if self.narrative_state.current_beat > 0:
            context['plot_knowledge'] = self.narrative_state.completed_beats
        
        # Add special dialogue based on story flags
        for flag, value in self.narrative_state.story_flags.items():
            if value and flag not in context['special_dialogue']:
                context['special_dialogue'].append(f"References {flag}")
        
        return context
    
    def advance_story(self, trigger_reason: str = "natural_progression") -> bool:
        """
        Advance the story to the next beat
        
        Args:
            trigger_reason: Why the story is advancing
            
        Returns:
            True if story advanced, False if at end
        """
        if not self.narrative_state:
            return False
        
        if self.narrative_state.advance_beat():
            # Log the advancement
            current_beat = self.narrative_state.get_current_beat()
            print(f"Story advanced: {current_beat}")
            
            # Adjust narrative tension based on new beat
            if current_beat:
                if 'climax' in current_beat.lower():
                    self.narrative_state.narrative_tension = min(1.0, 
                        self.narrative_state.narrative_tension + 0.3)
                elif 'resolution' in current_beat.lower():
                    self.narrative_state.narrative_tension = max(0.3, 
                        self.narrative_state.narrative_tension - 0.4)
            
            return True
        
        return False
    
    def track_player_action(self, action_type: str, details: Dict[str, Any] = None) -> List[str]:
        """
        Track a player action and check for story progression triggers
        
        Args:
            action_type: Type of action ('room_entered', 'item_taken', 'npc_talked', 'enemy_defeated')
            details: Additional details about the action
            
        Returns:
            List of story messages triggered by this action
        """
        if not self.narrative_state or not details:
            return []
        
        details = details or {}
        triggered_messages = []
        
        # Track the action
        if action_type not in self.narrative_state.player_choices:
            self.narrative_state.player_choices[action_type] = []
        self.narrative_state.player_choices[action_type].append(details)
        
        # Check for story beat progression triggers
        current_beat_index = self.narrative_state.current_beat
        
        if action_type == 'room_entered':
            rooms_explored = len(self.narrative_state.player_choices.get('room_entered', []))
            
            # Story progresses every 4-6 rooms explored
            if rooms_explored > 0 and rooms_explored % random.randint(4, 6) == 0:
                if self.advance_story("room_exploration"):
                    triggered_messages.append(f"As you explore deeper, the story unfolds...")
        
        elif action_type == 'item_taken':
            # Check for story-relevant items
            item_name = details.get('item', '').lower()
            if any(keyword in item_name for keyword in ['ancient', 'mysterious', 'magical', 'key', 'artifact']):
                if current_beat_index < len(self.narrative_state.seed.story_beats) - 1:
                    if random.random() < 0.6:  # 60% chance to advance story
                        if self.advance_story("important_item_found"):
                            triggered_messages.append(f"The {item_name} seems significant to your quest...")
        
        elif action_type == 'npc_talked':
            # NPCs can provide story progression hints or advance story
            npc_name = details.get('npc', '').lower()
            
            # Add NPC to active list if not already there
            if npc_name and npc_name not in self.narrative_state.active_npcs:
                self.narrative_state.active_npcs.append(npc_name)
                triggered_messages.append(f"{npc_name.title()} seems to know more about your journey...")
        
        elif action_type == 'enemy_defeated':
            # Combat can trigger story progression
            enemy_type = details.get('enemy_type', '').lower()
            if 'boss' in enemy_type or 'champion' in enemy_type or 'lord' in enemy_type:
                if random.random() < 0.8:  # 80% chance for boss defeats
                    if self.advance_story("boss_defeated"):
                        triggered_messages.append("Your victory echoes through the dungeon, changing everything...")
        
        # Check for story flag triggers
        self._check_story_flag_triggers(action_type, details, triggered_messages)
        
        return triggered_messages
    
    def _check_story_flag_triggers(self, action_type: str, details: Dict[str, Any], messages: List[str]):
        """Check and set story flags based on player actions"""
        
        if action_type == 'room_entered':
            room_type = details.get('room_type', '').lower()
            
            # Set flags for discovering special rooms
            if 'library' in room_type:
                if not self.narrative_state.story_flags.get('found_library'):
                    self.narrative_state.story_flags['found_library'] = True
                    messages.append("The ancient knowledge here might prove useful...")
            
            elif 'shrine' in room_type or 'altar' in room_type:
                if not self.narrative_state.story_flags.get('found_shrine'):
                    self.narrative_state.story_flags['found_shrine'] = True
                    messages.append("Sacred power emanates from this place...")
            
            elif 'armory' in room_type:
                if not self.narrative_state.story_flags.get('found_armory'):
                    self.narrative_state.story_flags['found_armory'] = True
                    messages.append("These weapons suggest a great conflict once took place here...")
        
        elif action_type == 'item_taken':
            item_name = details.get('item', '').lower()
            
            # Track important item categories
            if 'key' in item_name:
                self.narrative_state.story_flags['has_key'] = True
            elif 'weapon' in item_name or 'sword' in item_name:
                self.narrative_state.story_flags['armed'] = True
            elif 'scroll' in item_name or 'tome' in item_name:
                self.narrative_state.story_flags['has_knowledge'] = True
    
    def get_story_progression_hints(self) -> List[str]:
        """
        Get hints about story progression based on current state
        
        Returns:
            List of hint messages
        """
        if not self.narrative_state:
            return []
        
        hints = []
        current_beat = self.narrative_state.get_current_beat()
        
        if not current_beat:
            return ["Your adventure begins..."]
        
        # Provide hints based on current story beat
        beat_lower = current_beat.lower()
        
        if 'discover' in beat_lower or 'find' in beat_lower:
            hints.append("Search thoroughly - something important awaits discovery.")
            if not self.narrative_state.story_flags.get('found_library'):
                hints.append("Knowledge might be found in places of learning.")
        
        elif 'conflict' in beat_lower or 'battle' in beat_lower:
            hints.append("Danger approaches - be prepared for confrontation.")
            if not self.narrative_state.story_flags.get('armed'):
                hints.append("A weapon would serve you well in the trials ahead.")
        
        elif 'character' in beat_lower or 'meet' in beat_lower:
            hints.append("Others may hold keys to your destiny - seek them out.")
            if len(self.narrative_state.active_npcs) < 2:
                hints.append("More allies may be found in the depths below.")
        
        # Add general progression hints
        rooms_explored = len(self.narrative_state.player_choices.get('room_entered', []))
        if rooms_explored < 5:
            hints.append("Explore deeper to uncover the mysteries that lie ahead.")
        
        return hints[:2]  # Return at most 2 hints to avoid overwhelming the player
    
    def present_story_choice(self, choice_context: str, options: List[str]) -> Dict[str, Any]:
        """
        Present a story choice to the player
        
        Args:
            choice_context: Context/description of the choice situation
            options: List of available choice options
            
        Returns:
            Dictionary with choice information
        """
        if not self.narrative_state:
            return {"error": "No narrative state"}
        
        choice_id = f"choice_{len(self.narrative_state.player_choices.get('story_choices', []))}"
        
        choice_data = {
            "choice_id": choice_id,
            "context": choice_context,
            "options": options,
            "consequences_preview": self._preview_choice_consequences(options)
        }
        
        return choice_data
    
    def _preview_choice_consequences(self, options: List[str]) -> Dict[str, str]:
        """Preview potential consequences of choices"""
        previews = {}
        
        for i, option in enumerate(options):
            option_lower = option.lower()
            
            if 'aggressive' in option_lower or 'attack' in option_lower or 'fight' in option_lower:
                previews[option] = "This path may lead to conflict and danger."
            elif 'peaceful' in option_lower or 'negotiate' in option_lower or 'talk' in option_lower:
                previews[option] = "This approach might reveal information or allies."
            elif 'investigate' in option_lower or 'search' in option_lower or 'explore' in option_lower:
                previews[option] = "This choice could uncover secrets or treasures."
            elif 'retreat' in option_lower or 'leave' in option_lower or 'ignore' in option_lower:
                previews[option] = "This may preserve safety but miss opportunities."
            else:
                previews[option] = "The consequences of this choice are unclear."
        
        return previews
    
    def process_story_choice(self, choice_id: str, selected_option: str) -> Dict[str, Any]:
        """
        Process a player's story choice and apply consequences
        
        Args:
            choice_id: ID of the choice being made
            selected_option: The option the player selected
            
        Returns:
            Dictionary with results and consequences
        """
        if not self.narrative_state:
            return {"error": "No narrative state"}
        
        # Record the choice
        if 'story_choices' not in self.narrative_state.player_choices:
            self.narrative_state.player_choices['story_choices'] = []
        
        choice_record = {
            "choice_id": choice_id,
            "selected": selected_option,
            "timestamp": len(self.narrative_state.player_choices['story_choices'])
        }
        self.narrative_state.player_choices['story_choices'].append(choice_record)
        
        # Apply consequences
        consequences = self._apply_choice_consequences(selected_option)
        
        # Check if choice affects story progression
        story_impact = self._evaluate_story_impact(selected_option)
        
        return {
            "choice_recorded": True,
            "consequences": consequences,
            "story_impact": story_impact,
            "narrative_changes": self._get_narrative_changes(consequences)
        }
    
    def _apply_choice_consequences(self, selected_option: str) -> Dict[str, Any]:
        """Apply the consequences of a story choice"""
        consequences = {
            "story_flags_changed": [],
            "tension_change": 0.0,
            "npc_relationships": {},
            "world_changes": [],
            "future_options_modified": []
        }
        
        option_lower = selected_option.lower()
        
        # Aggressive/Combat choices
        if 'aggressive' in option_lower or 'attack' in option_lower or 'fight' in option_lower:
            consequences["tension_change"] = 0.2
            consequences["story_flags_changed"].append("chose_violence")
            consequences["world_changes"].append("Enemies are now more hostile")
            consequences["future_options_modified"].append("Peaceful resolutions may be harder")
            
            # Apply to narrative state
            self.narrative_state.story_flags["chose_violence"] = True
            self.narrative_state.narrative_tension = min(1.0, 
                self.narrative_state.narrative_tension + 0.2)
        
        # Peaceful/Diplomatic choices
        elif 'peaceful' in option_lower or 'negotiate' in option_lower or 'talk' in option_lower:
            consequences["tension_change"] = -0.1
            consequences["story_flags_changed"].append("chose_diplomacy")
            consequences["world_changes"].append("NPCs are more trusting")
            consequences["future_options_modified"].append("More dialogue options may appear")
            
            # Apply to narrative state
            self.narrative_state.story_flags["chose_diplomacy"] = True
            self.narrative_state.narrative_tension = max(0.0, 
                self.narrative_state.narrative_tension - 0.1)
        
        # Investigation/Exploration choices
        elif 'investigate' in option_lower or 'search' in option_lower or 'explore' in option_lower:
            consequences["story_flags_changed"].append("thorough_explorer")
            consequences["world_changes"].append("Hidden secrets may be revealed")
            consequences["future_options_modified"].append("Additional areas may become accessible")
            
            # Apply to narrative state
            self.narrative_state.story_flags["thorough_explorer"] = True
        
        # Cautious/Retreat choices
        elif 'retreat' in option_lower or 'leave' in option_lower or 'ignore' in option_lower:
            consequences["tension_change"] = -0.05
            consequences["story_flags_changed"].append("cautious_approach")
            consequences["world_changes"].append("Some opportunities may be missed")
            consequences["future_options_modified"].append("Safer but potentially less rewarding paths")
            
            # Apply to narrative state
            self.narrative_state.story_flags["cautious_approach"] = True
        
        return consequences
    
    def _evaluate_story_impact(self, selected_option: str) -> Dict[str, Any]:
        """Evaluate how a choice impacts the overall story"""
        impact = {
            "beat_progression_affected": False,
            "character_development": None,
            "plot_branch_unlocked": None,
            "ending_influenced": False
        }
        
        option_lower = selected_option.lower()
        current_beat = self.narrative_state.get_current_beat() or ""
        
        # Check if choice aligns with or conflicts with current story beat
        if current_beat:
            beat_lower = current_beat.lower()
            
            if 'conflict' in beat_lower and ('fight' in option_lower or 'aggressive' in option_lower):
                impact["beat_progression_affected"] = True
                impact["character_development"] = "warrior"
                if random.random() < 0.3:  # 30% chance
                    if self.advance_story("choice_alignment"):
                        impact["plot_branch_unlocked"] = "combat_mastery_path"
            
            elif 'discovery' in beat_lower and ('investigate' in option_lower or 'search' in option_lower):
                impact["beat_progression_affected"] = True
                impact["character_development"] = "scholar"
                if random.random() < 0.3:
                    if self.advance_story("choice_alignment"):
                        impact["plot_branch_unlocked"] = "knowledge_seeker_path"
        
        # Track choices for ending determination
        story_choices = self.narrative_state.player_choices.get('story_choices', [])
        if len(story_choices) >= 3:  # After 3+ choices, they start affecting ending
            impact["ending_influenced"] = True
        
        return impact
    
    def _get_narrative_changes(self, consequences: Dict[str, Any]) -> List[str]:
        """Convert consequences into narrative description messages"""
        messages = []
        
        for flag in consequences.get("story_flags_changed", []):
            if flag == "chose_violence":
                messages.append("Your aggressive approach echoes through the dungeon...")
            elif flag == "chose_diplomacy":
                messages.append("Your peaceful words create ripples of understanding...")
            elif flag == "thorough_explorer":
                messages.append("Your careful investigation reveals hidden depths...")
            elif flag == "cautious_approach":
                messages.append("Your prudent choice preserves future possibilities...")
        
        if consequences.get("tension_change", 0) > 0.1:
            messages.append("The atmosphere grows more tense and dangerous.")
        elif consequences.get("tension_change", 0) < -0.05:
            messages.append("A sense of calm begins to settle over the area.")
        
        return messages
    
    def get_available_story_choices(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate contextual story choices based on current situation
        
        Args:
            context: Current game context (room, NPCs, items, etc.)
            
        Returns:
            Story choice data or None if no choice available
        """
        if not self.narrative_state:
            return None
        
        # Don't present choices too frequently
        recent_choices = len(self.narrative_state.player_choices.get('story_choices', []))
        rooms_since_last_choice = len(self.narrative_state.player_choices.get('room_entered', [])) - recent_choices * 3
        
        if rooms_since_last_choice < 2:  # Wait at least 2 rooms between story choices
            return None
        
        # Generate choice based on context
        room_type = context.get('room_type', '').lower()
        has_npc = bool(context.get('npcs', []))
        has_enemies = bool(context.get('enemies', []))
        narrative_tension = self.narrative_state.narrative_tension
        
        if has_enemies and narrative_tension > 0.5:
            # Combat choice
            return self.present_story_choice(
                "Enemies block your path. How do you proceed?",
                [
                    "Attack immediately with full force",
                    "Try to negotiate or find peaceful solution", 
                    "Attempt to sneak around them",
                    "Retreat and find another route"
                ]
            )
        
        elif has_npc and 'library' in room_type:
            # Knowledge/NPC choice
            return self.present_story_choice(
                "A knowledgeable person offers to share ancient secrets. What do you do?",
                [
                    "Ask about the dungeon's history",
                    "Inquire about dangerous areas ahead",
                    "Request information about treasures",
                    "Politely decline and continue exploring"
                ]
            )
        
        elif 'shrine' in room_type or 'altar' in room_type:
            # Spiritual/magical choice
            return self.present_story_choice(
                "You discover a mystical shrine. What action do you take?",
                [
                    "Make an offering and pray for guidance",
                    "Study the symbols and inscriptions carefully",
                    "Take any valuable items you see",
                    "Leave the shrine undisturbed"
                ]
            )
        
        elif random.random() < 0.2:  # 20% random chance for general choice
            return self.present_story_choice(
                "You sense this is a moment of significance. How do you proceed?",
                [
                    "Press forward boldly and confidently",
                    "Proceed with careful observation",
                    "Take time to rest and plan",
                    "Trust your instincts completely"
                ]
            )
        
        return None
    
    def adapt_story_dynamically(self, player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically adapt the story based on player behavior and stats
        
        Args:
            player_stats: Dictionary with player statistics and behavior patterns
            
        Returns:
            Dictionary with adaptation results
        """
        if not self.narrative_state:
            return {"error": "No narrative state"}
        
        adaptation_results = {
            "story_modifications": [],
            "new_beats_generated": [],
            "difficulty_adjusted": False,
            "narrative_focus_shift": None
        }
        
        # Analyze player behavior patterns
        behavior_analysis = self._analyze_player_behavior(player_stats)
        
        # Adapt story based on player preferences
        self._adapt_to_player_preferences(behavior_analysis, adaptation_results)
        
        # Adjust narrative difficulty
        self._adjust_narrative_difficulty(player_stats, adaptation_results)
        
        # Generate new content if needed
        self._generate_adaptive_content(behavior_analysis, adaptation_results)
        
        return adaptation_results
    
    def _analyze_player_behavior(self, player_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze player behavior patterns to inform story adaptation"""
        
        # Get player action history
        choices = self.narrative_state.player_choices
        
        analysis = {
            "playstyle": "balanced",  # Default
            "preferences": {
                "combat": 0.5,
                "exploration": 0.5,
                "diplomacy": 0.5,
                "mystery": 0.5
            },
            "risk_tolerance": 0.5,
            "story_engagement": 0.5,
            "exploration_thoroughness": 0.5
        }
        
        # Analyze combat behavior
        enemy_encounters = choices.get('enemy_defeated', [])
        total_encounters = len(enemy_encounters)
        if total_encounters > 0:
            boss_fights = sum(1 for encounter in enemy_encounters 
                            if 'boss' in encounter.get('enemy_type', '').lower())
            analysis["preferences"]["combat"] = min(1.0, (total_encounters + boss_fights * 2) / 10)
        
        # Analyze exploration behavior
        rooms_entered = choices.get('room_entered', [])
        total_rooms = len(rooms_entered)
        if total_rooms > 0:
            unique_room_types = len(set(room.get('room_type', '') for room in rooms_entered))
            analysis["exploration_thoroughness"] = min(1.0, unique_room_types / max(5, total_rooms * 0.3))
            analysis["preferences"]["exploration"] = min(1.0, total_rooms / 15)
        
        # Analyze social interaction
        npcs_talked = choices.get('npc_talked', [])
        if len(npcs_talked) > 0:
            analysis["preferences"]["diplomacy"] = min(1.0, len(npcs_talked) / 5)
        
        # Analyze story choices
        story_choices = choices.get('story_choices', [])
        if len(story_choices) > 0:
            aggressive_choices = sum(1 for choice in story_choices 
                                   if any(word in choice.get('selected', '').lower() 
                                         for word in ['attack', 'aggressive', 'fight']))
            peaceful_choices = sum(1 for choice in story_choices 
                                 if any(word in choice.get('selected', '').lower() 
                                       for word in ['peaceful', 'negotiate', 'talk']))
            investigative_choices = sum(1 for choice in story_choices 
                                      if any(word in choice.get('selected', '').lower() 
                                            for word in ['investigate', 'search', 'explore']))
            
            total_story_choices = len(story_choices)
            if total_story_choices > 0:
                analysis["preferences"]["combat"] = max(analysis["preferences"]["combat"],
                                                      aggressive_choices / total_story_choices)
                analysis["preferences"]["diplomacy"] = max(analysis["preferences"]["diplomacy"],
                                                         peaceful_choices / total_story_choices)
                analysis["preferences"]["mystery"] = investigative_choices / total_story_choices
                analysis["risk_tolerance"] = (aggressive_choices + investigative_choices) / total_story_choices
        
        # Determine overall playstyle
        prefs = analysis["preferences"]
        if prefs["combat"] > 0.6:
            analysis["playstyle"] = "warrior"
        elif prefs["diplomacy"] > 0.6:
            analysis["playstyle"] = "diplomat"
        elif prefs["mystery"] > 0.6:
            analysis["playstyle"] = "scholar"
        elif prefs["exploration"] > 0.6:
            analysis["playstyle"] = "explorer"
        
        return analysis
    
    def _adapt_to_player_preferences(self, behavior_analysis: Dict[str, Any], results: Dict[str, Any]):
        """Adapt story content to match player preferences"""
        
        playstyle = behavior_analysis["playstyle"]
        preferences = behavior_analysis["preferences"]
        
        # Modify future story beats based on playstyle
        if playstyle == "warrior" and preferences["combat"] > 0.7:
            # Add more combat-focused story beats
            if len(self.narrative_state.seed.story_beats) < 8:  # Don't overstuff
                new_beat = "A legendary weapon calls out to you from the depths"
                self.narrative_state.seed.story_beats.append(new_beat)
                results["new_beats_generated"].append(new_beat)
                results["narrative_focus_shift"] = "combat_focused"
        
        elif playstyle == "scholar" and preferences["mystery"] > 0.7:
            # Add more mystery/knowledge-focused beats
            if len(self.narrative_state.seed.story_beats) < 8:
                new_beat = "Ancient texts reveal a hidden truth about this place"
                self.narrative_state.seed.story_beats.append(new_beat)
                results["new_beats_generated"].append(new_beat)
                results["narrative_focus_shift"] = "knowledge_focused"
        
        elif playstyle == "diplomat" and preferences["diplomacy"] > 0.7:
            # Add more NPC/social interaction beats
            if len(self.narrative_state.seed.story_beats) < 8:
                new_beat = "A faction of inhabitants offers alliance or enmity"
                self.narrative_state.seed.story_beats.append(new_beat)
                results["new_beats_generated"].append(new_beat)
                results["narrative_focus_shift"] = "social_focused"
        
        # Adjust story flags to match preferences
        if preferences["combat"] > 0.6:
            self.narrative_state.story_flags["prefers_combat"] = True
            results["story_modifications"].append("NPCs now respect your martial prowess")
        
        if preferences["diplomacy"] > 0.6:
            self.narrative_state.story_flags["skilled_diplomat"] = True
            results["story_modifications"].append("Word of your diplomatic skills spreads")
        
        if behavior_analysis["exploration_thoroughness"] > 0.7:
            self.narrative_state.story_flags["thorough_explorer"] = True
            results["story_modifications"].append("Your methodical exploration reveals hidden secrets")
    
    def _adjust_narrative_difficulty(self, player_stats: Dict[str, Any], results: Dict[str, Any]):
        """Adjust story difficulty based on player performance"""
        
        player_level = player_stats.get('level', 1)
        rooms_explored = len(self.narrative_state.player_choices.get('room_entered', []))
        deaths = player_stats.get('death_count', 0)
        
        # Calculate difficulty adjustment
        if deaths == 0 and rooms_explored > 10:
            # Player is doing well, increase challenge
            self.narrative_state.narrative_tension = min(1.0, 
                self.narrative_state.narrative_tension + 0.1)
            results["difficulty_adjusted"] = True
            results["story_modifications"].append("The dungeon seems to respond to your competence with greater challenges")
        
        elif deaths > 2 and rooms_explored < 8:
            # Player struggling, provide assistance
            self.narrative_state.narrative_tension = max(0.2, 
                self.narrative_state.narrative_tension - 0.15)
            results["difficulty_adjusted"] = True
            results["story_modifications"].append("Fortune seems to smile upon you, offering respite")
            
            # Add helpful story flag
            self.narrative_state.story_flags["needs_assistance"] = True
    
    def _generate_adaptive_content(self, behavior_analysis: Dict[str, Any], results: Dict[str, Any]):
        """Generate new story content based on analysis"""
        
        # Generate character-specific story elements
        playstyle = behavior_analysis["playstyle"]
        
        if playstyle == "warrior":
            # Add combat mastery subplot
            if "combat_mastery_unlocked" not in self.narrative_state.story_flags:
                self.narrative_state.story_flags["combat_mastery_unlocked"] = True
                results["story_modifications"].append("Your combat skills attract the attention of ancient spirits")
        
        elif playstyle == "scholar":
            # Add knowledge seeking subplot
            if "ancient_knowledge_unlocked" not in self.narrative_state.story_flags:
                self.narrative_state.story_flags["ancient_knowledge_unlocked"] = True
                results["story_modifications"].append("Your thirst for knowledge opens doors to forgotten lore")
        
        elif playstyle == "diplomat":
            # Add alliance building subplot
            if "diplomatic_connections" not in self.narrative_state.story_flags:
                self.narrative_state.story_flags["diplomatic_connections"] = True
                results["story_modifications"].append("Your diplomatic nature forges unexpected alliances")
        
        # Adaptive narrative events based on player behavior
        risk_tolerance = behavior_analysis["risk_tolerance"]
        if risk_tolerance > 0.7:
            # High risk player - add high reward opportunities
            high_risk_event = NarrativeEvent(
                event_type="high_risk_opportunity",
                description="A dangerous path promises great rewards",
                conditions={"random_chance": 0.4},
                consequences={"spawn_items": ["legendary_artifact"], "narrative_tension_change": 0.2}
            )
            self.narrative_events.append(high_risk_event)
            results["story_modifications"].append("Dangerous opportunities begin to present themselves")
        
        elif risk_tolerance < 0.3:
            # Low risk player - add safer progression options
            safe_event = NarrativeEvent(
                event_type="safe_progression",
                description="A secure path forward reveals itself",
                conditions={"random_chance": 0.3},
                consequences={"unlock_areas": ["safe_passage"], "narrative_tension_change": -0.1}
            )
            self.narrative_events.append(safe_event)
            results["story_modifications"].append("Safer paths begin to manifest around you")
    
    def get_adaptive_ending_path(self) -> str:
        """
        Determine which ending path the player is heading towards based on their choices
        
        Returns:
            String describing the likely ending path
        """
        if not self.narrative_state:
            return "unknown"
        
        story_flags = self.narrative_state.story_flags
        choices = self.narrative_state.player_choices.get('story_choices', [])
        
        # Count different types of choices
        combat_score = 0
        diplomacy_score = 0
        knowledge_score = 0
        
        for choice in choices:
            selected = choice.get('selected', '').lower()
            if any(word in selected for word in ['attack', 'fight', 'aggressive']):
                combat_score += 1
            elif any(word in selected for word in ['peaceful', 'negotiate', 'talk']):
                diplomacy_score += 1
            elif any(word in selected for word in ['investigate', 'study', 'learn']):
                knowledge_score += 1
        
        # Consider story flags
        if story_flags.get('chose_violence'):
            combat_score += 2
        if story_flags.get('chose_diplomacy'):
            diplomacy_score += 2
        if story_flags.get('thorough_explorer') or story_flags.get('has_knowledge'):
            knowledge_score += 2
        
        # Determine ending path
        total_scores = combat_score + diplomacy_score + knowledge_score
        if total_scores == 0:
            return "neutral_ending"
        
        if combat_score > diplomacy_score and combat_score > knowledge_score:
            return "warrior_ending"
        elif diplomacy_score > combat_score and diplomacy_score > knowledge_score:
            return "diplomatic_ending"
        elif knowledge_score > combat_score and knowledge_score > diplomacy_score:
            return "scholar_ending"
        else:
            return "balanced_ending"
    
    def create_narrative_continuity_thread(self, room_id: str, event_type: str, details: Dict[str, Any]) -> str:
        """
        Create a narrative thread that will continue across multiple rooms
        
        Args:
            room_id: Room where the thread originates
            event_type: Type of continuity ('mystery', 'character', 'item', 'conflict')
            details: Details about the thread
            
        Returns:
            Thread ID for tracking
        """
        if not self.narrative_state:
            return ""
        
        thread_id = f"{event_type}_{len(self.narrative_state.story_flags)}"
        
        # Create continuity data
        continuity_data = {
            "thread_id": thread_id,
            "origin_room": room_id,
            "event_type": event_type,
            "details": details,
            "progression_rooms": [room_id],
            "current_stage": 0,
            "max_stages": details.get("stages", 3),
            "references": []
        }
        
        # Store in narrative state
        if 'continuity_threads' not in self.narrative_state.story_flags:
            self.narrative_state.story_flags['continuity_threads'] = {}
        
        self.narrative_state.story_flags['continuity_threads'][thread_id] = continuity_data
        
        return thread_id
    
    def advance_continuity_thread(self, thread_id: str, room_id: str) -> Optional[Dict[str, Any]]:
        """
        Advance a narrative continuity thread in a new room
        
        Args:
            thread_id: ID of the thread to advance
            room_id: Current room ID
            
        Returns:
            Continuity event details or None
        """
        if not self.narrative_state or 'continuity_threads' not in self.narrative_state.story_flags:
            return None
        
        threads = self.narrative_state.story_flags['continuity_threads']
        if thread_id not in threads:
            return None
        
        thread = threads[thread_id]
        
        # Check if thread should appear in this room
        if not self._should_thread_appear(thread, room_id):
            return None
        
        # Advance the thread
        thread['current_stage'] += 1
        thread['progression_rooms'].append(room_id)
        
        # Generate continuity event
        event = self._generate_continuity_event(thread, room_id)
        thread['references'].append({
            "room_id": room_id,
            "stage": thread['current_stage'],
            "description": event.get('description', '')
        })
        
        return event
    
    def _should_thread_appear(self, thread: Dict[str, Any], room_id: str) -> bool:
        """Determine if a continuity thread should appear in the current room"""
        
        # Don't appear in the same room twice
        if room_id in thread['progression_rooms']:
            return False
        
        # Thread is completed
        if thread['current_stage'] >= thread['max_stages']:
            return False
        
        # Random chance based on thread type and stage
        base_chance = 0.3  # 30% base chance
        
        # Increase chance as story progresses
        stage_multiplier = 1 + (thread['current_stage'] * 0.2)
        
        # Thread-specific modifiers
        event_type = thread['event_type']
        if event_type == 'mystery':
            base_chance = 0.4  # Mysteries appear more frequently
        elif event_type == 'character':
            base_chance = 0.25  # Characters less frequent but more impactful
        elif event_type == 'conflict':
            base_chance = 0.35  # Conflicts build tension
        
        final_chance = base_chance * stage_multiplier
        return random.random() < final_chance
    
    def _generate_continuity_event(self, thread: Dict[str, Any], room_id: str) -> Dict[str, Any]:
        """Generate a continuity event for the thread"""
        
        event_type = thread['event_type']
        stage = thread['current_stage']
        details = thread['details']
        
        event = {
            "thread_id": thread['thread_id'],
            "room_id": room_id,
            "stage": stage,
            "description": "",
            "interaction_options": [],
            "story_impact": "minor"
        }
        
        if event_type == 'mystery':
            event.update(self._generate_mystery_continuity(details, stage))
        elif event_type == 'character':
            event.update(self._generate_character_continuity(details, stage))
        elif event_type == 'item':
            event.update(self._generate_item_continuity(details, stage))
        elif event_type == 'conflict':
            event.update(self._generate_conflict_continuity(details, stage))
        
        return event
    
    def _generate_mystery_continuity(self, details: Dict[str, Any], stage: int) -> Dict[str, Any]:
        """Generate mystery continuity event"""
        
        mystery_name = details.get('name', 'ancient mystery')
        
        if stage == 1:
            return {
                "description": f"You notice more clues about {mystery_name}. Strange symbols mark the walls.",
                "interaction_options": ["Examine the symbols closely", "Note the pattern for later", "Ignore the markings"],
                "story_impact": "minor"
            }
        elif stage == 2:
            return {
                "description": f"The mystery of {mystery_name} deepens. You find a torn piece of ancient parchment.",
                "interaction_options": ["Try to decipher the text", "Save it with other clues", "Search for more pieces"],
                "story_impact": "moderate"
            }
        else:  # Final stage
            return {
                "description": f"The truth about {mystery_name} becomes clear! Ancient forces stir in response.",
                "interaction_options": ["Embrace the revelation", "Prepare for consequences", "Try to contain the discovery"],
                "story_impact": "major"
            }
    
    def _generate_character_continuity(self, details: Dict[str, Any], stage: int) -> Dict[str, Any]:
        """Generate character continuity event"""
        
        character_name = details.get('name', 'mysterious figure')
        
        if stage == 1:
            return {
                "description": f"You find evidence of {character_name}'s presence - fresh footprints in the dust.",
                "interaction_options": ["Follow the trail", "Examine the footprints", "Proceed cautiously"],
                "story_impact": "minor"
            }
        elif stage == 2:
            return {
                "description": f"Personal belongings of {character_name} lie scattered here, as if they left in haste.",
                "interaction_options": ["Search through the items", "Look for signs of struggle", "Call out their name"],
                "story_impact": "moderate"
            }
        else:  # Final stage
            return {
                "description": f"You finally encounter {character_name}! They seem changed by their ordeal.",
                "interaction_options": ["Approach peacefully", "Question them about their journey", "Offer assistance"],
                "story_impact": "major"
            }
    
    def _generate_item_continuity(self, details: Dict[str, Any], stage: int) -> Dict[str, Any]:
        """Generate item-related continuity event"""
        
        item_name = details.get('name', 'legendary artifact')
        
        if stage == 1:
            return {
                "description": f"Energy resonates from somewhere nearby - {item_name} must be close.",
                "interaction_options": ["Search for the source", "Follow the energy trail", "Proceed with caution"],
                "story_impact": "minor"
            }
        elif stage == 2:
            return {
                "description": f"The power of {item_name} grows stronger. Mystical barriers begin to weaken.",
                "interaction_options": ["Break through the barriers", "Study the magical patterns", "Gather your strength"],
                "story_impact": "moderate"
            }
        else:  # Final stage
            return {
                "description": f"{item_name} lies before you, radiating immense power!",
                "interaction_options": ["Take the artifact", "Study it first", "Approach with reverence"],
                "story_impact": "major"
            }
    
    def _generate_conflict_continuity(self, details: Dict[str, Any], stage: int) -> Dict[str, Any]:
        """Generate conflict continuity event"""
        
        conflict_name = details.get('name', 'ancient war')
        
        if stage == 1:
            return {
                "description": f"Echoes of {conflict_name} linger here. Old battle scars mark the walls.",
                "interaction_options": ["Examine the battle damage", "Pay respects to the fallen", "Search for useful items"],
                "story_impact": "minor"
            }
        elif stage == 2:
            return {
                "description": f"The conflict of {conflict_name} intensifies. You hear distant sounds of battle.",
                "interaction_options": ["Move toward the sounds", "Prepare for combat", "Find a defensive position"],
                "story_impact": "moderate"
            }
        else:  # Final stage
            return {
                "description": f"The culmination of {conflict_name} unfolds before you! Choose your side wisely.",
                "interaction_options": ["Join the battle", "Try to end the conflict", "Protect the innocent"],
                "story_impact": "major"
            }
    
    def get_room_narrative_continuity(self, room_id: str) -> List[Dict[str, Any]]:
        """
        Get all active narrative continuity elements for a room
        
        Args:
            room_id: Room to check for continuity elements
            
        Returns:
            List of active continuity events
        """
        if not self.narrative_state or 'continuity_threads' not in self.narrative_state.story_flags:
            return []
        
        active_events = []
        threads = self.narrative_state.story_flags['continuity_threads']
        
        for thread_id, thread in threads.items():
            event = self.advance_continuity_thread(thread_id, room_id)
            if event:
                active_events.append(event)
        
        return active_events
    
    def create_callback_reference(self, room_id: str, reference_type: str, reference_data: Dict[str, Any]) -> str:
        """
        Create a callback reference that can be mentioned in future rooms
        
        Args:
            room_id: Room where event occurred
            reference_type: Type of reference ('npc_met', 'item_found', 'choice_made', 'mystery_discovered')
            reference_data: Data about the reference
            
        Returns:
            Reference ID
        """
        if not self.narrative_state:
            return ""
        
        reference_id = f"{reference_type}_{room_id}_{len(self.narrative_state.story_flags)}"
        
        # Store reference data
        if 'callback_references' not in self.narrative_state.story_flags:
            self.narrative_state.story_flags['callback_references'] = {}
        
        self.narrative_state.story_flags['callback_references'][reference_id] = {
            "room_id": room_id,
            "type": reference_type,
            "data": reference_data,
            "reference_count": 0,
            "created_at": len(self.narrative_state.player_choices.get('room_entered', []))
        }
        
        return reference_id
    
    def get_narrative_callbacks(self, current_room: str) -> List[str]:
        """
        Get narrative callback references that should be mentioned in descriptions
        
        Args:
            current_room: Current room ID
            
        Returns:
            List of callback description strings
        """
        if not self.narrative_state or 'callback_references' not in self.narrative_state.story_flags:
            return []
        
        callbacks = []
        references = self.narrative_state.story_flags['callback_references']
        
        # Don't callback to the same room
        for ref_id, ref_data in references.items():
            if ref_data['room_id'] == current_room:
                continue
            
            # Limit callback frequency
            if ref_data['reference_count'] > 2:
                continue
            
            # 30% chance to reference previous events
            if random.random() < 0.3:
                callback_text = self._generate_callback_text(ref_data)
                if callback_text:
                    callbacks.append(callback_text)
                    ref_data['reference_count'] += 1
        
        return callbacks[:2]  # At most 2 callbacks per room
    
    def _generate_callback_text(self, ref_data: Dict[str, Any]) -> str:
        """Generate callback text based on reference data"""
        
        ref_type = ref_data['type']
        data = ref_data['data']
        
        if ref_type == 'npc_met':
            npc_name = data.get('name', 'someone')
            return f"You recall your encounter with {npc_name} and their words echo in your mind."
        
        elif ref_type == 'item_found':
            item_name = data.get('name', 'something important')
            return f"The {item_name} you discovered earlier seems relevant to this place."
        
        elif ref_type == 'choice_made':
            choice_desc = data.get('description', 'your previous decision')
            return f"The consequences of {choice_desc} continue to unfold."
        
        elif ref_type == 'mystery_discovered':
            mystery_name = data.get('name', 'the mystery')
            return f"Clues about {mystery_name} seem to point to this location."
        
        return ""
    
    def establish_narrative_connection(self, from_room: str, to_room: str, connection_type: str) -> str:
        """
        Establish a narrative connection between two rooms
        
        Args:
            from_room: Source room ID
            to_room: Destination room ID  
            connection_type: Type of connection ('causal', 'thematic', 'character', 'mystery')
            
        Returns:
            Connection description text
        """
        if not self.narrative_state:
            return ""
        
        # Generate connection text based on type
        connection_texts = {
            'causal': [
                "Your actions in the previous area have clearly affected this place.",
                "The consequences of your choices led you here.",
                "What happened before has changed the nature of this space."
            ],
            'thematic': [
                "This area shares a mysterious connection with where you've been.",
                "The same dark energy that you felt before permeates this place.",
                "Familiar themes echo through this chamber."
            ],
            'character': [
                "Someone you met before clearly spent time in this room.",
                "The presence you encountered earlier has been here too.",
                "Traces of a familiar personality linger in this space."
            ],
            'mystery': [
                "The puzzle you're solving has another piece here.",
                "This location holds more clues to the mystery you're unraveling.",
                "The same ancient force that puzzled you before is at work here."
            ]
        }
        
        return random.choice(connection_texts.get(connection_type, ["Something connects this place to your journey."]))
    
    def get_narrative_momentum(self) -> Dict[str, Any]:
        """
        Calculate the current narrative momentum and pacing
        
        Returns:
            Dictionary with momentum information
        """
        if not self.narrative_state:
            return {"momentum": "static"}
        
        # Count recent story events
        recent_rooms = self.narrative_state.player_choices.get('room_entered', [])[-5:]
        recent_choices = self.narrative_state.player_choices.get('story_choices', [])[-3:]
        
        # Calculate momentum factors
        story_progression_rate = len(recent_choices) / max(1, len(recent_rooms))
        current_beat = self.narrative_state.current_beat
        total_beats = len(self.narrative_state.seed.story_beats)
        story_completion = current_beat / max(1, total_beats)
        
        # Determine momentum state
        if story_progression_rate > 0.4:
            momentum = "rapid"
        elif story_progression_rate > 0.2:
            momentum = "steady"
        elif story_progression_rate > 0.1:
            momentum = "slow"
        else:
            momentum = "static"
        
        return {
            "momentum": momentum,
            "progression_rate": story_progression_rate,
            "story_completion": story_completion,
            "narrative_tension": self.narrative_state.narrative_tension,
            "active_threads": len(self.narrative_state.story_flags.get('continuity_threads', {})),
            "pacing_suggestion": self._get_pacing_suggestion(momentum, story_completion)
        }
    
    def _get_pacing_suggestion(self, momentum: str, completion: float) -> str:
        """Get a suggestion for narrative pacing"""
        
        if momentum == "static" and completion < 0.5:
            return "Consider introducing a story choice or significant event"
        elif momentum == "rapid" and completion > 0.8:
            return "Allow time for reflection and consequences to unfold"
        elif momentum == "slow" and completion > 0.6:
            return "Increase tension and story urgency"
        else:
            return "Pacing is appropriate for current story stage"
    
    def get_narrative_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current narrative state
        
        Returns:
            Dictionary with narrative information
        """
        if not self.narrative_state:
            return {'error': 'No narrative initialized'}
        
        seed = self.narrative_state.seed
        current_beat = self.narrative_state.get_current_beat()
        
        return {
            'theme': seed.theme,
            'setting': seed.setting,
            'current_beat': current_beat,
            'progress': f"{self.narrative_state.current_beat + 1}/{len(seed.story_beats)}",
            'narrative_tension': self.narrative_state.narrative_tension,
            'active_story_flags': [flag for flag, value in 
                                 self.narrative_state.story_flags.items() if value],
            'completed_beats': len(self.narrative_state.completed_beats),
            'total_events': len(self.narrative_events),
            'triggered_events': len([e for e in self.narrative_events if e.triggered])
        }
    
    def export_narrative_state(self, filepath: str) -> bool:
        """
        Export current narrative state to file
        
        Args:
            filepath: Path to save the state
            
        Returns:
            Success boolean
        """
        if not self.narrative_state:
            return False
        
        try:
            export_data = {
                'narrative_state': {
                    'seed': self.narrative_state.seed.to_dict(),
                    'current_beat': self.narrative_state.current_beat,
                    'completed_beats': self.narrative_state.completed_beats,
                    'active_npcs': self.narrative_state.active_npcs,
                    'story_flags': self.narrative_state.story_flags,
                    'player_choices': self.narrative_state.player_choices,
                    'narrative_tension': self.narrative_state.narrative_tension
                },
                'events': [
                    {
                        'event_type': event.event_type,
                        'description': event.description,
                        'triggered': event.triggered,
                        'story_beat_index': event.story_beat_index
                    }
                    for event in self.narrative_events
                ],
                'story_context': self.story_context
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Failed to export narrative state: {e}")
            return False