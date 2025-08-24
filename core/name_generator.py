"""
Dynamic Name Generation System for Cra-mud-gen
Generates thematic names for NPCs, items, locations, and other game elements
"""
import random
from typing import Dict, List, Optional


class NameGenerator:
    """Generates contextual names for game elements"""
    
    def __init__(self):
        """Initialize name generator with themed name pools"""
        self.name_pools = self._initialize_name_pools()
        self.title_pools = self._initialize_title_pools()
        self.surname_pools = self._initialize_surname_pools()
        
    def _initialize_name_pools(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize first name pools by theme and gender"""
        return {
            "fantasy": {
                "masculine": [
                    "Aiden", "Aldric", "Bastian", "Cedric", "Darian", "Edmund", "Finn", "Gareth", 
                    "Hadrian", "Ivan", "Jasper", "Kieran", "Lysander", "Magnus", "Nolan", 
                    "Orion", "Percival", "Quintin", "Roderick", "Stellan", "Theron", "Ulric", 
                    "Viktor", "Willem", "Xavier", "Yorick", "Zander"
                ],
                "feminine": [
                    "Aria", "Beatrice", "Celeste", "Delia", "Evelyn", "Fiona", "Gwendolyn", 
                    "Helena", "Iris", "Juliana", "Kira", "Lydia", "Miranda", "Nora", "Ophelia", 
                    "Penelope", "Quinn", "Rosalind", "Seraphina", "Theodora", "Una", "Vivienne", 
                    "Willow", "Xara", "Yvonne", "Zara"
                ],
                "neutral": [
                    "Sage", "River", "Phoenix", "Raven", "Storm", "Vale", "Wren", "Ash", 
                    "Brook", "Clay", "Dawn", "Echo", "Frost", "Gray", "Haven", "Justice"
                ]
            },
            "sci-fi": {
                "masculine": [
                    "Atlas", "Caspian", "Drake", "Echo", "Felix", "Gideon", "Hunter", "Ion", 
                    "Jax", "Knox", "Leo", "Matrix", "Neo", "Orion", "Phoenix", "Quantum", 
                    "Rex", "Sirius", "Titan", "Vector", "Warden", "Xerus", "Yago", "Zephyr"
                ],
                "feminine": [
                    "Astra", "Binary", "Cora", "Delta", "Echo", "Flux", "Galaxy", "Halo", 
                    "Ion", "Jinx", "Kyra", "Luna", "Nyx", "Onyx", "Pixel", "Quasar", 
                    "Raven", "Stella", "Terra", "Unity", "Vega", "Wren", "Xena", "Zara"
                ],
                "neutral": [
                    "Cipher", "Data", "Edge", "Flux", "Grid", "Hex", "Input", "Json", 
                    "Kernel", "Logic", "Mesh", "Node", "Pixel", "Query", "Root", "Sync"
                ]
            },
            "horror": {
                "masculine": [
                    "Amos", "Bartholomew", "Cornelius", "Damien", "Edgar", "Francis", "Gideon", 
                    "Horatio", "Ignatius", "Jeremiah", "Klaus", "Lucifer", "Mortimer", "Nathaniel", 
                    "Obediah", "Phineas", "Quincy", "Reginald", "Silas", "Thaddeus", "Ulysses", 
                    "Vincent", "Waldo", "Xerxes", "Yorick", "Zoltan"
                ],
                "feminine": [
                    "Agatha", "Belinda", "Cordelia", "Drusilla", "Evangeline", "Felicity", "Grizelda", 
                    "Hestia", "Isadora", "Jezebel", "Kassandra", "Lilith", "Mordecai", "Narcissa", 
                    "Ophelia", "Prudence", "Queenie", "Rowena", "Serena", "Tabitha", "Ursula", 
                    "Viviana", "Winifred", "Xanthe", "Yolanda", "Zelda"
                ],
                "neutral": [
                    "Raven", "Shadow", "Thorn", "Wraith", "Ghost", "Shade", "Void", "Mist", 
                    "Hollow", "Dusk", "Gloom", "Bane", "Frost", "Chill", "Ember", "Ash"
                ]
            },
            "cyberpunk": {
                "masculine": [
                    "Ajax", "Blaze", "Chrome", "Dante", "Edge", "Flash", "Ghost", "Hack", 
                    "Ice", "Jinx", "Knox", "Link", "Max", "Neon", "Onyx", "Pulse", 
                    "Quantum", "Razor", "Spike", "Tech", "Vex", "Wire", "X", "Zap"
                ],
                "feminine": [
                    "Angel", "Bit", "Cyber", "Digital", "Echo", "Flux", "Ghost", "Hack", 
                    "Ice", "Jazz", "Kilo", "Lux", "Matrix", "Nova", "Onyx", "Pixel", 
                    "Quantum", "Riot", "Sync", "Tech", "Vex", "Wire", "X", "Zero"
                ],
                "neutral": [
                    "Binary", "Code", "Data", "Error", "Firewall", "Grid", "Hash", "Input", 
                    "Json", "Kernel", "Loop", "Macro", "Node", "Output", "Process", "Query"
                ]
            }
        }
    
    def _initialize_title_pools(self) -> Dict[str, List[str]]:
        """Initialize title pools by theme"""
        return {
            "fantasy": [
                "Sir", "Lady", "Lord", "Master", "Sage", "Elder", "Captain", "Commander", 
                "Priestess", "Priest", "Scholar", "Keeper", "Guardian", "Warden", "Mystic", 
                "Arcane", "Divine", "Sacred", "Ancient", "Wise", "Noble", "Royal", "Grand"
            ],
            "sci-fi": [
                "Captain", "Commander", "Lieutenant", "Sergeant", "Agent", "Operative", 
                "Technician", "Engineer", "Specialist", "Analyst", "Director", "Chief", 
                "Prime", "Alpha", "Beta", "Gamma", "Neural", "Cyber", "Digital", "Quantum"
            ],
            "horror": [
                "Doctor", "Professor", "Reverend", "Father", "Mother", "Sister", "Brother", 
                "Madame", "Mister", "Miss", "Old", "Ancient", "Cursed", "Damned", "Lost", 
                "Mad", "Twisted", "Dark", "Shadow", "Forgotten", "Wretched", "Doomed"
            ],
            "cyberpunk": [
                "Agent", "Operative", "Hacker", "Runner", "Corp", "Executive", "Tech", 
                "Cyber", "Digital", "Mr.", "Ms.", "Boss", "Chief", "Prime", "Alpha", 
                "Beta", "Shadow", "Ghost", "Wire", "Net", "Grid", "System", "Neo"
            ]
        }
    
    def _initialize_surname_pools(self) -> Dict[str, List[str]]:
        """Initialize surname pools by theme"""
        return {
            "fantasy": [
                "Stormwind", "Ironforge", "Goldleaf", "Silverstone", "Brightblade", "Darkwood", 
                "Fireborn", "Frostwalker", "Moonwhisper", "Starweaver", "Dragonbane", "Wolfheart", 
                "Ravencrest", "Thornwick", "Rosewood", "Blackthorne", "Greycloak", "Redmane", 
                "Swiftarrow", "Stronghammer", "Lightbringer", "Shadowmere", "Windwalker", "Earthshaker"
            ],
            "sci-fi": [
                "Vega", "Orion", "Nova", "Stellar", "Cosmic", "Quantum", "Digital", "Neural", 
                "Chrome", "Steel", "Titanium", "Plasma", "Ion", "Photon", "Electron", "Neutron", 
                "Matrix", "Binary", "Cipher", "Vector", "Nexus", "Vertex", "Helix", "Core"
            ],
            "horror": [
                "Grimwood", "Blackwater", "Bloodmoor", "Ravenscroft", "Thornfield", "Ashford", 
                "Blackwood", "Darkmore", "Gravewood", "Shadowmere", "Nightshade", "Doomhaven", 
                "Bleakwood", "Ghoulheart", "Corpsewright", "Bonechill", "Soulrend", "Deathwhisper", 
                "Voidwalker", "Grimheart", "Darkthorn", "Shadowbane", "Cursewood", "Haunthaven"
            ],
            "cyberpunk": [
                "Chrome", "Steel", "Wire", "Grid", "Net", "Code", "Data", "Hack", "Tech", 
                "Cyber", "Digital", "Neural", "System", "Core", "Node", "Link", "Sync", 
                "Binary", "Hex", "Bit", "Byte", "Pixel", "Vector", "Matrix", "Quantum"
            ]
        }
    
    def generate_npc_name(self, theme: str = "fantasy", role: str = None, gender: str = None) -> str:
        """
        Generate a full NPC name with title, first name, and surname
        
        Args:
            theme: Theme for name generation (fantasy, sci-fi, horror, cyberpunk)
            role: NPC role to influence title selection
            gender: Gender preference (masculine, feminine, neutral, random)
            
        Returns:
            Generated full name
        """
        theme = theme.lower()
        if theme not in self.name_pools:
            theme = "fantasy"
        
        # Select gender
        if not gender or gender == "random":
            gender = random.choice(["masculine", "feminine", "neutral"])
        
        # Get name pools for theme
        first_names = self.name_pools[theme][gender]
        titles = self.title_pools[theme]
        surnames = self.surname_pools[theme]
        
        # Select components
        first_name = random.choice(first_names)
        surname = random.choice(surnames)
        
        # Select title based on role if provided
        if role:
            role_titles = self._get_role_appropriate_titles(role, theme)
            if role_titles:
                title = random.choice(role_titles)
            else:
                title = random.choice(titles) if random.random() < 0.3 else None
        else:
            title = random.choice(titles) if random.random() < 0.3 else None
        
        # Construct name
        if title:
            return f"{title} {first_name} {surname}"
        else:
            return f"{first_name} {surname}"
    
    def _get_role_appropriate_titles(self, role: str, theme: str) -> List[str]:
        """Get titles appropriate for a specific role"""
        role = role.lower()
        
        role_title_map = {
            "fantasy": {
                "warrior": ["Sir", "Captain", "Commander", "Guardian"],
                "guard": ["Captain", "Sergeant", "Commander", "Warden"],
                "scholar": ["Master", "Sage", "Elder", "Keeper"],
                "trader": ["Master", "Lord", "Lady"],
                "priest": ["Father", "Mother", "Sister", "Brother", "Reverend"],
                "wizard": ["Master", "Arcane", "Mystic", "Elder"],
                "blacksmith": ["Master", "Keeper"],
                "healer": ["Sister", "Brother", "Wise", "Sacred"]
            },
            "sci-fi": {
                "guard": ["Captain", "Sergeant", "Commander", "Chief"],
                "engineer": ["Chief", "Technician", "Specialist"],
                "scientist": ["Doctor", "Professor", "Chief", "Prime"],
                "hacker": ["Agent", "Operative", "Cyber", "Digital"],
                "pilot": ["Captain", "Commander", "Lieutenant"],
                "medic": ["Doctor", "Chief", "Medical"]
            },
            "horror": {
                "survivor": ["Old", "Mad", "Lost", "Wretched"],
                "priest": ["Father", "Mother", "Reverend", "Sister"],
                "doctor": ["Doctor", "Professor", "Mad", "Cursed"],
                "scholar": ["Professor", "Ancient", "Forgotten"],
                "cultist": ["Brother", "Sister", "Dark", "Shadow"]
            },
            "cyberpunk": {
                "hacker": ["Agent", "Ghost", "Shadow", "Cyber"],
                "guard": ["Agent", "Chief", "Corp", "Security"],
                "executive": ["Mr.", "Ms.", "Executive", "Boss"],
                "engineer": ["Tech", "Chief", "System", "Grid"],
                "runner": ["Shadow", "Ghost", "Wire", "Net"]
            }
        }
        
        return role_title_map.get(theme, {}).get(role, [])
    
    def generate_item_name(self, item_type: str, theme: str = "fantasy", rarity: str = "common") -> str:
        """
        Generate a thematic item name
        
        Args:
            item_type: Type of item (weapon, armor, potion, etc.)
            theme: Theme for naming
            rarity: Item rarity (common, uncommon, rare, legendary)
            
        Returns:
            Generated item name
        """
        prefixes = self._get_item_prefixes(theme, rarity)
        suffixes = self._get_item_suffixes(theme, rarity)
        base_names = self._get_base_item_names(item_type, theme)
        
        if not base_names:
            return f"mysterious {item_type}"
        
        base_name = random.choice(base_names)
        
        # Higher rarity items are more likely to have prefixes/suffixes
        rarity_chance = {"common": 0.1, "uncommon": 0.3, "rare": 0.6, "legendary": 0.9}
        chance = rarity_chance.get(rarity, 0.1)
        
        if random.random() < chance:
            if random.random() < 0.5 and prefixes:
                prefix = random.choice(prefixes)
                return f"{prefix} {base_name}"
            elif suffixes:
                suffix = random.choice(suffixes)
                return f"{base_name} {suffix}"
        
        return base_name
    
    def _get_item_prefixes(self, theme: str, rarity: str) -> List[str]:
        """Get item prefixes by theme and rarity"""
        prefix_pools = {
            "fantasy": {
                "common": ["Old", "Worn", "Simple", "Basic"],
                "uncommon": ["Fine", "Sharp", "Sturdy", "Blessed"],
                "rare": ["Enchanted", "Magical", "Ancient", "Masterwork"],
                "legendary": ["Divine", "Legendary", "Mythical", "Godforged"]
            },
            "sci-fi": {
                "common": ["Standard", "Basic", "Mass-produced"],
                "uncommon": ["Advanced", "Enhanced", "Military-grade"],
                "rare": ["Prototype", "Experimental", "Quantum"],
                "legendary": ["Alien", "Transcendent", "Reality-bending"]
            },
            "horror": {
                "common": ["Rusty", "Bloodstained", "Tattered"],
                "uncommon": ["Cursed", "Haunted", "Sinister"],
                "rare": ["Eldritch", "Forbidden", "Soul-bound"],
                "legendary": ["Nightmare", "Abyssal", "World-ending"]
            },
            "cyberpunk": {
                "common": ["Cheap", "Knockoff", "Street"],
                "uncommon": ["Corporate", "Military", "Black-market"],
                "rare": ["Prototype", "Illegal", "Zero-day"],
                "legendary": ["Transcendent", "Reality-hacking", "God-tier"]
            }
        }
        
        return prefix_pools.get(theme, prefix_pools["fantasy"]).get(rarity, [])
    
    def _get_item_suffixes(self, theme: str, rarity: str) -> List[str]:
        """Get item suffixes by theme and rarity"""
        suffix_pools = {
            "fantasy": {
                "uncommon": ["of Power", "of Might", "of Grace"],
                "rare": ["of the Eagle", "of Dragonslaying", "of the Ancients"],
                "legendary": ["of the Gods", "of Eternity", "of World-shaking"]
            },
            "sci-fi": {
                "uncommon": ["Mark II", "Enhanced", "v2.0"],
                "rare": ["Prototype", "Quantum Edition", "Neural Link"],
                "legendary": ["Singularity Class", "Reality Shifter", "Universe Breaker"]
            },
            "horror": {
                "uncommon": ["of Torment", "of Whispers", "of Shadows"],
                "rare": ["of the Damned", "of Nightmares", "of the Void"],
                "legendary": ["of Madness", "of the Outer Dark", "of Soul Destruction"]
            },
            "cyberpunk": {
                "uncommon": ["2.0", "Pro", "Elite"],
                "rare": ["Ghost Protocol", "Zero-day", "Black ICE"],
                "legendary": ["Singularity", "Reality Hack", "God Mode"]
            }
        }
        
        return suffix_pools.get(theme, suffix_pools["fantasy"]).get(rarity, [])
    
    def _get_base_item_names(self, item_type: str, theme: str) -> List[str]:
        """Get base item names by type and theme"""
        item_pools = {
            "fantasy": {
                "weapon": ["Sword", "Blade", "Axe", "Hammer", "Bow", "Staff", "Wand", "Dagger"],
                "armor": ["Chainmail", "Plate", "Robes", "Leather", "Shield", "Helm", "Gauntlets"],
                "potion": ["Potion", "Elixir", "Draught", "Tonic", "Brew", "Philter"],
                "scroll": ["Scroll", "Tome", "Grimoire", "Codex", "Manuscript"],
                "jewelry": ["Ring", "Amulet", "Pendant", "Bracelet", "Crown", "Circlet"]
            },
            "sci-fi": {
                "weapon": ["Blaster", "Rifle", "Cannon", "Saber", "Launcher", "Disruptor"],
                "armor": ["Suit", "Exoskeleton", "Shield", "Plating", "Mesh", "Barrier"],
                "tech": ["Scanner", "Communicator", "Interface", "Processor", "Drive", "Core"],
                "consumable": ["Stim", "Booster", "Enhancer", "Patch", "Injector"]
            },
            "horror": {
                "weapon": ["Cleaver", "Blade", "Ritual Knife", "Bone Saw", "Cursed Sword"],
                "artifact": ["Idol", "Tome", "Relic", "Skull", "Bone", "Heart"],
                "consumable": ["Tincture", "Draught", "Blood Vial", "Essence", "Extract"]
            },
            "cyberpunk": {
                "weapon": ["Pistol", "SMG", "Rifle", "Blade", "Shock Baton", "Neural Whip"],
                "tech": ["Chip", "Interface", "Deck", "Wire", "Implant", "Booster"],
                "software": ["Program", "Virus", "ICE", "Daemon", "Script", "Exploit"]
            }
        }
        
        return item_pools.get(theme, item_pools["fantasy"]).get(item_type, [])
    
    def generate_location_name(self, location_type: str, theme: str = "fantasy") -> str:
        """Generate a thematic location name"""
        descriptors = self._get_location_descriptors(theme)
        base_names = self._get_location_base_names(location_type, theme)
        
        if not base_names:
            return f"the {location_type}"
        
        descriptor = random.choice(descriptors)
        base_name = random.choice(base_names)
        
        return f"{descriptor} {base_name}"
    
    def _get_location_descriptors(self, theme: str) -> List[str]:
        """Get location descriptive adjectives by theme"""
        descriptors = {
            "fantasy": ["Ancient", "Forgotten", "Sacred", "Cursed", "Hidden", "Lost", "Mystic", "Golden"],
            "sci-fi": ["Abandoned", "Classified", "Orbital", "Underground", "Quantum", "Neural", "Digital"],
            "horror": ["Cursed", "Haunted", "Forsaken", "Damned", "Twisted", "Nightmare", "Shadow"],
            "cyberpunk": ["Neon", "Corporate", "Underground", "Digital", "Chrome", "Shadow", "Grid"]
        }
        
        return descriptors.get(theme, descriptors["fantasy"])
    
    def _get_location_base_names(self, location_type: str, theme: str) -> List[str]:
        """Get base location names by type and theme"""
        location_pools = {
            "fantasy": {
                "chamber": ["Chamber", "Hall", "Sanctuary", "Vault", "Crypt"],
                "library": ["Library", "Archive", "Study", "Scriptorium", "Repository"],
                "shrine": ["Shrine", "Temple", "Altar", "Chapel", "Sanctum"],
                "armory": ["Armory", "Forge", "Arsenal", "Smithy", "Workshop"]
            },
            "sci-fi": {
                "chamber": ["Bay", "Module", "Hub", "Core", "Station"],
                "laboratory": ["Lab", "Research Center", "Facility", "Complex", "Installation"],
                "server": ["Server Room", "Data Center", "Core", "Matrix", "Network Hub"],
                "medical": ["Medical Bay", "Clinic", "Treatment Center", "Bio-lab"]
            },
            "horror": {
                "chamber": ["Chamber", "Crypt", "Tomb", "Lair", "Den"],
                "ritual": ["Ritual Chamber", "Altar Room", "Sacrifice Chamber", "Blood Pit"],
                "library": ["Study", "Archive", "Forbidden Library", "Tome Vault"]
            },
            "cyberpunk": {
                "chamber": ["Node", "Terminal", "Hub", "Core", "Interface"],
                "server": ["Server Farm", "Data Vault", "Grid Node", "Network Core"],
                "club": ["Club", "Bar", "Den", "Lounge", "Underground"]
            }
        }
        
        return location_pools.get(theme, location_pools["fantasy"]).get(location_type, [])