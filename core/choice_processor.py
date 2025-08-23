"""
Choice Processor
Transforms player input into meaningful story choices with consequences
"""
import re
from typing import Dict, List, Any, Optional, Tuple


class ChoiceProcessor:
    """Processes player input to create meaningful narrative choices"""
    
    def __init__(self, story_engine=None, llm=None):
        self.story_engine = story_engine
        self.llm = llm
        self.choice_patterns = self._initialize_choice_patterns()
        self.context_modifiers = {
            "stealth": ["quietly", "sneakily", "stealthily", "carefully"],
            "aggressive": ["forcefully", "aggressively", "violently", "harshly"],
            "diplomatic": ["peacefully", "diplomatically", "politely", "respectfully"],
            "cunning": ["cleverly", "cunningly", "trickily", "deceptively"]
        }
        
    def _initialize_choice_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns that identify meaningful choices"""
        return {
            "moral_choices": [
                r"(help|save|protect|heal|give|share|donate)",
                r"(attack|kill|harm|hurt|steal|rob|betray)",
                r"(lie|deceive|cheat|trick|manipulate)"
            ],
            "social_choices": [
                r"(talk to|speak with|negotiate|persuade|threaten)",
                r"(befriend|ally with|trust|follow)",
                r"(challenge|confront|accuse|demand)"
            ],
            "exploration_choices": [
                r"(explore|investigate|search|examine|study)",
                r"(enter|go into|venture|proceed|advance)",
                r"(retreat|flee|escape|avoid|hide)"
            ],
            "resource_choices": [
                r"(take|get|grab|collect|gather)",
                r"(use|consume|spend|sacrifice)",
                r"(save|preserve|hoard|keep)"
            ]
        }
    
    def analyze_player_input(self, user_input: str, context: Dict) -> Dict[str, Any]:
        """Analyze player input for choice significance and consequences"""
        input_lower = user_input.lower().strip()
        
        # Determine if this is a significant choice
        choice_significance = self._assess_choice_significance(input_lower, context)
        
        if choice_significance["is_significant"]:
            return self._process_significant_choice(user_input, context, choice_significance)
        else:
            return self._process_routine_action(user_input, context)
    
    def _assess_choice_significance(self, input_text: str, context: Dict) -> Dict[str, Any]:
        """Assess whether player input represents a significant choice"""
        significance = {"is_significant": False, "type": "routine", "weight": 0}
        
        # Check for moral implications
        moral_patterns = self.choice_patterns["moral_choices"]
        for pattern in moral_patterns:
            if re.search(pattern, input_text):
                significance["is_significant"] = True
                significance["type"] = "moral"
                significance["weight"] = 3
                break
        
        # Check for social implications
        social_patterns = self.choice_patterns["social_choices"]
        for pattern in social_patterns:
            if re.search(pattern, input_text):
                significance["is_significant"] = True
                significance["type"] = "social"
                significance["weight"] = 2
                break
        
        # Check context for significance boosters
        if context.get("npcs") and significance["weight"] > 0:
            significance["weight"] += 1  # Choices with NPCs present are more significant
        
        if context.get("combat_possible"):
            significance["weight"] += 1  # Combat situations increase significance
        
        if context.get("story_moment"):
            significance["weight"] += 2  # Story moments are always significant
        
        return significance
    
    def _process_significant_choice(self, user_input: str, context: Dict, significance: Dict) -> Dict[str, Any]:
        """Process a significant player choice"""
        if not self.story_engine:
            return {"type": "routine", "processed_input": user_input}
        
        # Enhance the choice with context and style modifiers
        enhanced_choice = self._enhance_choice_description(user_input, context)
        
        # Process through story engine
        choice_result = self.story_engine.process_player_choice(enhanced_choice, context)
        
        return {
            "type": "significant_choice",
            "original_input": user_input,
            "enhanced_choice": enhanced_choice,
            "significance": significance,
            "story_result": choice_result,
            "narrative_response": choice_result.get("narrative", ""),
            "consequences": choice_result.get("immediate_consequences", []),
            "future_implications": choice_result.get("delayed_consequences", [])
        }
    
    def _process_routine_action(self, user_input: str, context: Dict) -> Dict[str, Any]:
        """Process routine actions that might still generate story content"""
        return {
            "type": "routine",
            "processed_input": user_input,
            "context_aware_response": self._generate_context_aware_response(user_input, context)
        }
    
    def _enhance_choice_description(self, user_input: str, context: Dict) -> str:
        """Enhance choice description with context and style"""
        enhanced = user_input
        
        # Add context modifiers based on situation
        if context.get("stealth_required"):
            enhanced = f"carefully {enhanced}"
        elif context.get("time_pressure"):
            enhanced = f"quickly {enhanced}"
        elif context.get("dangerous_situation"):
            enhanced = f"boldly {enhanced}"
        
        # Add emotional context
        if context.get("npc_relationship") == "hostile":
            enhanced = f"{enhanced} despite the danger"
        elif context.get("npc_relationship") == "friendly":
            enhanced = f"{enhanced} with trust"
        
        return enhanced
    
    def _generate_context_aware_response(self, user_input: str, context: Dict) -> Optional[str]:
        """Generate context-aware response for routine actions"""
        if not self.llm:
            return None
        
        # Only generate responses for interesting routine actions
        if not any(word in user_input.lower() for word in ["examine", "look", "search", "listen"]):
            return None
        
        prompt = f"""The player performs this routine action: "{user_input}"

