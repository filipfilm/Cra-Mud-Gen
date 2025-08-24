"""
Dynamic Content Generator
Uses LLM to generate room contents, NPCs, and items on-the-fly
"""
import random
import re
from typing import List, Dict, Any, Optional, Tuple


class DynamicContentGenerator:
    """Generates dynamic room content using LLM"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.generated_items = {}  # Cache for consistency
        self.generated_npcs = {}   # Cache for NPC personalities
    
    def generate_room_contents(self, room_description: str, theme: str, depth: int, narrative_context: Dict = None) -> Dict[str, Any]:
        """Generate items and NPCs for a room using LLM with optional narrative context"""
        if not self.llm:
            return self._fallback_generation(room_description, theme, depth, narrative_context)
        
        # Create LLM prompt for room contents
        prompt = self._create_content_prompt(room_description, theme, depth, narrative_context)
        
        try:
            response = self.llm.generate_response(prompt)
            return self._parse_llm_response(response, theme)
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._fallback_generation(room_description, theme, depth, narrative_context)
    
    def _create_content_prompt(self, room_description: str, theme: str, depth: int, narrative_context: Dict = None) -> str:
        """Create prompt for LLM room content generation with narrative context"""
        
        # Adjust content based on depth
        if depth <= 3:
            complexity = "simple, basic"
            item_rarity = "common"
        elif depth <= 10:
            complexity = "moderate"
            item_rarity = "some uncommon"
        else:
            complexity = "complex, dangerous"
            item_rarity = "rare and magical"
        
        # Add narrative context if available
        narrative_info = ""
        if narrative_context:
            narrative_info = f"""
STORY CONTEXT:
- Setting: {narrative_context.get('setting', 'Unknown')}
- Main Conflict: {narrative_context.get('conflict', 'Unknown')}
- Mood: {narrative_context.get('mood', 'Neutral')}
- Danger Level: {narrative_context.get('danger_level', 5)}/10
- Mystery Level: {narrative_context.get('mystery_level', 5)}/10
- Current Story Beat: {narrative_context.get('current_beat', 'None')}
"""

        prompt = f"""You are generating content for a {theme} dungeon room at depth {depth}.

ROOM DESCRIPTION: {room_description}{narrative_info}

Generate appropriate items and NPCs for this room. The content should be {complexity} with {item_rarity} items.
{narrative_context and "Consider the story context when selecting items and NPCs - they should reflect the narrative mood, danger level, and current story beat." or ""}

Format your response EXACTLY like this:
ITEMS: item1, item2, item3
NPCS: npc_name (occupation/role), another_npc (role)
ITEM_DESCRIPTIONS:
- item1: brief description
- item2: brief description  
NPC_PROFILES:
- npc_name: personality_trait1, personality_trait2, personality_trait3 | speech_style | brief_background

Rules:
- Items should fit the room and theme
- 1-4 items per room (fewer at low depths)
- 0-1 NPCs per room (30% chance)
- Keep descriptions concise but atmospheric
- Items can be weapons, armor, potions, tools, treasures, or magical items
- NPCs can be merchants, guards, wizards, priests, etc.

For NPC_PROFILES:
- List 3 personality traits (e.g., gruff, wise, cautious)
- Speech style: gruff, mystical, formal, casual, or normal
- One sentence background/motivation
- The NPC will use LLM to respond naturally as this character

