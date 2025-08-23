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
    
    def generate_room_contents(self, room_description: str, theme: str, depth: int) -> Dict[str, Any]:
        """Generate items and NPCs for a room using LLM"""
        if not self.llm:
            return self._fallback_generation(room_description, theme, depth)
        
        # Create LLM prompt for room contents
        prompt = self._create_content_prompt(room_description, theme, depth)
        
        try:
            response = self.llm.generate_response(prompt)
            return self._parse_llm_response(response, theme)
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._fallback_generation(room_description, theme, depth)
    
    def _create_content_prompt(self, room_description: str, theme: str, depth: int) -> str:
        """Create prompt for LLM room content generation"""
        
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
        
        prompt = f"""You are generating content for a {theme} dungeon room at depth {depth}.

ROOM DESCRIPTION: {room_description}

Generate appropriate items and NPCs for this room. The content should be {complexity} with {item_rarity} items.

Format your response EXACTLY like this:
ITEMS: item1, item2, item3
NPCS: npc_name (occupation/role), another_npc (role)
ITEM_DESCRIPTIONS:
- item1: brief description
- item2: brief description  
DIALOGUES:
- npc_name: greeting_message | topic1:response1 | topic2:response2

Rules:
- Items should fit the room and theme
- 1-4 items per room (fewer at low depths)
- 0-1 NPCs per room (30% chance)
- NPCs should have personality matching theme
- Keep descriptions concise but atmospheric
- Items can be weapons, armor, potions, tools, treasures, or magical items
- NPCs can be merchants, guards, wizards, priests, etc.

Example for a fantasy armory:
ITEMS: enchanted sword, chainmail armor, shield of valor
NPCS: Master Blacksmith (weaponsmith)
ITEM_DESCRIPTIONS:
- enchanted sword: A blade that glows with inner light, perfectly balanced
- chainmail armor: Well-crafted rings of steel, still gleaming
- shield of valor: A sturdy shield bearing ancient heraldry
DIALOGUES:  
- Master Blacksmith: *looks up from anvil* Need something forged? | weapons:I craft the finest blades in the realm! | armor:Protection is as important as offense, friend.
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
                
            elif line.startswith('DIALOGUES:'):
                current_section = "dialogues"
                
            elif current_section == "item_descriptions" and line.startswith('-'):
                # Parse "- item: description"
                match = re.match(r'-\s*([^:]+):\s*(.+)', line)
                if match:
                    item_name, description = match.groups()
                    content["item_descriptions"][item_name.strip()] = description.strip()
                    
            elif current_section == "dialogues" and line.startswith('-'):
                # Parse "- npc_name: greeting | topic:response | topic:response"
                match = re.match(r'-\s*([^:]+):\s*(.+)', line)
                if match:
                    npc_name, dialogue_text = match.groups()
                    dialogue_parts = dialogue_text.split('|')
                    
                    if dialogue_parts:
                        greeting = dialogue_parts[0].strip()
                        topics = {}
                        
                        for part in dialogue_parts[1:]:
                            if ':' in part:
                                topic, response = part.split(':', 1)
                                topics[topic.strip()] = response.strip()
                        
                        content["npc_dialogues"][npc_name.strip()] = {
                            "greeting": greeting,
                            "topics": topics
                        }
        
        return content
    
    def _fallback_generation(self, room_description: str, theme: str, depth: int) -> Dict[str, Any]:
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
                    "greeting": f"*nods* Greetings, traveler.",
                    "topics": {
                        "help": "I might be able to assist you.",
                        "information": "I know a few things about these parts."
                    }
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
    
    def create_dynamic_npc_conversation(self, npc_name: str, npc_role: str, theme: str) -> Dict[str, Any]:
        """Create a conversation personality for a dynamically generated NPC"""
        if npc_name in self.generated_npcs:
            return self.generated_npcs[npc_name]
        
        if not self.llm:
            return self._fallback_npc_personality(npc_name, npc_role, theme)
        
        prompt = f"""Create a conversation personality for: {npc_name} ({npc_role}) in a {theme} setting.

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

Make them feel authentic to their role and the {theme} theme."""
        
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