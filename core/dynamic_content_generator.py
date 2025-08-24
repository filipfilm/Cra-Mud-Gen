"""
Dynamic Content Generator
Uses LLM to generate room contents, NPCs, and items on-the-fly
"""
import random
import re
from typing import List, Dict, Any, Optional, Tuple
from core.llm_name_engine import LLMNameEngine


class DynamicContentGenerator:
    """Generates dynamic room content using LLM"""
    
    def __init__(self, llm=None, fallback_mode=False):
        self.llm = llm
        self.generated_items = {}  # Cache for consistency
        self.generated_npcs = {}   # Cache for NPC personalities
        self.name_generator = LLMNameEngine(llm=llm, fallback_mode=fallback_mode)
        self.fallback_mode = fallback_mode
    
    def generate_room_contents(self, room_description: str, theme: str, depth: int, narrative_context: Dict = None) -> Dict[str, Any]:
        """Generate items and NPCs for a room using LLM with optional narrative context"""
        if not self.llm:
            if self.fallback_mode:
                return self._fallback_generation(room_description, theme, depth, narrative_context)
            else:
                raise RuntimeError("LLM is required for room content generation (fallback mode disabled)")
        
        # Create LLM prompt for room contents
        prompt = self._create_content_prompt(room_description, theme, depth, narrative_context)
        
        try:
            response = self.llm.generate_response(prompt)
            return self._parse_llm_response(response, theme)
        except Exception as e:
            print(f"LLM generation failed: {e}")
            if self.fallback_mode:
                return self._fallback_generation(room_description, theme, depth, narrative_context)
            else:
                raise RuntimeError(f"LLM generation failed and fallback mode disabled: {e}")
    
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
        
        # Generate dynamic items
        item_types = {
            "fantasy": ["weapon", "armor", "potion", "scroll"],
            "sci-fi": ["tech", "weapon", "armor", "consumable"],
            "horror": ["artifact", "weapon", "consumable"],
            "cyberpunk": ["tech", "software", "weapon"]
        }
        
        available_types = item_types.get(theme, item_types["fantasy"])
        num_items = min(4, max(1, depth // 3 + random.randint(0, 2)))
        
        # Generate unique item names
        content["items"] = []
        for _ in range(num_items):
            item_type = random.choice(available_types)
            rarity = "common" if depth < 5 else "uncommon" if depth < 10 else "rare"
            item_name = self.name_generator.generate_item_name(item_type, theme, rarity)
            content["items"].append(item_name)
        
        # Simple descriptions
        for item in content["items"]:
            content["item_descriptions"][item] = f"A {item} that looks useful for your adventure."
        
        # Occasional NPC - now dynamically generated
        if random.random() < 0.3:
            # Define roles by theme
            theme_roles = {
                "fantasy": ["warrior", "guard", "scholar", "trader", "priest", "healer", "blacksmith", "wizard"],
                "sci-fi": ["guard", "engineer", "scientist", "pilot", "medic", "hacker", "operative"],
                "horror": ["survivor", "cultist", "priest", "doctor", "scholar"],
                "cyberpunk": ["hacker", "guard", "executive", "engineer", "runner", "operative"]
            }
            
            roles = theme_roles.get(theme, theme_roles["fantasy"])
            npc_role = random.choice(roles)
            
            # Generate dynamic name
            npc_name = self.name_generator.generate_dynamic_name(theme, npc_role, "full")
            
            content["npcs"] = [{"name": npc_name, "role": npc_role}]
            
            # Generate dynamic personality traits
            personality_traits = self._generate_personality_traits(theme, npc_role)
            speech_pattern = self._get_speech_pattern(theme, npc_role)
            
            content["npc_dialogues"][npc_name] = {
                "personality_traits": personality_traits,
                "speech_pattern": speech_pattern,
                "background": f"A {npc_role} who has made these {self._get_area_descriptor(theme)} their domain.",
                "greeting": self._generate_dynamic_greeting(npc_name, npc_role, theme),
                "farewell": self._generate_dynamic_farewell(npc_role, theme)
            }
        
        return content
    
    def get_item_description(self, item_name: str, theme: str) -> str:
        """Get detailed description of an item"""
        if item_name in self.generated_items:
            return self.generated_items[item_name]
        
        if not self.llm:
            if self.fallback_mode:
                return f"A {item_name} that could be useful on your adventure."
            else:
                raise RuntimeError("LLM is required for item descriptions (fallback mode disabled)")
        
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
        except Exception as e:
            if self.fallback_mode:
                fallback = f"A {item_name} that appears to be of {theme} origin, well-crafted and potentially valuable."
                self.generated_items[item_name] = fallback
                return fallback
            else:
                raise RuntimeError(f"LLM item description failed and fallback mode disabled: {e}")
    
    def create_dynamic_npc_conversation(self, npc_name: str, npc_role: str, theme: str, narrative_context: Dict = None) -> Dict[str, Any]:
        """Create a conversation personality for a dynamically generated NPC"""
        if npc_name in self.generated_npcs:
            return self.generated_npcs[npc_name]
        
        if not self.llm:
            if self.fallback_mode:
                return self._fallback_npc_personality(npc_name, npc_role, theme)
            else:
                raise RuntimeError("LLM is required for NPC conversation creation (fallback mode disabled)")
        
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
        except Exception as e:
            if self.fallback_mode:
                return self._fallback_npc_personality(npc_name, npc_role, theme)
            else:
                raise RuntimeError(f"LLM NPC conversation creation failed and fallback mode disabled: {e}")
    
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
    
    def _generate_personality_traits(self, theme: str, role: str) -> List[str]:
        """Generate dynamic personality traits based on theme and role"""
        base_traits = {
            "fantasy": {
                "warrior": ["brave", "honorable", "protective", "disciplined"],
                "guard": ["vigilant", "duty-bound", "suspicious", "loyal"],
                "scholar": ["wise", "curious", "methodical", "patient"],
                "trader": ["shrewd", "friendly", "opportunistic", "traveled"],
                "priest": ["devout", "compassionate", "wise", "solemn"],
                "healer": ["caring", "gentle", "knowledgeable", "empathetic"],
                "blacksmith": ["skilled", "honest", "hardworking", "gruff"],
                "wizard": ["mysterious", "powerful", "eccentric", "learned"]
            },
            "sci-fi": {
                "guard": ["alert", "professional", "trained", "suspicious"],
                "engineer": ["technical", "precise", "innovative", "logical"],
                "scientist": ["analytical", "curious", "methodical", "intellectual"],
                "pilot": ["confident", "skilled", "adventurous", "quick-thinking"],
                "medic": ["caring", "precise", "calm", "knowledgeable"],
                "hacker": ["clever", "rebellious", "secretive", "tech-savvy"],
                "operative": ["stealthy", "professional", "cautious", "trained"]
            },
            "horror": {
                "survivor": ["traumatized", "cautious", "resilient", "paranoid"],
                "cultist": ["fanatical", "secretive", "unhinged", "devoted"],
                "priest": ["fearful", "faithful", "protective", "haunted"],
                "doctor": ["knowledgeable", "disturbed", "obsessive", "clinical"],
                "scholar": ["obsessed", "knowledgeable", "reclusive", "haunted"]
            },
            "cyberpunk": {
                "hacker": ["rebellious", "tech-savvy", "paranoid", "clever"],
                "guard": ["corporate", "professional", "suspicious", "armed"],
                "executive": ["ambitious", "ruthless", "polished", "calculating"],
                "engineer": ["technical", "innovative", "underground", "skilled"],
                "runner": ["fast", "streetwise", "independent", "risky"],
                "operative": ["professional", "discrete", "dangerous", "connected"]
            }
        }
        
        role_traits = base_traits.get(theme, base_traits["fantasy"]).get(role, ["experienced", "cautious", "helpful"])
        
        # Add some randomness - pick 3-4 traits from the pool
        selected_traits = random.sample(role_traits, min(len(role_traits), random.randint(3, 4)))
        
        # Occasionally add a contrasting trait for depth
        if random.random() < 0.3:
            contrasting_traits = ["quirky", "secretive", "humorous", "melancholy", "optimistic", "cynical"]
            selected_traits.append(random.choice(contrasting_traits))
        
        return selected_traits
    
    def _get_speech_pattern(self, theme: str, role: str) -> str:
        """Get speech pattern for NPC based on theme and role"""
        speech_patterns = {
            "fantasy": {
                "warrior": "honorable",
                "guard": "formal",
                "scholar": "eloquent",
                "trader": "friendly",
                "priest": "solemn",
                "healer": "gentle",
                "blacksmith": "gruff",
                "wizard": "mystical"
            },
            "sci-fi": {
                "guard": "military",
                "engineer": "technical",
                "scientist": "analytical",
                "pilot": "casual",
                "medic": "professional",
                "hacker": "slang",
                "operative": "clipped"
            },
            "horror": {
                "survivor": "nervous",
                "cultist": "fanatical",
                "priest": "fearful",
                "doctor": "clinical",
                "scholar": "obsessive"
            },
            "cyberpunk": {
                "hacker": "street",
                "guard": "corporate",
                "executive": "polished",
                "engineer": "technical",
                "runner": "fast",
                "operative": "professional"
            }
        }
        
        return speech_patterns.get(theme, speech_patterns["fantasy"]).get(role, "normal")
    
    def _get_area_descriptor(self, theme: str) -> str:
        """Get area descriptor for NPC background"""
        descriptors = {
            "fantasy": "ancient halls",
            "sci-fi": "technological corridors",
            "horror": "cursed chambers", 
            "cyberpunk": "neon-lit passages"
        }
        return descriptors.get(theme, "mysterious passages")
    
    def _generate_dynamic_greeting(self, name: str, role: str, theme: str) -> str:
        """Generate dynamic greeting based on NPC characteristics"""
        greeting_templates = {
            "fantasy": {
                "warrior": ["*straightens armor* Well met, traveler!", "*nods respectfully* Greetings, wanderer.", "*salutes* Hail and well met!"],
                "guard": ["*eyes you warily* State your business here.", "*stands at attention* What brings you to these halls?", "Halt! Who goes there?"],
                "scholar": ["*looks up from studies* Ah, a visitor! How fascinating.", "*adjusts spectacles* Welcome, seeker of knowledge.", "*marks place in tome* Greetings, traveler."],
                "trader": ["*rubs hands together* Ah, a customer! Welcome!", "*smiles broadly* Come, come! See what wares I have!", "*waves enthusiastically* Greetings, friend! Looking to trade?"],
                "priest": ["*bows head* May the light guide you, child.", "*makes sacred gesture* Blessings upon you, traveler.", "*speaks softly* Peace be with you, wanderer."],
                "healer": ["*looks up with kind eyes* Are you injured, traveler?", "*speaks gently* Welcome, child. How may I aid you?", "*offers warm smile* Greetings. Do you need tending?"],
                "blacksmith": ["*wipes sweat from brow* What can I forge for you?", "*looks up from anvil* Need weapons or repairs?", "*grunts* You look like you need better gear."],
                "wizard": ["*looks up from spell components* Ah, the currents brought you here.", "*waves staff mysteriously* The arcane whispers of your arrival.", "*eyes glow briefly* Magic draws you here, I sense."]
            },
            "sci-fi": {
                "guard": ["*checks scanner* Identification, please.", "*hand on weapon* Access authorized?", "*speaks into comm* We have a visitor."],
                "engineer": ["*looks up from console* System malfunction?", "*adjusts goggles* Technical assistance needed?", "*powers down tool* What's the problem?"],
                "scientist": ["*pauses experiment* Fascinating! A test subject!", "*makes notes* Interesting specimen.", "*scans you with device* Remarkable readings."],
                "pilot": ["*leans back in chair* Going somewhere?", "*checks instruments* Need a ride?", "*grins* Another groundwalker, eh?"],
                "medic": ["*medical scanner beeps* Any injuries to report?", "*checks medical kit* Need treatment?", "*professional tone* Medical assistance required?"],
                "hacker": ["*doesn't look up from screens* What do you want?", "*types rapidly* Another corpo spy?", "*glances over* You're not supposed to be here."],
                "operative": ["*emerges from shadows* You're being watched.", "*speaks quietly* We need to talk.", "*checks surroundings* This isn't secure."]
            },
            "horror": {
                "survivor": ["*jumps at your approach* Oh! Another living soul!", "*clutches makeshift weapon* Are... are you real?", "*whispers* Please tell me you're not one of them."],
                "cultist": ["*eyes gleam with madness* The darkness calls to you too!", "*chants softly* Join us in eternal shadow.", "*grins unsettlingly* The old ones have sent you."],
                "priest": ["*holds holy symbol* May God protect us both.", "*prays quietly* The Lord tests us here.", "*trembles* Evil walks these halls."],
                "doctor": ["*blood on hands* Another patient for the procedure.", "*clinical tone* Symptoms present as expected.", "*disturbing smile* Time for your examination."],
                "scholar": ["*surrounded by forbidden tomes* The knowledge! It calls!", "*eyes wide with obsession* Have you seen the texts?", "*mutters about ancient secrets* The truth is here somewhere."]
            },
            "cyberpunk": {
                "hacker": ["*neon light reflects off screen* You lost, choom?", "*doesn't look away from code* Another tourist?", "*types aggressively* Corporate or street?"],
                "guard": ["*corporate uniform pristine* Authorized personnel only.", "*checks tablet* Your credentials?", "*hand on shock baton* Move along, citizen."],
                "executive": ["*expensive suit, cold smile* How can I exploit-- I mean, help you?", "*checks chrono* Make it quick.", "*calculates profit margins* What's your worth?"],
                "engineer": ["*surrounded by tech* Another system crash?", "*works on implant* Upgrades or repairs?", "*sparks fly* Just give me a few more cycles."],
                "runner": ["*checks alley entrance* Quick job or just passing through?", "*nervous energy* Got heat on your tail?", "*always moving* Time is money, choom."],
                "operative": ["*from the shadows* You didn't see me here.", "*checks for surveillance* We're clean.", "*professional whisper* What's the contract?"]
            }
        }
        
        templates = greeting_templates.get(theme, greeting_templates["fantasy"]).get(role, ["Greetings, traveler."])
        return random.choice(templates)
    
    def _generate_dynamic_farewell(self, role: str, theme: str) -> str:
        """Generate dynamic farewell based on NPC characteristics"""
        farewell_templates = {
            "fantasy": {
                "warrior": ["May your blade stay sharp!", "Fight with honor!", "Victory be yours!"],
                "guard": ["Stay vigilant out there.", "Keep to the safe paths.", "Watch your back."],
                "scholar": ["May knowledge light your path.", "Seek wisdom in all things.", "Learn well, traveler."],
                "trader": ["Profitable ventures ahead!", "May fortune favor your trades!", "Come back with more coin!"],
                "priest": ["Go with divine blessing.", "May the light protect you.", "Walk in sacred grace."],
                "healer": ["Take care of yourself.", "May you stay healthy and whole.", "Healing be with you."],
                "blacksmith": ["May your equipment serve you well.", "Good steel makes good adventures.", "Forge your own destiny."],
                "wizard": ["May the arcane currents guide you.", "Magic follows in your wake.", "The mysteries await you."]
            },
            "sci-fi": {
                "guard": ["Stay in authorized zones.", "Watch for security alerts.", "Keep your clearance current."],
                "engineer": ["Systems optimal.", "All functions normal.", "May your tech not fail you."],
                "scientist": ["Fascinating data ahead.", "Continue your research.", "The hypothesis holds."],
                "pilot": ["Safe travels through the void.", "May your nav systems stay true.", "See you in the stars."],
                "medic": ["Stay healthy out there.", "Medical bay is always open.", "Vital signs optimal."],
                "hacker": ["Stay off the grid.", "Don't get traced.", "Keep your ICE cold."],
                "operative": ["This conversation never happened.", "Stay in the shadows.", "Watch for surveillance."]
            },
            "horror": {
                "survivor": ["Don't trust the shadows.", "They're always watching.", "Stay in the light!"],
                "cultist": ["The darkness embraces you.", "Join us when you're ready.", "The old ones call."],
                "priest": ["May God have mercy on your soul.", "Evil cannot triumph forever.", "Faith will protect you."],
                "doctor": ["The procedure will continue.", "Symptoms are progressing nicely.", "See you on the table."],
                "scholar": ["The forbidden knowledge awaits.", "Truth lies in the texts.", "The ancient wisdom calls."]
            },
            "cyberpunk": {
                "hacker": ["Keep it digital, choom.", "Don't get flatlined.", "Data is freedom."],
                "guard": ["Move along, citizen.", "Corporate interests protected.", "Comply with regulations."],
                "executive": ["Profit margins maintained.", "Shareholder value preserved.", "The market decides all."],
                "engineer": ["May your chrome stay shiny.", "Upgrades available 24/7.", "Technology serves."],
                "runner": ["Fast data, faster legs.", "The street remembers.", "Keep running, never stop."],
                "operative": ["The job is never done.", "Trust no one.", "Information is ammunition."]
            }
        }
        
        templates = farewell_templates.get(theme, farewell_templates["fantasy"]).get(role, ["Safe travels."])
        return random.choice(templates)