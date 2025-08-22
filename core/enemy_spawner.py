"""
Enemy Spawning System
Dynamically generates enemies based on room type, theme, and player level
"""
import random
from typing import List, Dict, Any
from .combat_system import Enemy

class EnemySpawner:
    """Generates thematic enemies for different environments"""
    
    def __init__(self):
        self.enemy_templates = self._initialize_enemy_templates()
    
    def _initialize_enemy_templates(self) -> Dict[str, Dict]:
        """Initialize enemy templates by theme and environment"""
        return {
            "fantasy": {
                "dungeon": {
                    "common": [
                        {"name": "Goblin Scout", "type": "goblin", "health_mult": 0.8, "attack_mult": 0.9},
                        {"name": "Skeleton Warrior", "type": "undead", "health_mult": 1.0, "attack_mult": 1.0},
                        {"name": "Giant Rat", "type": "beast", "health_mult": 0.6, "attack_mult": 0.7},
                        {"name": "Cave Spider", "type": "beast", "health_mult": 0.7, "attack_mult": 1.1},
                    ],
                    "uncommon": [
                        {"name": "Orc Berserker", "type": "orc", "health_mult": 1.3, "attack_mult": 1.2},
                        {"name": "Dark Mage", "type": "humanoid", "health_mult": 0.9, "attack_mult": 1.4},
                        {"name": "Stone Golem", "type": "construct", "health_mult": 1.8, "attack_mult": 0.8},
                    ],
                    "rare": [
                        {"name": "Shadow Dragon", "type": "dragon", "health_mult": 2.5, "attack_mult": 1.8},
                        {"name": "Lich", "type": "undead", "health_mult": 2.0, "attack_mult": 2.0},
                        {"name": "Demon Lord", "type": "demon", "health_mult": 2.2, "attack_mult": 1.9},
                    ]
                },
                "forest": {
                    "common": [
                        {"name": "Forest Wolf", "type": "beast", "health_mult": 0.9, "attack_mult": 1.0},
                        {"name": "Wild Boar", "type": "beast", "health_mult": 1.1, "attack_mult": 0.9},
                        {"name": "Tree Sprite", "type": "fey", "health_mult": 0.6, "attack_mult": 1.2},
                    ],
                    "uncommon": [
                        {"name": "Dire Bear", "type": "beast", "health_mult": 1.6, "attack_mult": 1.1},
                        {"name": "Forest Guardian", "type": "elemental", "health_mult": 1.4, "attack_mult": 1.3},
                    ],
                    "rare": [
                        {"name": "Ancient Treant", "type": "plant", "health_mult": 2.8, "attack_mult": 1.5},
                    ]
                }
            },
            "sci-fi": {
                "space_station": {
                    "common": [
                        {"name": "Security Droid", "type": "robot", "health_mult": 1.0, "attack_mult": 1.0},
                        {"name": "Maintenance Bot", "type": "robot", "health_mult": 0.8, "attack_mult": 0.7},
                        {"name": "Alien Parasite", "type": "alien", "health_mult": 0.6, "attack_mult": 1.1},
                    ],
                    "uncommon": [
                        {"name": "Combat Android", "type": "robot", "health_mult": 1.4, "attack_mult": 1.3},
                        {"name": "Hostile Alien", "type": "alien", "health_mult": 1.1, "attack_mult": 1.4},
                    ],
                    "rare": [
                        {"name": "AI Core Guardian", "type": "robot", "health_mult": 2.2, "attack_mult": 1.7},
                        {"name": "Alien Queen", "type": "alien", "health_mult": 2.5, "attack_mult": 1.9},
                    ]
                }
            },
            "horror": {
                "mansion": {
                    "common": [
                        {"name": "Possessed Doll", "type": "undead", "health_mult": 0.7, "attack_mult": 0.9},
                        {"name": "Shadow Figure", "type": "spirit", "health_mult": 0.8, "attack_mult": 1.1},
                        {"name": "Zombie Servant", "type": "undead", "health_mult": 1.0, "attack_mult": 0.8},
                    ],
                    "uncommon": [
                        {"name": "Vengeful Ghost", "type": "spirit", "health_mult": 1.2, "attack_mult": 1.3},
                        {"name": "Flesh Abomination", "type": "aberration", "health_mult": 1.5, "attack_mult": 1.2},
                    ],
                    "rare": [
                        {"name": "Ancient Evil", "type": "elder_horror", "health_mult": 2.3, "attack_mult": 2.0},
                        {"name": "Nightmare Incarnate", "type": "aberration", "health_mult": 2.1, "attack_mult": 1.8},
                    ]
                }
            },
            "cyberpunk": {
                "corporate": {
                    "common": [
                        {"name": "Corporate Security", "type": "human", "health_mult": 0.9, "attack_mult": 1.0},
                        {"name": "Street Gang Member", "type": "human", "health_mult": 0.8, "attack_mult": 0.9},
                        {"name": "Surveillance Drone", "type": "robot", "health_mult": 0.6, "attack_mult": 1.1},
                    ],
                    "uncommon": [
                        {"name": "Cybernetic Enforcer", "type": "cyborg", "health_mult": 1.3, "attack_mult": 1.2},
                        {"name": "Rogue AI Avatar", "type": "digital", "health_mult": 1.1, "attack_mult": 1.4},
                    ],
                    "rare": [
                        {"name": "Corporate Assassin", "type": "human", "health_mult": 1.8, "attack_mult": 2.1},
                        {"name": "Military Cyborg", "type": "cyborg", "health_mult": 2.4, "attack_mult": 1.6},
                    ]
                }
            }
        }
    
    def spawn_enemy(self, room_type: str, theme: str, player_level: int, depth: int) -> Enemy:
        """Spawn a single enemy based on parameters"""
        # Get theme templates
        theme_data = self.enemy_templates.get(theme, self.enemy_templates["fantasy"])
        
        # Match room type to environment
        environment = self._match_environment(room_type, theme)
        env_data = theme_data.get(environment, list(theme_data.values())[0])
        
        # Choose rarity based on depth and level
        rarity = self._determine_rarity(depth, player_level)
        enemy_pool = env_data.get(rarity, env_data.get("common", []))
        
        if not enemy_pool:
            return self._create_default_enemy(theme, player_level)
        
        # Select enemy template
        template = random.choice(enemy_pool)
        
        # Scale enemy to player level and depth
        enemy_level = self._calculate_enemy_level(player_level, depth, rarity)
        base_health = 30 + (enemy_level * 12)
        enemy_health = int(base_health * template["health_mult"])
        
        # Create enemy
        enemy = Enemy(
            name=template["name"],
            health=enemy_health,
            level=enemy_level,
            enemy_type=template["type"],
            theme=theme
        )
        
        # Apply template modifiers
        enemy.attack = int(enemy.attack * template["attack_mult"])
        
        return enemy
    
    def spawn_encounter(self, room_type: str, theme: str, player_level: int, depth: int) -> List[Enemy]:
        """Spawn a complete encounter (1-3 enemies)"""
        # Determine number of enemies
        if depth <= 3:
            num_enemies = random.choices([1, 2], weights=[70, 30])[0]  # 70% single, 30% pair
        elif depth <= 10:
            num_enemies = random.choices([1, 2, 3], weights=[50, 40, 10])[0]  # More variety
        else:
            num_enemies = random.choices([1, 2, 3], weights=[40, 45, 15])[0]  # Higher chance of groups
        
        enemies = []
        for _ in range(num_enemies):
            enemy = self.spawn_enemy(room_type, theme, player_level, depth)
            enemies.append(enemy)
        
        return enemies
    
    def _match_environment(self, room_type: str, theme: str) -> str:
        """Match room type to enemy environment"""
        environment_mapping = {
            "fantasy": {
                "chamber": "dungeon", "hallway": "dungeon", "cavern": "dungeon",
                "tunnel": "dungeon", "library": "dungeon", "shrine": "dungeon",
                "forest": "forest", "grove": "forest"
            },
            "sci-fi": {
                "chamber": "space_station", "hallway": "space_station", "laboratory": "space_station",
                "bridge": "space_station", "engine": "space_station"
            },
            "horror": {
                "chamber": "mansion", "hallway": "mansion", "library": "mansion",
                "attic": "mansion", "basement": "mansion"
            },
            "cyberpunk": {
                "office": "corporate", "server_room": "corporate", "laboratory": "corporate",
                "security": "corporate"
            }
        }
        
        theme_envs = environment_mapping.get(theme, {})
        return theme_envs.get(room_type, list(theme_envs.values())[0] if theme_envs else "dungeon")
    
    def _determine_rarity(self, depth: int, player_level: int) -> str:
        """Determine enemy rarity based on depth and player level"""
        # Base chances
        rare_chance = min(0.15, depth * 0.01 + player_level * 0.005)  # Max 15% rare
        uncommon_chance = min(0.35, depth * 0.02 + player_level * 0.01)  # Max 35% uncommon
        
        roll = random.random()
        if roll < rare_chance:
            return "rare"
        elif roll < rare_chance + uncommon_chance:
            return "uncommon"
        else:
            return "common"
    
    def _calculate_enemy_level(self, player_level: int, depth: int, rarity: str) -> int:
        """Calculate appropriate enemy level"""
        base_level = player_level + (depth // 5)  # Every 5 depths = +1 level
        
        # Rarity modifiers
        if rarity == "rare":
            base_level += random.randint(1, 3)
        elif rarity == "uncommon":
            base_level += random.randint(0, 2)
        
        # Add some randomness
        level_variance = random.randint(-1, 2)
        final_level = max(1, base_level + level_variance)
        
        return final_level
    
    def _create_default_enemy(self, theme: str, level: int) -> Enemy:
        """Create a default enemy when no template found"""
        default_names = {
            "fantasy": "Wandering Monster",
            "sci-fi": "Unknown Entity", 
            "horror": "Lurking Terror",
            "cyberpunk": "System Glitch"
        }
        
        name = default_names.get(theme, "Strange Creature")
        health = 25 + (level * 10)
        
        return Enemy(name, health, level, "unknown", theme)
    
    def should_spawn_enemy(self, room_visited_before: bool, depth: int, player_level: int) -> bool:
        """Determine if an enemy should spawn in this room"""
        # Never spawn in previously visited rooms
        if room_visited_before:
            return False
        
        # Base spawn chance increases with depth
        base_chance = min(0.6, 0.3 + (depth * 0.02))  # 30% base, up to 60%
        
        # Level scaling
        if player_level <= 3:
            base_chance *= 0.7  # Easier for new players
        elif player_level >= 10:
            base_chance *= 1.2  # More challenging for veterans
        
        return random.random() < base_chance