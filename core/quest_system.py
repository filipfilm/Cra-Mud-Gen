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
    
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.active_quests: List[str] = []  # Quest IDs that are currently active
        self.completed_quests: List[str] = []
        
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
        """Parse a story beat into a quest with objectives"""
        beat_lower = beat.lower()
        
        # Extract quest title (usually before colon)
        if ":" in beat:
            title = beat.split(":")[0].strip("*").strip()
            description = beat.split(":", 1)[1].strip()
        else:
            title = f"Story Goal {index + 1}"
            description = beat.strip("*").strip()
        
        quest = Quest(
            id=f"story_quest_{index}",
            title=title,
            description=description,
            story_beat_index=index
        )
        
        # Parse objectives based on keywords
        objectives = []
        
        if "find" in beat_lower or "locate" in beat_lower:
            if "entrance" in beat_lower or "door" in beat_lower:
                objectives.append(QuestObjective(
                    id=f"find_entrance_{index}",
                    description="Find the hidden entrance",
                    type=ObjectiveType.DISCOVER,
                    target="entrance",
                    hints=["Look for celestial symbols or hidden mechanisms"]
                ))
            elif "crystals" in beat_lower or "crystal" in beat_lower:
                objectives.append(QuestObjective(
                    id=f"collect_crystals_{index}",
                    description="Collect luminescent crystals",
                    type=ObjectiveType.COLLECT,
                    target="crystal",
                    target_count=5,
                    hints=["Crystals may be scattered throughout the cavern"]
                ))
        
        if "solve" in beat_lower and "puzzle" in beat_lower:
            objectives.append(QuestObjective(
                id=f"solve_puzzle_{index}",
                description="Solve the celestial puzzle",
                type=ObjectiveType.SOLVE,
                target="puzzle",
                hints=["Study the constellation patterns on the wall"]
            ))
        
        if "unlock" in beat_lower or "open" in beat_lower:
            if "chamber" in beat_lower:
                objectives.append(QuestObjective(
                    id=f"unlock_chamber_{index}",
                    description="Unlock the Starlight Chamber",
                    type=ObjectiveType.INTERACT,
                    target="chamber",
                    hints=["Listen for musical notes from wind chimes"]
                ))
        
        if "activate" in beat_lower:
            if "map" in beat_lower:
                objectives.append(QuestObjective(
                    id=f"activate_map_{index}",
                    description="Activate the celestial map",
                    type=ObjectiveType.INTERACT,
                    target="map",
                    hints=["Align the map with current night sky patterns"]
                ))
        
        if "claim" in beat_lower or "retrieve" in beat_lower:
            if "orb" in beat_lower:
                objectives.append(QuestObjective(
                    id=f"claim_orb_{index}",
                    description="Claim the Starlight Orb",
                    type=ObjectiveType.COLLECT,
                    target="orb",
                    hints=["Escape before protective wards reset"]
                ))
        
        # Default objective if no specific ones found
        if not objectives:
            objectives.append(QuestObjective(
                id=f"complete_goal_{index}",
                description=title,
                type=ObjectiveType.DISCOVER,
                target="goal"
            ))
        
        quest.objectives = objectives
        return quest