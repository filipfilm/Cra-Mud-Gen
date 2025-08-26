"""
Quest System for Cra-mud-gen
Manages quest objectives, tracking, and completion
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json

class QuestStatus(Enum):
    INACTIVE = "inactive"      # Not started yet
    ACTIVE = "active"         # Currently active
    COMPLETED = "completed"   # Successfully completed
    FAILED = "failed"         # Failed or abandoned

class ObjectiveType(Enum):
    COLLECT = "collect"       # Collect N items
    TRAVEL = "travel"         # Go to a location
    INTERACT = "interact"     # Use/examine/talk to something
    SOLVE = "solve"          # Solve a puzzle
    DEFEAT = "defeat"        # Defeat enemies
    DISCOVER = "discover"    # Discover/explore areas

@dataclass
class QuestObjective:
    """Individual quest objective"""
    id: str
    description: str
    type: ObjectiveType
    target: str                    # What to collect/interact with/etc
    target_count: int = 1          # How many (for collect objectives)
    current_progress: int = 0       # Current progress
    completed: bool = False
    hints: List[str] = field(default_factory=list)
    
    def progress_percentage(self) -> float:
        """Get completion percentage"""
        return (self.current_progress / max(1, self.target_count)) * 100
    
    def advance_progress(self, amount: int = 1) -> bool:
        """Advance progress and return True if objective completed"""
        old_progress = self.current_progress
        self.current_progress = min(self.current_progress + amount, self.target_count)
        
        if self.current_progress >= self.target_count and not self.completed:
            self.completed = True
            return True
        return False

@dataclass 
class Quest:
    """Complete quest with multiple objectives"""
    id: str
    title: str
    description: str
    objectives: List[QuestObjective] = field(default_factory=list)
    status: QuestStatus = QuestStatus.INACTIVE
    rewards: Dict[str, Any] = field(default_factory=dict)
    story_beat_index: Optional[int] = None  # Links to story beat
    
    def is_completed(self) -> bool:
        """Check if all objectives are completed"""
        return all(obj.completed for obj in self.objectives)
    
    def get_active_objectives(self) -> List[QuestObjective]:
        """Get all uncompleted objectives"""
        return [obj for obj in self.objectives if not obj.completed]
    
    def get_completed_objectives(self) -> List[QuestObjective]:
        """Get all completed objectives"""
        return [obj for obj in self.objectives if obj.completed]
    
    def progress_percentage(self) -> float:
        """Get overall quest completion percentage"""
        if not self.objectives:
            return 0.0
        completed = len(self.get_completed_objectives())
        return (completed / len(self.objectives)) * 100

class QuestSystem:
    """Manages all quests and quest progression"""
    
    def __init__(self, llm_interface=None):
        self.quests: Dict[str, Quest] = {}
        self.active_quests: List[str] = []  # Quest IDs that are currently active
        self.completed_quests: List[str] = []
        self.llm = llm_interface
        
    def add_quest(self, quest: Quest) -> bool:
        """Add a new quest to the system"""
        if quest.id not in self.quests:
            self.quests[quest.id] = quest
            return True
        return False
    
    def activate_quest(self, quest_id: str) -> bool:
        """Activate a quest"""
        if quest_id in self.quests and quest_id not in self.active_quests:
            self.quests[quest_id].status = QuestStatus.ACTIVE
            self.active_quests.append(quest_id)
            return True
        return False
    
    def complete_quest(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Complete a quest and return rewards"""
        if quest_id in self.active_quests:
            quest = self.quests[quest_id]
            quest.status = QuestStatus.COMPLETED
            self.active_quests.remove(quest_id)
            self.completed_quests.append(quest_id)
            return quest.rewards
        return None
    
    def update_objective_progress(self, target: str, objective_type: ObjectiveType, amount: int = 1) -> List[str]:
        """Update progress for objectives matching target and type. Returns completed quest IDs"""
        completed_quests = []
        
        for quest_id in self.active_quests:
            quest = self.quests[quest_id]
            
            for objective in quest.objectives:
                if objective.type == objective_type and objective.target.lower() in target.lower():
                    if objective.advance_progress(amount):
                        print(f"✅ Objective completed: {objective.description}")
                        
                        # Check if entire quest is now complete
                        if quest.is_completed():
                            completed_quests.append(quest_id)
                            
        return completed_quests
    
    def get_quest_log(self) -> Dict[str, Any]:
        """Get formatted quest log for display"""
        log = {
            "active_quests": [],
            "completed_count": len(self.completed_quests),
            "total_count": len(self.quests)
        }
        
        for quest_id in self.active_quests:
            quest = self.quests[quest_id]
            quest_info = {
                "id": quest.id,
                "title": quest.title,
                "description": quest.description,
                "progress": quest.progress_percentage(),
                "objectives": []
            }
            
            for obj in quest.objectives:
                obj_info = {
                    "description": obj.description,
                    "completed": obj.completed,
                    "progress": f"{obj.current_progress}/{obj.target_count}" if obj.target_count > 1 else None,
                    "hints": obj.hints
                }
                quest_info["objectives"].append(obj_info)
            
            log["active_quests"].append(quest_info)
            
        return log
    
    def generate_quests_from_story_beats(self, story_beats: List[str]) -> List[Quest]:
        """Convert story beats into structured quests"""
        quests = []
        
        for i, beat in enumerate(story_beats):
            quest = self._parse_story_beat_to_quest(beat, i)
            if quest:
                quests.append(quest)
                self.add_quest(quest)
        
        # Activate the first quest
        if quests:
            self.activate_quest(quests[0].id)
            
        return quests
    
    def _parse_story_beat_to_quest(self, beat: str, index: int) -> Optional[Quest]:
        """Generate a fully dynamic quest using LLM based on story beat"""
        if not self.llm:
            return self._create_fallback_quest(beat, index)
        
        try:
            return self._generate_dynamic_quest(beat, index)
        except Exception as e:
            print(f"Failed to generate dynamic quest: {e}")
            return self._create_fallback_quest(beat, index)
    
    def _generate_dynamic_quest(self, beat: str, index: int) -> Optional[Quest]:
        """Generate a quest using LLM based on story beat context"""
        
        prompt = f"""Convert this story beat into a detailed quest with specific objectives:

STORY BEAT: "{beat}"

Create a quest that breaks down this story beat into 2-4 actionable objectives that the player can complete step by step.

Provide your response in this EXACT format:

QUEST_TITLE: [Clear, engaging quest title]
QUEST_DESCRIPTION: [Brief description of what this quest is about - 1 sentence]
OBJECTIVE_1_TYPE: [COLLECT/TRAVEL/INTERACT/SOLVE/DEFEAT/DISCOVER]
OBJECTIVE_1_DESC: [What the player needs to do - be specific]
OBJECTIVE_1_TARGET: [What they're interacting with - single word/phrase]
OBJECTIVE_1_COUNT: [Number needed - must be a digit (1, 2, 3, etc), use 1 if not applicable]
OBJECTIVE_1_HINT1: [Helpful hint for completing this objective]
OBJECTIVE_1_HINT2: [Second helpful hint]
OBJECTIVE_2_TYPE: [COLLECT/TRAVEL/INTERACT/SOLVE/DEFEAT/DISCOVER]
OBJECTIVE_2_DESC: [What the player needs to do - be specific]
OBJECTIVE_2_TARGET: [What they're interacting with - single word/phrase]
OBJECTIVE_2_COUNT: [Number needed - must be a digit (1, 2, 3, etc), use 1 if not applicable]
OBJECTIVE_2_HINT1: [Helpful hint for completing this objective]
OBJECTIVE_2_HINT2: [Second helpful hint]
[Continue with OBJECTIVE_3 and OBJECTIVE_4 if needed]

Example:
QUEST_TITLE: Infiltrate Corporate Database
QUEST_DESCRIPTION: Break into StellarCon's secure servers to steal classified data
OBJECTIVE_1_TYPE: INTERACT
OBJECTIVE_1_DESC: Access a security terminal to disable alarms
OBJECTIVE_1_TARGET: terminal
OBJECTIVE_1_COUNT: 1
OBJECTIVE_1_HINT1: Look for terminals near entrance areas
OBJECTIVE_1_HINT2: Terminals may require hacking skills
OBJECTIVE_2_TYPE: COLLECT
OBJECTIVE_2_DESC: Gather three data chips from different server rooms
OBJECTIVE_2_TARGET: data_chip
OBJECTIVE_2_COUNT: 3
OBJECTIVE_2_HINT1: Server rooms are usually well-guarded
OBJECTIVE_2_HINT2: Data chips may be hidden in server cabinets

Make objectives specific, actionable, and fitting the story beat's theme and setting."""

        try:
            # Get LLM response
            if hasattr(self.llm, 'llm'):
                response = self.llm.llm.generate_response(prompt)
            else:
                response = self.llm.generate_response(prompt)
                
            # Parse the response into a quest
            return self._parse_llm_quest_response(response, beat, index)
            
        except Exception as e:
            print(f"Error generating quest with LLM: {e}")
            return None
    
    def _parse_llm_quest_response(self, response: str, beat: str, index: int) -> Optional[Quest]:
        """Parse LLM response into a Quest object"""
        try:
            lines = response.strip().split('\n')
            quest_data = {}
            objectives_data = []
            current_obj = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().upper()
                    value = value.strip()
                    
                    if key.startswith('OBJECTIVE_') and key.endswith('_TYPE'):
                        # Start new objective
                        if current_obj:
                            objectives_data.append(current_obj)
                        obj_num = key.split('_')[1]
                        current_obj = {'num': obj_num, 'type': value}
                    elif key.startswith('OBJECTIVE_') and current_obj:
                        # Add to current objective
                        field = key.split('_', 2)[2]  # Get DESC, TARGET, COUNT, HINT1, HINT2
                        current_obj[field.lower()] = value
                    elif key in ['QUEST_TITLE', 'QUEST_DESCRIPTION']:
                        quest_data[key.lower()] = value
            
            # Add the last objective
            if current_obj:
                objectives_data.append(current_obj)
            
            # Validate required fields
            if not quest_data.get('quest_title') or not objectives_data:
                print("Missing required quest fields")
                return None
            
            # Create objectives
            objectives = []
            for obj_data in objectives_data:
                if not all(k in obj_data for k in ['type', 'desc', 'target']):
                    continue
                    
                # Map type strings to enums
                type_map = {
                    'COLLECT': ObjectiveType.COLLECT,
                    'TRAVEL': ObjectiveType.TRAVEL,
                    'INTERACT': ObjectiveType.INTERACT,
                    'SOLVE': ObjectiveType.SOLVE,
                    'DEFEAT': ObjectiveType.DEFEAT,
                    'DISCOVER': ObjectiveType.DISCOVER
                }
                
                obj_type = type_map.get(obj_data['type'], ObjectiveType.DISCOVER)
                
                # Handle count field with fallback for non-numeric values
                count_value = obj_data.get('count', '1').strip()
                try:
                    target_count = int(count_value)
                except ValueError:
                    # Handle cases where LLM returns non-numeric values like "varies", "multiple", etc.
                    target_count = 1
                
                # Collect hints
                hints = []
                for hint_key in ['hint1', 'hint2', 'hint3']:
                    if hint_key in obj_data and obj_data[hint_key]:
                        hints.append(obj_data[hint_key])
                
                objective = QuestObjective(
                    id=f"obj_{index}_{len(objectives)}",
                    description=obj_data['desc'],
                    type=obj_type,
                    target=obj_data['target'],
                    target_count=target_count,
                    hints=hints
                )
                objectives.append(objective)
            
            # Create quest
            quest = Quest(
                id=f"llm_quest_{index}",
                title=quest_data['quest_title'],
                description=quest_data.get('quest_description', beat),
                objectives=objectives,
                story_beat_index=index,
                rewards={
                    "experience": 50 + (index * 25),
                    "gold": 100 + (index * 50),
                    "items": [f"quest_reward_{index}"]
                }
            )
            
            return quest
            
        except Exception as e:
            print(f"Error parsing LLM quest response: {e}")
            return None
    
    def _create_fallback_quest(self, beat: str, index: int) -> Quest:
        """Create a simple fallback quest when LLM is unavailable"""
        # Extract quest title (usually before colon)
        if ":" in beat:
            title = beat.split(":")[0].strip("*").strip()
            description = beat.split(":", 1)[1].strip()
        else:
            title = f"Story Goal {index + 1}"
            description = beat.strip("*").strip()
        
        # Create simple fallback objective
        objective = QuestObjective(
            id=f"fallback_obj_{index}",
            description=f"Complete: {title}",
            type=ObjectiveType.DISCOVER,
            target="goal",
            hints=["Explore the area and interact with objects", "Look for clues related to your objective"]
        )
        
        quest = Quest(
            id=f"fallback_quest_{index}",
            title=title,
            description=description,
            objectives=[objective],
            story_beat_index=index,
            rewards={"experience": 25, "gold": 50}
        )
        
        return quest