Example for a fantasy cavern:
ITEMS: rusted pickaxe, silver nugget, miner's lamp
NPCS: Old Pete (prospector)
ITEM_DESCRIPTIONS:
- rusted pickaxe: A well-used mining tool, handle worn smooth by years of labor
- silver nugget: A small chunk of precious metal, gleaming in the torch light
- miner's lamp: An oil-burning lantern designed for underground exploration
NPC_PROFILES:
- Old Pete: gruff, experienced, lonely | gruff | An old miner who has spent decades working these tunnels alone, searching for silver veins.
"""
        
        return prompt
    
    def _parse_llm_response(self, response: str, theme: str) -> Dict[str, Any]:
        """Parse LLM response into structured content"""
        content = {
            "items": [],
            "npcs": [],
            "item_descriptions": {},
            "npc_dialogues": {}
        }
        
        lines = response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('ITEMS:'):
                items_text = line.replace('ITEMS:', '').strip()
                content["items"] = [item.strip() for item in items_text.split(',') if item.strip()]
                current_section = "items"
                
            elif line.startswith('NPCS:'):
                npcs_text = line.replace('NPCS:', '').strip()
                if npcs_text:
                    # Parse NPCs with roles: "npc_name (role)"
                    npc_matches = re.findall(r'([^(]+)\s*\(([^)]+)\)', npcs_text)
                    for name, role in npc_matches:
                        content["npcs"].append({
                            "name": name.strip(),
                            "role": role.strip()
                        })
                current_section = "npcs"
                
            elif line.startswith('ITEM_DESCRIPTIONS:'):
                current_section = "item_descriptions"
                
            elif line.startswith('NPC_PROFILES:'):
                current_section = "npc_profiles"
                
            elif current_section == "item_descriptions" and line.startswith('-'):
                # Parse "- item: description"
                match = re.match(r'-\s*([^:]+):\s*(.+)', line)
                if match:
                    item_name, description = match.groups()
                    content["item_descriptions"][item_name.strip()] = description.strip()
                    
            elif current_section == "npc_profiles" and line.startswith('-'):
                # Parse "- npc_name: trait1, trait2, trait3 | speech_style | background"
                match = re.match(r'-\s*([^:]+):\s*(.+)', line)
                if match:
                    npc_name, profile_text = match.groups()
                    profile_parts = profile_text.split('|')
                    
                    if len(profile_parts) >= 3:
                        traits = [t.strip() for t in profile_parts[0].split(',')]
                        speech_style = profile_parts[1].strip()
                        background = profile_parts[2].strip()
                        
                        content["npc_dialogues"][npc_name.strip()] = {
                            "personality_traits": traits,
                            "speech_pattern": speech_style,
                            "background": background,
                            "greeting": f"*looks up* Greetings, traveler.",
                            "farewell": "Safe travels, friend."
                        }
        
        return content
    
    def _fallback_generation(self, room_description: str, theme: str, depth: int, narrative_context: Dict = None) -> Dict[str, Any]:
        """Fallback content generation when LLM fails"""
        content = {
            "items": [],
            "npcs": [],
            "item_descriptions": {},
            "npc_dialogues": {}
        }
        
        # Simple item generation
        theme_items = {
            "fantasy": ["sword", "shield", "potion", "scroll", "gem", "coin purse", "torch", "dagger"],
            "sci-fi": ["data pad", "energy cell", "laser pistol", "scanner", "med kit", "oxygen tank"],
            "horror": ["old key", "torn journal", "candle", "cursed amulet", "bone fragment"],
            "cyberpunk": ["credit chip", "neural interface", "holo-display", "encrypted drive"]
        }
        
        items = theme_items.get(theme, theme_items["fantasy"])
        num_items = min(4, max(1, depth // 3 + random.randint(0, 2)))
        content["items"] = random.sample(items, min(num_items, len(items)))
        
        # Simple descriptions
        for item in content["items"]:
            content["item_descriptions"][item] = f"A {item} that looks useful for your adventure."
        
        # Occasional NPC
        if random.random() < 0.3:
            theme_npcs = {
                "fantasy": [("Guard Captain", "warrior"), ("Wise Sage", "scholar"), ("Traveling Merchant", "trader")],
                "sci-fi": [("Security Officer", "guard"), ("Tech Specialist", "engineer")],
                "horror": [("Mad Survivor", "survivor"), ("Cultist", "fanatic")],
                "cyberpunk": [("Data Broker", "hacker"), ("Corp Security", "guard")]
            }
            
            npcs = theme_npcs.get(theme, theme_npcs["fantasy"])
            if npcs:
                npc_name, npc_role = random.choice(npcs)
                content["npcs"] = [{"name": npc_name, "role": npc_role}]
                content["npc_dialogues"][npc_name] = {
                    "personality_traits": ["helpful", "experienced", "cautious"],
                    "speech_pattern": "normal",
                    "background": f"A {npc_role} who knows these lands well.",
                    "greeting": f"*nods* Greetings, traveler.",
                    "farewell": "May your path be safe, traveler."
                }
        
        return content
    
    def get_item_description(self, item_name: str, theme: str) -> str:
        """Get detailed description of an item"""
        if item_name in self.generated_items:
            return self.generated_items[item_name]
        
        if not self.llm:
            return f"A {item_name} that could be useful on your adventure."
        
        prompt = f"""Describe this {theme} item in detail: {item_name}