Context:
- Location: {context.get('location', 'unknown area')}
- Theme: {context.get('theme', 'fantasy')}
- NPCs present: {', '.join(context.get('npcs', []))}
- Mood: {context.get('mood', 'neutral')}
- Time of day: {context.get('time', 'unknown')}

Generate a brief, atmospheric response (1-2 sentences) that:
1. Describes what they notice/discover
2. Adds flavor without major consequences
3. Maintains immersion and mood
4. Might hint at deeper mysteries

Keep it concise and evocative."""
        
        try:
            return self.llm.generate_response(prompt).strip()
        except:
            return None
    
    def suggest_meaningful_choices(self, context: Dict) -> List[str]:
        """Suggest meaningful choices based on current context"""
        suggestions = []
        
        # Based on NPCs present
        if context.get("npcs"):
            for npc in context["npcs"]:
                suggestions.extend([
                    f"talk to {npc}",
                    f"ask {npc} about the situation",
                    f"offer to help {npc}"
                ])
        
        # Based on items/environment
        if context.get("items"):
            for item in context.get("items", [])[:3]:  # Limit to 3 items
                suggestions.extend([
                    f"examine {item}",
                    f"take {item}",
                    f"use {item}"
                ])
        
        # Based on story tension
        tension = context.get("world_tension", 0)
        if tension > 50:
            suggestions.extend([
                "proceed cautiously",
                "investigate the danger",
                "find another route"
            ])
        
        # Based on moral alignment opportunity
        if context.get("moral_choice_available"):
            suggestions.extend([
                "do the right thing",
                "take the practical approach", 
                "look for a creative solution"
            ])
        
        return suggestions[:6]  # Limit to 6 suggestions
    
    def create_choice_prompt(self, context: Dict, suggestions: List[str]) -> str:
        """Create a choice prompt for the player"""
        base_prompt = "> "
        
        if not suggestions:
            return base_prompt
        
        # Add tension indicator
        tension = context.get("world_tension", 0)
        if tension > 70:
            tension_indicator = "⚡"
        elif tension > 40:
            tension_indicator = "⚠️"
        else:
            tension_indicator = ""
        
        # Format suggestions
        suggestion_text = " | ".join(suggestions)
        
        return f"{tension_indicator}What do you do? [{suggestion_text}]\n{base_prompt}"
    
    def handle_ambiguous_input(self, user_input: str, context: Dict) -> Dict[str, Any]:
        """Handle ambiguous input by asking for clarification"""
        if not self.llm:
            return {
                "type": "clarification_needed",
                "message": "Could you be more specific about what you want to do?"
            }
        
        prompt = f"""The player said: "{user_input}"

Context: {context.get('situation', 'general situation')}
Available options: {', '.join(context.get('available_actions', []))}

This input is ambiguous. Generate a helpful clarification question that:
1. Acknowledges what they might want to do
2. Offers 2-3 specific options
3. Maintains immersion and story flow

Format as a question with options."""
        
        try:
            clarification = self.llm.generate_response(prompt)
            return {
                "type": "clarification_needed", 
                "message": clarification.strip()
            }
        except:
            return {
                "type": "clarification_needed",
                "message": f"I understand you want to {user_input}, but could you be more specific about how?"
            }
    
    def extract_choice_intent(self, user_input: str) -> Dict[str, Any]:
        """Extract the intent and style from player choice"""
        input_lower = user_input.lower()
        
        intent = {
            "action": "unknown",
            "target": None,
            "style": "direct",
            "intensity": "moderate"
        }
        
        # Extract action
        action_patterns = {
            "help": r"(help|assist|aid|support|save)",
            "attack": r"(attack|fight|hit|strike|kill)",
            "talk": r"(talk|speak|say|tell|ask|discuss)",
            "take": r"(take|get|grab|pick up|collect)",
            "examine": r"(examine|look at|inspect|study|check)",
            "go": r"(go|move|travel|walk|run|head)"
        }
        
        for action, pattern in action_patterns.items():
            if re.search(pattern, input_lower):
                intent["action"] = action
                break
        
        # Extract target
        target_match = re.search(r"(?:to|at|with|on)\s+(\w+(?:\s+\w+)*)", input_lower)
        if target_match:
            intent["target"] = target_match.group(1)
        
        # Extract style modifiers
        if any(word in input_lower for word in ["quietly", "carefully", "stealthily"]):
            intent["style"] = "stealth"
        elif any(word in input_lower for word in ["aggressively", "forcefully", "violently"]):
            intent["style"] = "aggressive"
        elif any(word in input_lower for word in ["diplomatically", "politely", "peacefully"]):
            intent["style"] = "diplomatic"
        
        # Extract intensity
        if any(word in input_lower for word in ["really", "very", "extremely", "completely"]):
            intent["intensity"] = "high"
        elif any(word in input_lower for word in ["slightly", "gently", "barely", "somewhat"]):
            intent["intensity"] = "low"
        
        return intent