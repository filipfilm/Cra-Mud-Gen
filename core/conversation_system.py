"""
Conversation System for NPC Interactions
Manages dialogue trees, NPC memory, and contextual responses
"""
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class ConversationContext:
    """Tracks conversation state and history"""
    current_npc: Optional[str] = None
    conversation_history: List[str] = field(default_factory=list)
    npc_memory: Dict[str, Any] = field(default_factory=dict)
    last_topic: Optional[str] = None
    conversation_active: bool = False


@dataclass
class NPCPersonality:
    """Defines NPC personality and response patterns"""
    name: str
    occupation: str
    personality_traits: List[str]
    greeting: str
    farewell: str
    topics: Dict[str, str]  # topic -> response
    default_response: str
    speech_pattern: str = "normal"  # "formal", "casual", "gruff", "mystical"


class ConversationSystem:
    """Manages NPC conversations and dialogue"""
    
    def __init__(self):
        self.context = ConversationContext()
        self.npcs = self._initialize_npcs()
        self.conversation_patterns = self._initialize_patterns()
    
    def _initialize_npcs(self) -> Dict[str, NPCPersonality]:
        """Initialize NPC personalities and dialogue"""
        npcs = {}
        
        # Weapons Master
        npcs["weapons master"] = NPCPersonality(
            name="Gorin Ironforge",
            occupation="Master Blacksmith",
            personality_traits=["gruff", "honest", "skilled", "protective"],
            greeting="*looks up from forge* Aye, what brings ye to me workshop, adventurer?",
            farewell="May yer blade stay sharp and yer armor strong, warrior.",
            topics={
                "weapons": "I craft the finest blades in all the realm! Steel so sharp it could cut through dragon scales. What kind of weapon ye be needin'?",
                "armor": "Aye, protection is just as important as offense. I've got mail, plate, leather - all crafted with me own hands.",
                "fortune": "*chuckles gruffly* Fortune? Aye, I've made me fortune with these hands and this forge. Hard work beats luck every time, lad.",
                "gold": "Gold's nice, but a well-made sword is worth more than all the gold in the kingdom when yer life's on the line.",
                "quest": "Quests, eh? I hear tell of strange happenings in the deeper tunnels. Might be worth investigatin' if ye've got the mettle.",
                "trade": "I'll trade ye good steel for good coin, or rare materials if ye've got 'em. What ye got to offer?",
                "work": "*pounds hammer on anvil* This is me life's work - turning raw metal into instruments of legend.",
                "dragons": "*eyes gleam* Ah, dragon steel! The finest material a smith could work with. Bring me dragon scales and I'll forge ye something legendary!"
            },
            default_response="*scratches beard thoughtfully* Can't say I know much about that, but if it involves metal or combat, I might be able to help.",
            speech_pattern="gruff"
        )
        
        # Fortune Teller
        npcs["fortune teller"] = NPCPersonality(
            name="Madame Zelara",
            occupation="Mystic Seer",
            personality_traits=["mysterious", "wise", "cryptic", "intuitive"],
            greeting="*looks up from crystal ball* Ahh, the fates have brought you to my humble caravan. I sense great destiny about you...",
            farewell="The threads of fate guide your path, traveler. May fortune smile upon your journey.",
            topics={
                "fortune": "*peers into crystal ball* I see... gold glinting in dark places, but beware - greed can be a curse as much as a blessing.",
                "future": "The mists of time swirl... I see trials ahead, but also great rewards for those brave enough to seize them.",
                "quest": "*crystal ball glows* The spirits whisper of an ancient evil stirring in the depths. You will face it, whether you choose to or not.",
                "death": "*shudders* The shadows of death hover near... but they are not yours to claim, not yet. Steel yourself, warrior.",
                "gold": "Coins and jewels... yes, I see wealth in your future, but also choices that will test your very soul.",
                "love": "*smiles mysteriously* Affairs of the heart are clouded... but I sense a kindred spirit in your future travels.",
                "magic": "Magic flows through all things, child. Even now, it courses through your veins, waiting to be awakened.",
                "secrets": "*whispers* The dungeon holds many secrets... some better left buried. But curiosity calls to you, doesn't it?"
            },
            default_response="*waves hand over crystal ball* The mists are unclear on this matter... ask me something else, perhaps?",
            speech_pattern="mystical"
        )
        
        return npcs
    
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize conversation pattern keywords"""
        return {
            "greeting": ["hello", "hi", "greetings", "good day", "hey", "talk"],
            "farewell": ["goodbye", "bye", "farewell", "see you", "later", "leave"],
            "questions": ["who", "what", "where", "when", "why", "how"],
            "trade": ["buy", "sell", "trade", "purchase", "cost", "price", "gold"],
            "combat": ["fight", "battle", "weapon", "sword", "armor", "shield"],
            "magic": ["magic", "spell", "enchant", "potion", "mystical", "arcane"],
            "information": ["tell me", "know about", "heard of", "information", "news"]
        }
    
    def start_conversation(self, npc_identifier: str, player_input: str) -> str:
        """Start or continue conversation with an NPC"""
        npc = self._find_npc(npc_identifier)
        
        if not npc:
            return f"There's no {npc_identifier} here to talk to."
        
        # Set conversation context
        if not self.context.conversation_active or self.context.current_npc != npc.name:
            self.context = ConversationContext(
                current_npc=npc.name,
                conversation_active=True
            )
            # Initial greeting
            return npc.greeting
        
        # Process ongoing conversation
        return self._process_conversation(npc, player_input)
    
    def _find_npc(self, identifier: str) -> Optional[NPCPersonality]:
        """Find NPC by name or occupation"""
        identifier_lower = identifier.lower()
        for key, npc in self.npcs.items():
            if (identifier_lower in key.lower() or 
                identifier_lower in npc.name.lower() or 
                identifier_lower in npc.occupation.lower()):
                return npc
        return None
    
    def _process_conversation(self, npc: NPCPersonality, player_input: str) -> str:
        """Process player input and generate NPC response"""
        player_input_lower = player_input.lower().strip()
        
        # Add to conversation history
        self.context.conversation_history.append(f"Player: {player_input}")
        
        # Check for farewell
        if any(word in player_input_lower for word in self.conversation_patterns["farewell"]):
            self._end_conversation()
            return npc.farewell
        
        # Find matching topic
        topic_match = self._find_topic_match(npc, player_input_lower)
        
        if topic_match:
            response = npc.topics[topic_match]
            self.context.last_topic = topic_match
            
            # Add context-aware additions
            response = self._add_contextual_elements(npc, response, player_input_lower)
            
        else:
            # Generate contextual default response
            response = self._generate_contextual_default(npc, player_input_lower)
        
        # Add to conversation history
        self.context.conversation_history.append(f"{npc.name}: {response}")
        
        # Apply speech pattern formatting
        response = self._apply_speech_pattern(response, npc.speech_pattern)
        
        return response
    
    def _find_topic_match(self, npc: NPCPersonality, player_input: str) -> Optional[str]:
        """Find the best matching topic for player input"""
        # Direct topic matches
        for topic, _ in npc.topics.items():
            if topic in player_input:
                return topic
        
        # Pattern-based matching
        topic_patterns = {
            "weapons": ["weapon", "sword", "blade", "axe", "mace", "bow", "dagger", "steel"],
            "armor": ["armor", "protection", "shield", "mail", "plate", "leather", "helm"],
            "fortune": ["fortune", "luck", "wealth", "riches", "treasure", "money"],
            "gold": ["gold", "coin", "money", "payment", "currency", "silver"],
            "quest": ["quest", "adventure", "mission", "task", "journey", "danger"],
            "trade": ["trade", "buy", "sell", "purchase", "exchange", "deal"],
            "magic": ["magic", "spell", "enchant", "mystical", "arcane", "power"],
            "future": ["future", "destiny", "fate", "tomorrow", "coming", "ahead"],
            "death": ["death", "die", "kill", "danger", "deadly", "mortal"],
            "work": ["work", "job", "craft", "skill", "profession", "trade"]
        }
        
        for topic, keywords in topic_patterns.items():
            if topic in npc.topics and any(keyword in player_input for keyword in keywords):
                return topic
        
        return None
    
    def _add_contextual_elements(self, npc: NPCPersonality, response: str, player_input: str) -> str:
        """Add contextual elements based on conversation history"""
        # Add player name recognition if mentioned multiple times
        if len(self.context.conversation_history) > 4:
            if npc.speech_pattern == "gruff":
                response = response.replace("adventurer", "friend", 1)
            elif npc.speech_pattern == "mystical":
                response = response.replace("traveler", "seeker", 1)
        
        # Add urgency based on certain keywords
        if any(word in player_input for word in ["urgent", "quickly", "help", "danger"]):
            if npc.speech_pattern == "gruff":
                response = "*looks concerned* " + response
            elif npc.speech_pattern == "mystical":
                response = "*crystal ball flickers ominously* " + response
        
        return response
    
    def _generate_contextual_default(self, npc: NPCPersonality, player_input: str) -> str:
        """Generate a contextual default response"""
        # Check if it's a question
        if any(word in player_input for word in ["?", "who", "what", "where", "when", "why", "how"]):
            if npc.speech_pattern == "gruff":
                return "*scratches head* Can't say I know the answer to that one, friend."
            elif npc.speech_pattern == "mystical":
                return "*peers into crystal ball* The mists are too thick... the answer eludes me."
        
        # Check if player seems confused
        if any(word in player_input for word in ["confused", "don't understand", "what do you mean"]):
            return "Let me explain better... " + npc.default_response
        
        return npc.default_response
    
    def _apply_speech_pattern(self, response: str, pattern: str) -> str:
        """Apply speech pattern formatting"""
        if pattern == "gruff":
            # Already formatted in the responses
            return response
        elif pattern == "mystical":
            # Add mystical emphasis occasionally
            if "*" not in response and len(response) > 50:
                return "*the air shimmers* " + response
            return response
        elif pattern == "formal":
            # Make more formal
            response = response.replace("you", "you, good sir")
            return response
        
        return response
    
    def _end_conversation(self):
        """End the current conversation"""
        self.context.conversation_active = False
        self.context.current_npc = None
    
    def is_in_conversation(self) -> bool:
        """Check if currently in a conversation"""
        return self.context.conversation_active
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """Get current conversation context"""
        return {
            "active": self.context.conversation_active,
            "npc": self.context.current_npc,
            "history_length": len(self.context.conversation_history),
            "last_topic": self.context.last_topic
        }
    
    def parse_conversation_input(self, user_input: str) -> Dict[str, Any]:
        """Parse user input to detect conversation attempts"""
        input_lower = user_input.lower().strip()
        
        # Check for "talk to X" pattern
        talk_match = re.match(r"(?:talk to|speak to|speak with|talk with|address)\s+(.+)", input_lower)
        if talk_match:
            npc_name = talk_match.group(1).strip()
            return {
                "type": "start_conversation",
                "npc": npc_name,
                "message": user_input
            }
        
        # Check for direct conversation (if already talking)
        if self.context.conversation_active:
            return {
                "type": "continue_conversation", 
                "message": user_input
            }
        
        # Check for greeting patterns that might start conversation
        greeting_patterns = [
            r"(?:hello|hi|hey|greetings)\s+(.+)",
            r"(.+),?\s+(?:hello|hi|hey|greetings)"
        ]
        
        for pattern in greeting_patterns:
            match = re.match(pattern, input_lower)
            if match:
                npc_name = match.group(1).strip()
                return {
                    "type": "start_conversation",
                    "npc": npc_name,
                    "message": user_input
                }
        
        return {"type": "not_conversation"}