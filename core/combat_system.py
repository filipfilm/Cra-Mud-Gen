"""
Combat System for Dun-Gen
Handles tactical turn-based combat, health, experience, and progression
"""
import random
import math
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

class ActionType(Enum):
    ATTACK = "attack"
    DEFEND = "defend"
    USE_ITEM = "use_item"
    CAST_SPELL = "cast_spell"
    FLEE = "flee"

class DamageType(Enum):
    PHYSICAL = "physical"
    FIRE = "fire"
    ICE = "ice"
    ELECTRIC = "electric"
    POISON = "poison"
    DARK = "dark"
    LIGHT = "light"

class CombatAction:
    """Represents a combat action"""
    def __init__(self, action_type: ActionType, target: str, damage: int = 0, 
                 damage_type: DamageType = DamageType.PHYSICAL, effects: List[str] = None):
        self.action_type = action_type
        self.target = target
        self.damage = damage
        self.damage_type = damage_type
        self.effects = effects or []
        self.accuracy = 0.85  # Base 85% hit chance
        self.critical_chance = 0.1  # 10% crit chance

class Combatant:
    """Base class for all combat participants"""
    def __init__(self, name: str, health: int, level: int = 1):
        self.name = name
        self.max_health = health
        self.current_health = health
        self.level = level
        
        # Combat stats
        self.attack = 10 + (level * 2)
        self.defense = 5 + level
        self.speed = 10 + random.randint(-3, 3)
        
        # Status effects
        self.status_effects = {}  # effect_name -> turns_remaining
        self.is_defending = False
        self.is_dead = False
        
        # Resistances (0.0 = immune, 1.0 = normal damage, 2.0 = double damage)
        self.resistances = {damage_type: 1.0 for damage_type in DamageType}
    
    def take_damage(self, amount: int, damage_type: DamageType = DamageType.PHYSICAL) -> int:
        """Take damage with resistance calculations"""
        if self.is_dead:
            return 0
            
        # Apply resistance
        resistance = self.resistances.get(damage_type, 1.0)
        actual_damage = int(amount * resistance)
        
        # Apply defense
        if self.is_defending:
            actual_damage = int(actual_damage * 0.5)  # Defending halves damage
        
        actual_damage = max(1, actual_damage - self.defense // 2)  # Minimum 1 damage
        
        self.current_health = max(0, self.current_health - actual_damage)
        
        if self.current_health <= 0:
            self.is_dead = True
            
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Heal damage"""
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        return self.current_health - old_health
    
    def apply_status_effect(self, effect: str, duration: int):
        """Apply a status effect"""
        self.status_effects[effect] = duration
    
    def process_status_effects(self) -> List[str]:
        """Process status effects and return descriptions"""
        messages = []
        effects_to_remove = []
        
        for effect, turns in self.status_effects.items():
            if effect == "poison":
                damage = max(1, self.level)
                self.take_damage(damage, DamageType.POISON)
                messages.append(f"{self.name} takes {damage} poison damage!")
            elif effect == "regeneration":
                healing = max(2, self.level * 2)
                healed = self.heal(healing)
                messages.append(f"{self.name} regenerates {healed} health!")
            elif effect == "burn":
                damage = max(2, self.level + 1)
                self.take_damage(damage, DamageType.FIRE)
                messages.append(f"{self.name} burns for {damage} damage!")
            
            # Decrease duration
            self.status_effects[effect] -= 1
            if self.status_effects[effect] <= 0:
                effects_to_remove.append(effect)
        
        # Remove expired effects
        for effect in effects_to_remove:
            del self.status_effects[effect]
            messages.append(f"{self.name} recovers from {effect}!")
        
        return messages

class Enemy(Combatant):
    """Enemy combatant with AI"""
    def __init__(self, name: str, health: int, level: int, enemy_type: str, theme: str = "fantasy"):
        super().__init__(name, health, level)
        self.enemy_type = enemy_type
        self.theme = theme
        self.experience_reward = level * 10 + random.randint(5, 15)
        self.gold_reward = level * 5 + random.randint(1, 10)
        self.loot_table = self._generate_loot_table()
        
        # AI behavior
        self.aggression = 0.7  # How likely to attack vs defend
        self.intelligence = 0.5  # How smart tactical decisions are
        
        # Theme-based adjustments
        self._apply_theme_modifiers()
    
    def _apply_theme_modifiers(self):
        """Apply theme-specific enemy modifiers"""
        if self.theme == "fantasy":
            if "dragon" in self.enemy_type.lower():
                self.resistances[DamageType.FIRE] = 0.2
                self.resistances[DamageType.ICE] = 2.0
                self.attack *= 1.5
            elif "undead" in self.enemy_type.lower():
                self.resistances[DamageType.DARK] = 0.1
                self.resistances[DamageType.LIGHT] = 2.0
        elif self.theme == "sci-fi":
            if "robot" in self.enemy_type.lower():
                self.resistances[DamageType.ELECTRIC] = 0.3
                self.resistances[DamageType.PHYSICAL] = 0.8
                self.defense += 3
        elif self.theme == "horror":
            self.resistances[DamageType.DARK] = 0.5
            self.resistances[DamageType.LIGHT] = 1.5
            # Horror enemies are more unpredictable
            self.intelligence = random.uniform(0.2, 0.8)
    
    def _generate_loot_table(self) -> List[Tuple[str, float]]:
        """Generate loot table with item name and drop chance"""
        loot = []
        
        # Common items (60% chance)
        if self.level <= 5:
            loot.extend([("healing potion", 0.4), ("rusty sword", 0.2), ("leather armor", 0.15)])
        elif self.level <= 10:
            loot.extend([("magic potion", 0.3), ("silver sword", 0.15), ("chainmail", 0.1)])
        else:
            loot.extend([("greater healing potion", 0.25), ("enchanted blade", 0.1), ("plate armor", 0.05)])
        
        # Rare items (10-20% chance)
        if self.level >= 5:
            loot.extend([("rare gem", 0.1), ("magic scroll", 0.08)])
        if self.level >= 10:
            loot.extend([("legendary artifact", 0.02), ("ancient rune", 0.05)])
        
        return loot
    
    def choose_action(self, player_health: int, player_level: int) -> ActionType:
        """AI chooses next action"""
        # Simple AI logic
        health_ratio = self.current_health / self.max_health
        
        # Low health - more likely to defend or flee
        if health_ratio < 0.3:
            if random.random() < 0.3:
                return ActionType.FLEE if self.level < player_level else ActionType.DEFEND
        
        # High aggression or player is weak - attack
        if random.random() < self.aggression or player_health < 30:
            return ActionType.ATTACK
        
        # Sometimes defend
        if random.random() < 0.2:
            return ActionType.DEFEND
        
        return ActionType.ATTACK

class CombatSystem:
    """Manages turn-based combat encounters"""
    
    def __init__(self):
        self.combat_log = []
        self.turn_count = 0
    
    def start_combat(self, player, enemies: List[Enemy]) -> Dict[str, Any]:
        """Start a combat encounter"""
        self.combat_log = []
        self.turn_count = 0
        
        # Determine initiative order (speed-based)
        all_combatants = [player] + enemies
        initiative_order = sorted(all_combatants, key=lambda x: x.speed + random.randint(0, 5), reverse=True)
        
        self.log(f"Combat begins! Initiative order: {', '.join([c.name for c in initiative_order])}")
        
        return {
            "status": "combat_started",
            "initiative": [c.name for c in initiative_order],
            "enemies": [{"name": e.name, "health": e.current_health, "max_health": e.max_health} for e in enemies]
        }
    
    def execute_turn(self, attacker: Combatant, action: CombatAction, targets: List[Combatant]) -> Dict[str, Any]:
        """Execute a single combat turn"""
        results = {"messages": [], "damage_dealt": 0, "effects": []}
        
        if attacker.is_dead:
            return results
        
        if action.action_type == ActionType.ATTACK:
            target = self._find_target(action.target, targets)
            if target and not target.is_dead:
                # Calculate hit chance
                hit_roll = random.random()
                if hit_roll <= action.accuracy:
                    # Hit! Calculate damage
                    base_damage = attacker.attack + random.randint(1, 6)
                    
                    # Critical hit?
                    is_critical = random.random() <= action.critical_chance
                    if is_critical:
                        base_damage *= 2
                        results["effects"].append("critical")
                    
                    # Apply damage
                    damage_dealt = target.take_damage(base_damage, action.damage_type)
                    results["damage_dealt"] = damage_dealt
                    
                    crit_text = " (CRITICAL HIT!)" if is_critical else ""
                    self.log(f"{attacker.name} attacks {target.name} for {damage_dealt} damage{crit_text}")
                    
                    if target.is_dead:
                        self.log(f"{target.name} has been defeated!")
                        results["effects"].append("enemy_death")
                else:
                    self.log(f"{attacker.name} attacks {target.name} but misses!")
                    
        elif action.action_type == ActionType.DEFEND:
            attacker.is_defending = True
            self.log(f"{attacker.name} takes a defensive stance")
            
        elif action.action_type == ActionType.FLEE:
            if random.random() < 0.6:  # 60% flee success
                results["effects"].append("flee_success")
                self.log(f"{attacker.name} flees from combat!")
            else:
                self.log(f"{attacker.name} tries to flee but fails!")
        
        # Process status effects
        status_messages = attacker.process_status_effects()
        for msg in status_messages:
            self.log(msg)
        
        results["messages"] = self.combat_log[-5:]  # Return last 5 messages
        return results
    
    def _find_target(self, target_name: str, possible_targets: List[Combatant]) -> Optional[Combatant]:
        """Find target by name"""
        for target in possible_targets:
            if target_name.lower() in target.name.lower() and not target.is_dead:
                return target
        return None
    
    def log(self, message: str):
        """Add message to combat log"""
        self.combat_log.append(message)
    
    def is_combat_over(self, player, enemies: List[Enemy]) -> Tuple[bool, str]:
        """Check if combat is over and return result"""
        if player.is_dead:
            return True, "defeat"
        
        living_enemies = [e for e in enemies if not e.is_dead]
        if not living_enemies:
            return True, "victory"
            
        return False, "ongoing"
    
    def calculate_rewards(self, defeated_enemies: List[Enemy], player_level: int) -> Dict[str, Any]:
        """Calculate experience, gold, and loot rewards"""
        total_exp = 0
        total_gold = 0
        loot_found = []
        
        for enemy in defeated_enemies:
            if enemy.is_dead:
                # Experience with level scaling
                exp_reward = enemy.experience_reward
                if enemy.level > player_level:
                    exp_reward = int(exp_reward * 1.2)  # Bonus for defeating higher level enemies
                elif enemy.level < player_level:
                    exp_reward = int(exp_reward * 0.8)  # Less exp for lower level enemies
                
                total_exp += exp_reward
                total_gold += enemy.gold_reward
                
                # Roll for loot
                for item, chance in enemy.loot_table:
                    if random.random() < chance:
                        loot_found.append(item)
        
        return {
            "experience": total_exp,
            "gold": total_gold,
            "loot": loot_found
        }

class HealthSystem:
    """Manages health, healing, and health-related mechanics"""
    
    @staticmethod
    def calculate_max_health(level: int, base_health: int = 100) -> int:
        """Calculate maximum health based on level"""
        return base_health + (level - 1) * 15  # +15 HP per level
    
    @staticmethod
    def natural_regeneration(current_health: int, max_health: int, level: int) -> int:
        """Calculate natural health regeneration over time"""
        if current_health >= max_health:
            return 0
        
        # Regenerate 1-2% of max health, minimum 1
        regen_amount = max(1, int(max_health * 0.02) + (level // 10))
        return min(regen_amount, max_health - current_health)
    
    @staticmethod
    def use_healing_item(item_name: str, level: int) -> Tuple[int, str]:
        """Use a healing item and return healing amount and description"""
        healing_items = {
            "healing potion": (25 + level * 2, "restores moderate health"),
            "greater healing potion": (50 + level * 3, "restores significant health"),
            "magic elixir": (100 + level * 5, "fully restores health and vitality"),
            "bandages": (10 + level, "provides basic healing"),
            "herb bundle": (15 + level, "natural healing herbs"),
        }
        
        item_lower = item_name.lower()
        for item, (healing, desc) in healing_items.items():
            if item in item_lower:
                return healing, desc
                
        return 5, "provides minimal healing"

class ExperienceSystem:
    """Manages experience points and leveling"""
    
    @staticmethod
    def calculate_level_from_exp(experience: int) -> int:
        """Calculate level based on total experience"""
        if experience < 100:
            return 1
        
        # Level formula: roughly 100 * level^1.5 experience per level
        level = 1
        exp_needed = 0
        
        while experience >= exp_needed:
            level += 1
            exp_needed += int(100 * (level ** 1.3))
        
        return max(1, level - 1)
    
    @staticmethod
    def exp_needed_for_next_level(current_level: int) -> int:
        """Calculate experience needed for next level"""
        return int(100 * ((current_level + 1) ** 1.3))
    
    @staticmethod
    def exp_progress_to_next_level(current_exp: int, current_level: int) -> Tuple[int, int]:
        """Get current progress toward next level"""
        exp_for_current = sum(int(100 * (i ** 1.3)) for i in range(2, current_level + 1))
        exp_for_next = exp_for_current + ExperienceSystem.exp_needed_for_next_level(current_level)
        
        progress = current_exp - exp_for_current
        needed = exp_for_next - exp_for_current
        
        return progress, needed
    
    @staticmethod
    def grant_experience(player, amount: int) -> Dict[str, Any]:
        """Grant experience and handle level ups"""
        old_level = ExperienceSystem.calculate_level_from_exp(player.stats["experience"])
        player.stats["experience"] += amount
        new_level = ExperienceSystem.calculate_level_from_exp(player.stats["experience"])
        
        result = {
            "exp_gained": amount,
            "leveled_up": new_level > old_level,
            "old_level": old_level,
            "new_level": new_level,
            "benefits": []
        }
        
        if result["leveled_up"]:
            # Update stats
            player.stats["level"] = new_level
            
            # Increase max health
            old_max_health = player.max_health if hasattr(player, 'max_health') else 100
            new_max_health = HealthSystem.calculate_max_health(new_level)
            health_gained = new_max_health - old_max_health
            
            if hasattr(player, 'max_health'):
                player.max_health = new_max_health
                player.health = min(player.health + health_gained, new_max_health)  # Heal on level up
            
            result["benefits"].append(f"Maximum health increased by {health_gained}!")
            result["benefits"].append(f"Health restored by {health_gained}!")
            
            # Increase other stats
            if hasattr(player, 'attack'):
                player.attack += 2
                result["benefits"].append("Attack power increased!")
            if hasattr(player, 'defense'):
                player.defense += 1
                result["benefits"].append("Defense improved!")
        
        return result