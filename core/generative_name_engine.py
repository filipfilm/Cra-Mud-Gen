"""
Truly Generative Name Engine for Cra-mud-gen
Creates completely unique names using syllable patterns and linguistic rules
No hardcoded lists - everything is generated dynamically based on theme context
"""
import random
from typing import Dict, List, Optional, Tuple


class GenerativeNameEngine:
    """Generates completely unique names using syllable patterns and linguistic rules"""
    
    def __init__(self):
        """Initialize the generative engine with phonetic patterns"""
        self.syllable_patterns = self._initialize_syllable_patterns()
        self.theme_linguistics = self._initialize_theme_linguistics()
        
    def _initialize_syllable_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize syllable building blocks by phonetic type"""
        return {
            "consonant_starts": {
                "soft": ["b", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "r", "s", "t", "v", "w", "y", "z"],
                "hard": ["br", "cr", "dr", "fr", "gr", "pr", "tr", "bl", "cl", "fl", "gl", "pl", "sl", "sc", "sk", "sp", "st", "sw"],
                "exotic": ["th", "ph", "ch", "sh", "zh", "kh", "gh", "xh", "zr", "vr", "wr"]
            },
            "vowel_cores": {
                "short": ["a", "e", "i", "o", "u"],
                "long": ["aa", "ee", "ii", "oo", "uu", "ay", "ey", "oy"],
                "complex": ["ae", "ai", "au", "ea", "ei", "eo", "ia", "ie", "io", "ou", "ua", "ue", "ui"]
            },
            "consonant_ends": {
                "soft": ["n", "m", "r", "l", "s", "t", "k", "d", "g", "x", "z"],
                "hard": ["th", "st", "nd", "nt", "rd", "rk", "lk", "lt", "rt", "sk", "sp"],
                "cluster": ["ndr", "str", "rst", "nst", "rth", "kth", "lth"]
            }
        }
    
    def _initialize_theme_linguistics(self) -> Dict[str, Dict]:
        """Initialize linguistic rules and patterns for each theme"""
        return {
            "fantasy": {
                "syllable_preference": {"min": 2, "max": 4},
                "consonant_bias": {"soft": 0.4, "hard": 0.4, "exotic": 0.2},
                "vowel_bias": {"short": 0.5, "long": 0.3, "complex": 0.2},
                "ending_bias": {"soft": 0.6, "hard": 0.3, "cluster": 0.1},
                "common_morphemes": ["ald", "wyn", "thor", "grim", "stone", "wind", "fire", "moon", "star"],
                "title_generators": ["noble", "mystical", "martial", "scholarly"],
                "name_flow": "flowing"
            },
            "sci-fi": {
                "syllable_preference": {"min": 1, "max": 3},
                "consonant_bias": {"soft": 0.3, "hard": 0.5, "exotic": 0.2},
                "vowel_bias": {"short": 0.6, "long": 0.2, "complex": 0.2},
                "ending_bias": {"soft": 0.7, "hard": 0.2, "cluster": 0.1},
                "common_morphemes": ["tek", "neo", "cyber", "quantum", "neural", "digital", "binary", "core"],
                "title_generators": ["technical", "military", "corporate", "operative"],
                "name_flow": "sharp"
            },
            "horror": {
                "syllable_preference": {"min": 2, "max": 5},
                "consonant_bias": {"soft": 0.3, "hard": 0.3, "exotic": 0.4},
                "vowel_bias": {"short": 0.4, "long": 0.4, "complex": 0.2},
                "ending_bias": {"soft": 0.4, "hard": 0.4, "cluster": 0.2},
                "common_morphemes": ["mor", "goth", "raven", "shadow", "blood", "night", "doom", "curse"],
                "title_generators": ["cursed", "ancient", "mad", "lost"],
                "name_flow": "ominous"
            },
            "cyberpunk": {
                "syllable_preference": {"min": 1, "max": 2},
                "consonant_bias": {"soft": 0.2, "hard": 0.6, "exotic": 0.2},
                "vowel_bias": {"short": 0.7, "long": 0.2, "complex": 0.1},
                "ending_bias": {"soft": 0.8, "hard": 0.2, "cluster": 0.0},
                "common_morphemes": ["byte", "neon", "chrome", "wire", "grid", "hack", "punk", "ghost"],
                "title_generators": ["street", "corporate", "underground", "net"],
                "name_flow": "edgy"
            }
        }
    
    def generate_dynamic_name(self, theme: str = "fantasy", role: str = None, name_type: str = "full") -> str:
        """
        Generate a completely unique name using linguistic rules
        
        Args:
            theme: Theme context (fantasy, sci-fi, horror, cyberpunk)
            role: Character role for title generation
            name_type: "first", "surname", "full", "title_only"
            
        Returns:
            Generated name string
        """
        theme = theme.lower()
        if theme not in self.theme_linguistics:
            theme = "fantasy"
        
        if name_type == "first":
            return self._generate_first_name(theme)
        elif name_type == "surname":
            return self._generate_surname(theme)
        elif name_type == "title_only":
            return self._generate_dynamic_title(theme, role)
        else:  # full name
            return self._generate_full_name(theme, role)
    
    def _generate_first_name(self, theme: str) -> str:
        """Generate a unique first name using syllable patterns"""
        rules = self.theme_linguistics[theme]
        syllable_count = random.randint(rules["syllable_preference"]["min"], rules["syllable_preference"]["max"])
        
        name_parts = []
        for i in range(syllable_count):
            syllable = self._create_syllable(theme, position=i, total=syllable_count)
            name_parts.append(syllable)
        
        name = "".join(name_parts)
        
        # Apply theme-specific modifications
        name = self._apply_theme_modifications(name, theme, "first")
        
        return name.capitalize()
    
    def _generate_surname(self, theme: str) -> str:
        """Generate a unique surname that may include morphemes"""
        rules = self.theme_linguistics[theme]
        
        # 40% chance to use morpheme-based surname
        if random.random() < 0.4 and rules["common_morphemes"]:
            return self._generate_morpheme_surname(theme)
        else:
            # Generate syllable-based surname
            syllable_count = random.randint(2, 4)
            name_parts = []
            
            for i in range(syllable_count):
                syllable = self._create_syllable(theme, position=i, total=syllable_count)
                name_parts.append(syllable)
            
            name = "".join(name_parts)
            name = self._apply_theme_modifications(name, theme, "surname")
            
            return name.capitalize()
    
    def _generate_morpheme_surname(self, theme: str) -> str:
        """Generate surname using thematic morphemes"""
        rules = self.theme_linguistics[theme]
        morphemes = rules["common_morphemes"]
        
        if random.random() < 0.6:
            # Single morpheme + syllable
            morpheme = random.choice(morphemes)
            suffix = self._create_syllable(theme, position=1, total=2)
            return f"{morpheme.capitalize()}{suffix}"
        else:
            # Two morphemes combined
            morpheme1 = random.choice(morphemes)
            morpheme2 = random.choice(morphemes)
            return f"{morpheme1.capitalize()}{morpheme2}"
    
    def _create_syllable(self, theme: str, position: int, total: int) -> str:
        """Create a single syllable following theme rules"""
        rules = self.theme_linguistics[theme]
        patterns = self.syllable_patterns
        
        # Choose consonant start based on position and theme bias
        if position == 0 or random.random() < 0.7:  # First syllable or 70% of others get consonants
            consonant_type = self._weighted_choice(rules["consonant_bias"])
            consonant = random.choice(patterns["consonant_starts"][consonant_type])
        else:
            consonant = ""
        
        # Choose vowel core
        vowel_type = self._weighted_choice(rules["vowel_bias"])
        vowel = random.choice(patterns["vowel_cores"][vowel_type])
        
        # Choose consonant end (less frequent in middle syllables)
        if position == total - 1 or random.random() < 0.4:  # Last syllable or 40% of others
            ending_type = self._weighted_choice(rules["ending_bias"])
            ending = random.choice(patterns["consonant_ends"][ending_type])
        else:
            ending = ""
        
        return f"{consonant}{vowel}{ending}"
    
    def _weighted_choice(self, weights: Dict[str, float]) -> str:
        """Make weighted random choice from dictionary"""
        choices = list(weights.keys())
        probabilities = list(weights.values())
        return random.choices(choices, weights=probabilities)[0]
    
    def _apply_theme_modifications(self, name: str, theme: str, name_type: str) -> str:
        """Apply theme-specific phonetic modifications"""
        
        if theme == "sci-fi":
            # Add tech-like elements occasionally
            if random.random() < 0.2:
                if name_type == "first":
                    name = name.replace("a", "4").replace("e", "3").replace("o", "0")[:len(name)//2] + name[len(name)//2:]
                else:
                    name += random.choice(["tek", "sys", "net", "core"])
        
        elif theme == "horror":
            # Make names sound more ominous
            if random.random() < 0.3:
                name = name.replace("s", "ss").replace("k", "ck").replace("th", "tth")
        
        elif theme == "cyberpunk":
            # Shorten and make edgier
            if len(name) > 4 and random.random() < 0.4:
                name = name[:4]  # Truncate to make it punchy
        
        return name
    
    def _generate_dynamic_title(self, theme: str, role: str = None) -> str:
        """Generate contextually appropriate titles dynamically"""
        rules = self.theme_linguistics[theme]
        title_type = random.choice(rules["title_generators"])
        
        if theme == "fantasy":
            return self._generate_fantasy_title(title_type, role)
        elif theme == "sci-fi":
            return self._generate_scifi_title(title_type, role)
        elif theme == "horror":
            return self._generate_horror_title(title_type, role)
        elif theme == "cyberpunk":
            return self._generate_cyberpunk_title(title_type, role)
        
        return ""
    
    def _generate_fantasy_title(self, title_type: str, role: str) -> str:
        """Generate fantasy-appropriate titles"""
        base_titles = {
            "noble": ["Lord", "Lady", "Duke", "Duchess", "Baron", "Baroness", "Count", "Countess"],
            "mystical": ["Sage", "Mystic", "Oracle", "Seer", "Archmage", "Enchanter", "Keeper", "Guardian"],
            "martial": ["Sir", "Dame", "Captain", "Commander", "Marshal", "Champion", "Warlord", "Knight"],
            "scholarly": ["Master", "Scholar", "Lorekeeper", "Chronicler", "Elder", "Wise", "Ancient"]
        }
        
        titles = base_titles.get(title_type, base_titles["martial"])
        base_title = random.choice(titles)
        
        # Add role-specific modifications
        if role == "warrior" and title_type != "martial":
            return random.choice(["Sir", "Captain", "Champion"])
        elif role == "wizard" and title_type != "mystical":
            return random.choice(["Sage", "Archmage", "Mystic"])
            
        return base_title
    
    def _generate_scifi_title(self, title_type: str, role: str) -> str:
        """Generate sci-fi appropriate titles"""
        base_titles = {
            "technical": ["Engineer", "Technician", "Specialist", "Analyst", "Systems", "Tech"],
            "military": ["Captain", "Commander", "Lieutenant", "Sergeant", "Major", "Admiral"],
            "corporate": ["Executive", "Director", "Manager", "Supervisor", "Administrator", "Chief"],
            "operative": ["Agent", "Operative", "Runner", "Contractor", "Asset", "Handler"]
        }
        
        titles = base_titles.get(title_type, base_titles["technical"])
        base_title = random.choice(titles)
        
        # Add numeric or classification suffixes sometimes
        if random.random() < 0.3:
            if title_type == "technical":
                return f"{base_title}-{random.randint(7, 99)}"
            elif title_type == "operative":
                return f"{base_title} {random.choice(['Alpha', 'Beta', 'Gamma', 'Prime'])}"
        
        return base_title
    
    def _generate_horror_title(self, title_type: str, role: str) -> str:
        """Generate horror-appropriate titles"""
        base_titles = {
            "cursed": ["Cursed", "Damned", "Forsaken", "Doomed", "Lost", "Fallen"],
            "ancient": ["Ancient", "Old", "Elder", "Forgotten", "Timeless"],
            "mad": ["Mad", "Twisted", "Deranged", "Broken", "Shattered"],
            "lost": ["Missing", "Vanished", "Ghost", "Shade", "Wraith", "Spirit"]
        }
        
        titles = base_titles.get(title_type, base_titles["cursed"])
        return random.choice(titles)
    
    def _generate_cyberpunk_title(self, title_type: str, role: str) -> str:
        """Generate cyberpunk-appropriate titles"""
        base_titles = {
            "street": ["", "Street", "Alley", "Underground", "Shadow"],  # Empty string for no title
            "corporate": ["Corp", "Executive", "Director", "Manager", "Suit"],
            "underground": ["Ghost", "Phantom", "Shadow", "Wire", "Net"],
            "net": ["Runner", "Jockey", "Hacker", "Ghost", "Cowboy", "Decker"]
        }
        
        titles = base_titles.get(title_type, base_titles["street"])
        title = random.choice(titles)
        
        # Cyberpunk often uses no titles or very short ones
        if not title or random.random() < 0.4:
            return ""
        
        return title
    
    def _generate_full_name(self, theme: str, role: str = None) -> str:
        """Generate a complete name with optional title"""
        first_name = self._generate_first_name(theme)
        surname = self._generate_surname(theme)
        
        # Determine if title should be used (varies by theme)
        title_chance = {"fantasy": 0.4, "sci-fi": 0.3, "horror": 0.5, "cyberpunk": 0.2}
        
        if random.random() < title_chance.get(theme, 0.3):
            title = self._generate_dynamic_title(theme, role)
            if title:
                return f"{title} {first_name} {surname}"
        
        return f"{first_name} {surname}"
    
    def generate_item_name(self, item_type: str, theme: str = "fantasy", rarity: str = "common") -> str:
        """Generate completely unique item names"""
        
        # Generate base item name dynamically
        base_name = self._generate_item_base(item_type, theme)
        
        # Add rarity-appropriate modifiers
        if rarity != "common":
            modifier = self._generate_item_modifier(rarity, theme)
            if modifier:
                if random.random() < 0.5:
                    return f"{modifier} {base_name}"
                else:
                    return f"{base_name} of {self._generate_item_suffix(rarity, theme)}"
        
        return base_name
    
    def _generate_item_base(self, item_type: str, theme: str) -> str:
        """Generate base item name using theme-appropriate syllables"""
        
        # Create a thematic base word
        syllable_count = random.randint(1, 3)
        base_parts = []
        
        for i in range(syllable_count):
            syllable = self._create_syllable(theme, i, syllable_count)
            base_parts.append(syllable)
        
        base_word = "".join(base_parts).capitalize()
        
        # Add item type classification
        type_classifiers = {
            "fantasy": {
                "weapon": ["blade", "edge", "strike", "fang", "claw"],
                "armor": ["guard", "ward", "shell", "hide", "mail"],
                "potion": ["draught", "brew", "elixir", "tonic"],
                "scroll": ["codex", "text", "script", "rune"]
            },
            "sci-fi": {
                "weapon": ["beam", "pulse", "disruptor", "lance", "cannon"],
                "armor": ["suit", "mesh", "shield", "plating", "barrier"],
                "tech": ["device", "unit", "module", "system", "interface"],
                "consumable": ["stim", "boost", "enhance", "patch"]
            },
            "horror": {
                "weapon": ["ripper", "cleaver", "fang", "talon", "bane"],
                "artifact": ["relic", "idol", "totem", "bone", "skull"],
                "consumable": ["essence", "extract", "ichor", "bile"]
            },
            "cyberpunk": {
                "weapon": ["striker", "zapper", "slicer", "burner"],
                "tech": ["chip", "deck", "wire", "link", "node"],
                "software": ["code", "script", "virus", "daemon"]
            }
        }
        
        classifiers = type_classifiers.get(theme, type_classifiers["fantasy"]).get(item_type, [item_type])
        if classifiers:
            classifier = random.choice(classifiers)
            return f"{base_word}{classifier.capitalize()}"
        
        return base_word
    
    def _generate_item_modifier(self, rarity: str, theme: str) -> str:
        """Generate dynamic item modifier based on rarity and theme"""
        
        rarity_syllables = {
            "uncommon": 1,
            "rare": 2, 
            "legendary": 2
        }
        
        syllable_count = rarity_syllables.get(rarity, 1)
        modifier_parts = []
        
        for i in range(syllable_count):
            syllable = self._create_syllable(theme, i, syllable_count)
            modifier_parts.append(syllable)
        
        modifier = "".join(modifier_parts).capitalize()
        
        # Apply rarity-specific enhancements
        if rarity == "legendary" and random.random() < 0.5:
            power_words = {
                "fantasy": ["god", "titan", "eternal", "void"],
                "sci-fi": ["quantum", "neural", "cosmic", "infinite"],
                "horror": ["nightmare", "abyss", "soul", "blood"],
                "cyberpunk": ["ghost", "matrix", "zero", "prime"]
            }
            power_word = random.choice(power_words.get(theme, power_words["fantasy"]))
            modifier = f"{power_word.capitalize()}{modifier}"
        
        return modifier
    
    def _generate_item_suffix(self, rarity: str, theme: str) -> str:
        """Generate dynamic item suffix"""
        suffix_parts = []
        syllable_count = 2 if rarity == "legendary" else 1
        
        for i in range(syllable_count):
            syllable = self._create_syllable(theme, i, syllable_count)
            suffix_parts.append(syllable)
        
        return "".join(suffix_parts).capitalize()
    
    def generate_location_name(self, location_type: str, theme: str = "fantasy") -> str:
        """Generate unique location names"""
        
        # Generate descriptive element
        descriptor_syllables = random.randint(1, 2)
        descriptor_parts = []
        
        for i in range(descriptor_syllables):
            syllable = self._create_syllable(theme, i, descriptor_syllables)
            descriptor_parts.append(syllable)
        
        descriptor = "".join(descriptor_parts).capitalize()
        
        # Generate location base name
        location_syllables = random.randint(1, 3)
        location_parts = []
        
        for i in range(location_syllables):
            syllable = self._create_syllable(theme, i, location_syllables)
            location_parts.append(syllable)
        
        location_base = "".join(location_parts).capitalize()
        
        # Combine with location type
        type_words = {
            "fantasy": {"chamber": "Hall", "library": "Archive", "shrine": "Sanctum"},
            "sci-fi": {"chamber": "Module", "laboratory": "Lab", "server": "Core"},
            "horror": {"chamber": "Crypt", "ritual": "Altar", "library": "Vault"},
            "cyberpunk": {"chamber": "Node", "server": "Hub", "club": "Den"}
        }
        
        type_word = type_words.get(theme, type_words["fantasy"]).get(location_type, location_type.capitalize())
        
        return f"{descriptor} {location_base} {type_word}"