Write a vivid, atmospheric description (2-3 sentences) that includes:
- Physical appearance
- Apparent function or power
- How it feels/looks/smells

Keep it immersive and thematic for {theme} setting."""
        
        try:
            description = self.llm.generate_response(prompt)
            self.generated_items[item_name] = description.strip()
            return description.strip()
        except:
            fallback = f"A {item_name} that appears to be of {theme} origin, well-crafted and potentially valuable."
            self.generated_items[item_name] = fallback
            return fallback
    
    def create_dynamic_npc_conversation(self, npc_name: str, npc_role: str, theme: str, narrative_context: Dict = None) -> Dict[str, Any]:
        """Create a conversation personality for a dynamically generated NPC"""
        if npc_name in self.generated_npcs:
            return self.generated_npcs[npc_name]
        
        if not self.llm:
            return self._fallback_npc_personality(npc_name, npc_role, theme)
        
        # Add narrative context for NPC personality
        narrative_info = ""
        if narrative_context:
            narrative_info = f"""
            
STORY CONTEXT:
- Setting: {narrative_context.get('setting', 'Unknown')}
- Main Conflict: {narrative_context.get('conflict', 'Unknown')}
- Mood: {narrative_context.get('mood', 'Neutral')}
- Current Story Beat: {narrative_context.get('current_beat', 'None')}

The NPC should be aware of and reference these story elements in their dialogue."""

        # Build the prompt with proper string handling
        context_addition = " Their dialogue should reflect the current story context and mood." if narrative_context else ""
        
        prompt = f"""Create a conversation personality for: {npc_name} ({npc_role}) in a {theme} setting.{narrative_info}

Generate responses for these topics (keep each response 1-2 sentences, in character):
- greeting (how they first address the player)
- farewell (how they say goodbye)  
- help (offering assistance)
- information (sharing knowledge)
- trade (if applicable to their role)
- quest (if they might have tasks)

Format like this:
GREETING: character greeting message
FAREWELL: character farewell message  
HELP: response about helping
INFORMATION: response about sharing knowledge
TRADE: response about trading (or "N/A" if not applicable)
QUEST: response about quests (or "N/A" if not applicable)
PERSONALITY: brief description of their speaking style/personality

Make them feel authentic to their role and the {theme} theme.{context_addition}"""
        
        try:
            response = self.llm.generate_response(prompt)
            personality = self._parse_npc_personality(response)
            self.generated_npcs[npc_name] = personality
            return personality
        except:
            return self._fallback_npc_personality(npc_name, npc_role, theme)
    
    def _parse_npc_personality(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into NPC personality"""
        personality = {
            "greeting": "*nods* Hello there.",
            "farewell": "Farewell, traveler.",
            "topics": {},
            "personality": "friendly"
        }
        
        lines = response.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().upper()
                value = value.strip()
                
                if key == "GREETING":
                    personality["greeting"] = value
                elif key == "FAREWELL":
                    personality["farewell"] = value
                elif key == "PERSONALITY":
                    personality["personality"] = value
                elif value and value != "N/A":
                    personality["topics"][key.lower()] = value
        
        return personality
    
    def _fallback_npc_personality(self, npc_name: str, npc_role: str, theme: str) -> Dict[str, Any]:
        """Fallback NPC personality when LLM fails"""
        return {
            "greeting": f"*{npc_role} looks up* Greetings, adventurer.",
            "farewell": "May your journey be safe.",
            "topics": {
                "help": "I do what I can to assist travelers.",
                "information": f"As a {npc_role}, I know these parts well."
            },
            "personality": "helpful"
        }