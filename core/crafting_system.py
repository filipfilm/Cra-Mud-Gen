"""
Advanced Crafting System for Cra-mud-gen
Allows players to craft items, enchant equipment, and create unique artifacts
"""
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class CraftingSkill(Enum):
    """Different crafting disciplines"""
    BLACKSMITHING = "blacksmithing"
    ALCHEMY = "alchemy"
    ENCHANTING = "enchanting"
    ARTIFICING = "artificing"
    COOKING = "cooking"
    TAILORING = "tailoring"
    JEWELCRAFTING = "jewelcrafting"
    RUNECRAFTING = "runecrafting"


class ItemQuality(Enum):
    """Crafted item quality tiers"""
    CRUDE = 0
    COMMON = 1
    FINE = 2
    SUPERIOR = 3
    EXCEPTIONAL = 4
    MASTERWORK = 5
    LEGENDARY = 6
    MYTHICAL = 7


@dataclass
class CraftingRecipe:
    """Represents a crafting recipe"""
    name: str
    skill: CraftingSkill
    skill_level_required: int
    ingredients: Dict[str, int]  # item_name -> quantity
    tools_required: List[str]
    output: str
    output_quantity: int
    base_quality: ItemQuality
    success_chance: float
    experience_reward: int
    special_effects: List[str] = None
    unlock_condition: str = None
    
    def __post_init__(self):
        if self.special_effects is None:
            self.special_effects = []


@dataclass
class CraftedItem:
    """Represents a crafted item with unique properties"""
    name: str
    base_type: str
    quality: ItemQuality
    durability: int
    max_durability: int
    enchantments: List[str]
    creator_name: str
    creation_date: str
    unique_properties: Dict[str, Any]
    soul_bound: bool = False
    
    def get_display_name(self) -> str:
        """Get item name with quality prefix"""
        quality_prefixes = {
            ItemQuality.CRUDE: "Crude",
            ItemQuality.COMMON: "",
            ItemQuality.FINE: "Fine",
            ItemQuality.SUPERIOR: "Superior",
            ItemQuality.EXCEPTIONAL: "Exceptional",
            ItemQuality.MASTERWORK: "Masterwork",
            ItemQuality.LEGENDARY: "Legendary",
            ItemQuality.MYTHICAL: "Mythical"
        }
        prefix = quality_prefixes.get(self.quality, "")
        suffix = f" (by {self.creator_name})" if self.quality.value >= ItemQuality.MASTERWORK.value else ""
        return f"{prefix} {self.name}{suffix}".strip()


class CraftingSystem:
    """Advanced crafting system with progression and discovery"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.recipes = self._initialize_recipes()
        self.discovered_recipes = set()
        self.crafting_stations = self._initialize_stations()
        
    def _initialize_recipes(self) -> Dict[str, CraftingRecipe]:
        """Initialize all crafting recipes"""
        recipes = {}
        
        # Blacksmithing recipes
        recipes["iron_sword"] = CraftingRecipe(
            name="Iron Sword",
            skill=CraftingSkill.BLACKSMITHING,
            skill_level_required=1,
            ingredients={"iron_ore": 3, "coal": 1},
            tools_required=["anvil", "hammer"],
            output="iron_sword",
            output_quantity=1,
            base_quality=ItemQuality.COMMON,
            success_chance=0.8,
            experience_reward=10
        )
        
        recipes["dragon_blade"] = CraftingRecipe(
            name="Dragon Blade",
            skill=CraftingSkill.BLACKSMITHING,
            skill_level_required=10,
            ingredients={"dragon_scale": 2, "mythril_ore": 5, "fire_essence": 1},
            tools_required=["ancient_anvil", "runic_hammer"],
            output="dragon_blade",
            output_quantity=1,
            base_quality=ItemQuality.LEGENDARY,
            success_chance=0.3,
            experience_reward=500,
            special_effects=["fire_damage", "dragon_slaying"],
            unlock_condition="defeat_dragon"
        )
        
        # Alchemy recipes
        recipes["healing_potion"] = CraftingRecipe(
            name="Healing Potion",
            skill=CraftingSkill.ALCHEMY,
            skill_level_required=1,
            ingredients={"red_herb": 2, "spring_water": 1},
            tools_required=["cauldron"],
            output="healing_potion",
            output_quantity=3,
            base_quality=ItemQuality.COMMON,
            success_chance=0.9,
            experience_reward=5
        )
        
        recipes["philosopher_stone"] = CraftingRecipe(
            name="Philosopher's Stone",
            skill=CraftingSkill.ALCHEMY,
            skill_level_required=20,
            ingredients={"mercury": 1, "sulfur": 1, "salt": 1, "quintessence": 1},
            tools_required=["alchemical_laboratory"],
            output="philosopher_stone",
            output_quantity=1,
            base_quality=ItemQuality.MYTHICAL,
            success_chance=0.1,
            experience_reward=2000,
            special_effects=["transmutation", "immortality"],
            unlock_condition="master_alchemist"
        )
        
        # Enchanting recipes
        recipes["flame_enchantment"] = CraftingRecipe(
            name="Flame Enchantment",
            skill=CraftingSkill.ENCHANTING,
            skill_level_required=5,
            ingredients={"fire_crystal": 1, "enchanting_dust": 3},
            tools_required=["enchanting_table"],
            output="flame_enchantment",
            output_quantity=1,
            base_quality=ItemQuality.FINE,
            success_chance=0.6,
            experience_reward=25,
            special_effects=["adds_fire_damage"]
        )
        
        # Cooking recipes
        recipes["dragon_steak"] = CraftingRecipe(
            name="Dragon Steak",
            skill=CraftingSkill.COOKING,
            skill_level_required=8,
            ingredients={"dragon_meat": 1, "exotic_spices": 2, "fire_pepper": 1},
            tools_required=["master_kitchen"],
            output="dragon_steak",
            output_quantity=1,
            base_quality=ItemQuality.SUPERIOR,
            success_chance=0.5,
            experience_reward=40,
            special_effects=["fire_resistance_buff", "strength_buff"]
        )
        
        return recipes
    
    def _initialize_stations(self) -> Dict[str, Dict]:
        """Initialize crafting station types"""
        return {
            "basic_workbench": {
                "skills": [CraftingSkill.BLACKSMITHING, CraftingSkill.TAILORING],
                "quality_bonus": 0,
                "success_bonus": 0.0
            },
            "forge": {
                "skills": [CraftingSkill.BLACKSMITHING],
                "quality_bonus": 1,
                "success_bonus": 0.1
            },
            "alchemical_laboratory": {
                "skills": [CraftingSkill.ALCHEMY],
                "quality_bonus": 2,
                "success_bonus": 0.2
            },
            "enchanting_altar": {
                "skills": [CraftingSkill.ENCHANTING, CraftingSkill.RUNECRAFTING],
                "quality_bonus": 1,
                "success_bonus": 0.15
            },
            "master_workshop": {
                "skills": list(CraftingSkill),  # All skills
                "quality_bonus": 3,
                "success_bonus": 0.3
            }
        }
    
    def craft_item(self, recipe_name: str, player_skills: Dict[CraftingSkill, int], 
                   station: str = None, luck_bonus: float = 0.0) -> Tuple[bool, Optional[CraftedItem], str]:
        """
        Attempt to craft an item
        
        Returns:
            (success, crafted_item, message)
        """
        if recipe_name not in self.recipes:
            return False, None, "Recipe not found!"
        
        recipe = self.recipes[recipe_name]
        
        # Check skill requirement
        player_skill = player_skills.get(recipe.skill, 0)
        if player_skill < recipe.skill_level_required:
            return False, None, f"Requires {recipe.skill.value} level {recipe.skill_level_required}"
        
        # Calculate success chance
        base_chance = recipe.success_chance
        skill_bonus = (player_skill - recipe.skill_level_required) * 0.02
        station_bonus = 0.0
        
        if station and station in self.crafting_stations:
            station_data = self.crafting_stations[station]
            if recipe.skill in station_data["skills"]:
                station_bonus = station_data["success_bonus"]
        
        total_chance = min(0.95, base_chance + skill_bonus + station_bonus + luck_bonus)
        
        # Roll for success
        if random.random() > total_chance:
            # Crafting failure
            if random.random() < 0.3:  # 30% chance to lose some materials
                return False, None, "Crafting failed! Some materials were lost."
            else:
                return False, None, "Crafting failed! Materials preserved."
        
        # Determine quality
        quality = self._determine_quality(recipe, player_skill, station, luck_bonus)
        
        # Create the crafted item
        import datetime
        crafted_item = CraftedItem(
            name=recipe.output,
            base_type=recipe.output,
            quality=quality,
            durability=100 + (quality.value * 20),
            max_durability=100 + (quality.value * 20),
            enchantments=[],
            creator_name="Player",  # Would be actual player name
            creation_date=datetime.datetime.now().isoformat(),
            unique_properties=self._generate_unique_properties(recipe, quality)
        )
        
        # Add special effects for high quality
        if quality.value >= ItemQuality.EXCEPTIONAL.value:
            crafted_item.enchantments.extend(recipe.special_effects or [])
        
        # Chance for masterwork to be soul-bound
        if quality == ItemQuality.MASTERWORK:
            crafted_item.soul_bound = random.random() < 0.5
        
        message = f"Successfully crafted {crafted_item.get_display_name()}!"
        if quality.value >= ItemQuality.EXCEPTIONAL.value:
            message += " It radiates with power!"
        
        return True, crafted_item, message
    
    def _determine_quality(self, recipe: CraftingRecipe, skill_level: int, 
                          station: str, luck_bonus: float) -> ItemQuality:
        """Determine the quality of crafted item"""
        base_quality = recipe.base_quality.value
        
        # Skill bonus
        skill_excess = skill_level - recipe.skill_level_required
        quality_from_skill = skill_excess // 5  # Every 5 levels above requirement
        
        # Station bonus
        station_quality_bonus = 0
        if station and station in self.crafting_stations:
            station_quality_bonus = self.crafting_stations[station]["quality_bonus"]
        
        # Random quality variation
        quality_roll = random.random() + luck_bonus
        if quality_roll > 0.95:
            random_bonus = 2
        elif quality_roll > 0.8:
            random_bonus = 1
        else:
            random_bonus = 0
        
        final_quality = base_quality + quality_from_skill + station_quality_bonus + random_bonus
        final_quality = min(final_quality, ItemQuality.MYTHICAL.value)
        
        return ItemQuality(final_quality)
    
    def _generate_unique_properties(self, recipe: CraftingRecipe, quality: ItemQuality) -> Dict[str, Any]:
        """Generate unique properties based on quality"""
        properties = {}
        
        if quality.value >= ItemQuality.FINE.value:
            properties["durability_bonus"] = quality.value * 10
        
        if quality.value >= ItemQuality.SUPERIOR.value:
            properties["damage_bonus"] = quality.value * 2
            properties["special_proc_chance"] = 0.05 * quality.value
        
        if quality.value >= ItemQuality.EXCEPTIONAL.value:
            properties["unique_ability"] = self._generate_unique_ability(recipe)
        
        if quality == ItemQuality.MYTHICAL:
            properties["legendary_effect"] = self._generate_legendary_effect(recipe)
        
        return properties
    
    def _generate_unique_ability(self, recipe: CraftingRecipe) -> str:
        """Generate a unique ability for exceptional items"""
        abilities = {
            CraftingSkill.BLACKSMITHING: ["Armor Piercing", "Whirlwind Strike", "Parry Master"],
            CraftingSkill.ALCHEMY: ["Regeneration Aura", "Poison Cloud", "Transmutation"],
            CraftingSkill.ENCHANTING: ["Spell Echo", "Mana Steal", "Elemental Burst"],
            CraftingSkill.TAILORING: ["Shadow Cloak", "Ethereal Form", "Speed Boost"],
            CraftingSkill.JEWELCRAFTING: ["Gem Resonance", "Crystal Shield", "Prismatic Beam"]
        }
        
        skill_abilities = abilities.get(recipe.skill, ["Special Power"])
        return random.choice(skill_abilities)
    
    def _generate_legendary_effect(self, recipe: CraftingRecipe) -> str:
        """Generate legendary effect for mythical items"""
        if self.llm:
            prompt = f"Generate a legendary effect name for a mythical {recipe.output}. Keep it under 5 words and epic."
            try:
                # Check if llm is the interface or the actual LLM
                if hasattr(self.llm, 'llm'):
                    response = self.llm.llm.generate_game_response(prompt, {"theme": "fantasy"})
                else:
                    response = self.llm.generate_game_response(prompt, {"theme": "fantasy"})
                return response.strip()
            except:
                pass
        
        # Fallback legendary effects
        effects = [
            "Reality Bender", "Soul Reaper", "Time Shatterer",
            "Void Walker", "Star Forged", "Dragon's Wrath",
            "Phoenix Rebirth", "Cosmic Harmony", "Eternal Guardian"
        ]
        return random.choice(effects)
    
    def discover_recipe(self, player, item_examined: str = None, npc_taught: str = None, 
                       book_read: str = None) -> Optional[CraftingRecipe]:
        """Discover new recipes through various means"""
        undiscovered = set(self.recipes.keys()) - self.discovered_recipes
        
        if not undiscovered:
            return None
        
        # Different discovery methods
        if item_examined:
            # Discover related recipes by examining items
            related_recipes = [r for r in undiscovered 
                             if item_examined in self.recipes[r].ingredients]
            if related_recipes:
                chosen = random.choice(related_recipes)
                self.discovered_recipes.add(chosen)
                return self.recipes[chosen]
        
        elif npc_taught:
            # NPCs teach specific recipe types
            npc_specialties = {
                "blacksmith": CraftingSkill.BLACKSMITHING,
                "alchemist": CraftingSkill.ALCHEMY,
                "enchanter": CraftingSkill.ENCHANTING,
                "chef": CraftingSkill.COOKING
            }
            
            for npc_type, skill in npc_specialties.items():
                if npc_type in npc_taught.lower():
                    skill_recipes = [r for r in undiscovered 
                                   if self.recipes[r].skill == skill]
                    if skill_recipes:
                        chosen = random.choice(skill_recipes)
                        self.discovered_recipes.add(chosen)
                        return self.recipes[chosen]
        
        elif book_read:
            # Books can teach any recipe
            if undiscovered:
                chosen = random.choice(list(undiscovered))
                self.discovered_recipes.add(chosen)
                return self.recipes[chosen]
        
        return None
    
    def enhance_item(self, item: CraftedItem, enhancement_type: str, 
                     materials: Dict[str, int]) -> Tuple[bool, str]:
        """Enhance an existing crafted item"""
        enhancement_types = {
            "sharpen": {
                "materials": {"whetstone": 1},
                "effect": "damage_bonus",
                "value": 5
            },
            "reinforce": {
                "materials": {"metal_plates": 2},
                "effect": "durability_bonus", 
                "value": 50
            },
            "enchant_fire": {
                "materials": {"fire_crystal": 1, "enchanting_dust": 2},
                "effect": "fire_damage",
                "value": True
            },
            "soul_bind": {
                "materials": {"soul_gem": 1},
                "effect": "soul_bound",
                "value": True
            }
        }
        
        if enhancement_type not in enhancement_types:
            return False, "Unknown enhancement type"
        
        enhancement = enhancement_types[enhancement_type]
        
        # Check materials
        for mat, qty in enhancement["materials"].items():
            if materials.get(mat, 0) < qty:
                return False, f"Insufficient {mat}"
        
        # Apply enhancement
        if enhancement["effect"] in item.unique_properties:
            item.unique_properties[enhancement["effect"]] += enhancement["value"]
        else:
            item.unique_properties[enhancement["effect"]] = enhancement["value"]
        
        # Add to enchantments list
        if enhancement_type not in item.enchantments:
            item.enchantments.append(enhancement_type)
        
        return True, f"Successfully enhanced {item.get_display_name()}!"
    
    def salvage_item(self, item: CraftedItem) -> Dict[str, int]:
        """Salvage materials from crafted items"""
        materials_recovered = {}
        
        # Higher quality items give more materials back
        recovery_rate = 0.2 + (item.quality.value * 0.1)
        recovery_rate = min(0.8, recovery_rate)
        
        # Try to find original recipe
        for recipe in self.recipes.values():
            if recipe.output == item.base_type:
                for material, quantity in recipe.ingredients.items():
                    recovered = max(1, int(quantity * recovery_rate))
                    materials_recovered[material] = recovered
                break
        
        # Bonus materials for enchanted items
        if item.enchantments:
            materials_recovered["enchanting_dust"] = len(item.enchantments)
        
        if item.quality.value >= ItemQuality.EXCEPTIONAL.value:
            materials_recovered["rare_essence"] = 1
        
        return materials_recovered
    
    def get_recipe_info(self, recipe_name: str) -> str:
        """Get detailed recipe information"""
        if recipe_name not in self.recipes:
            return "Recipe not found"
        
        recipe = self.recipes[recipe_name]
        
        info = f"=== {recipe.name} ===\n"
        info += f"Skill: {recipe.skill.value} (Level {recipe.skill_level_required})\n"
        info += f"Success Chance: {recipe.success_chance * 100:.0f}%\n"
        info += f"Quality: {recipe.base_quality.name}\n"
        info += f"\nIngredients:\n"
        for ingredient, qty in recipe.ingredients.items():
            info += f"  • {ingredient} x{qty}\n"
        info += f"\nTools Required: {', '.join(recipe.tools_required)}\n"
        info += f"Produces: {recipe.output_quantity}x {recipe.output}\n"
        
        if recipe.special_effects:
            info += f"Special Effects: {', '.join(recipe.special_effects)}\n"
        
        if recipe.unlock_condition:
            info += f"Unlock: {recipe.unlock_condition}\n"
        
        return info


class PlayerCrafting:
    """Player's crafting progression and skills"""
    
    def __init__(self):
        self.skill_levels = {skill: 0 for skill in CraftingSkill}
        self.skill_experience = {skill: 0 for skill in CraftingSkill}
        self.discovered_recipes = set()
        self.crafted_items_history = []
        self.crafting_achievements = set()
        
    def gain_experience(self, skill: CraftingSkill, amount: int):
        """Gain crafting experience"""
        self.skill_experience[skill] += amount
        
        # Check for level up
        while self.skill_experience[skill] >= self.get_exp_for_next_level(skill):
            self.skill_experience[skill] -= self.get_exp_for_next_level(skill)
            self.skill_levels[skill] += 1
            self._check_achievements(skill)
            
    def get_exp_for_next_level(self, skill: CraftingSkill) -> int:
        """Calculate experience needed for next level"""
        level = self.skill_levels[skill]
        return int(100 * (level + 1) ** 1.5)
    
    def _check_achievements(self, skill: CraftingSkill):
        """Check for crafting achievements"""
        level = self.skill_levels[skill]
        
        if level >= 5 and f"apprentice_{skill.value}" not in self.crafting_achievements:
            self.crafting_achievements.add(f"apprentice_{skill.value}")
        
        if level >= 10 and f"journeyman_{skill.value}" not in self.crafting_achievements:
            self.crafting_achievements.add(f"journeyman_{skill.value}")
        
        if level >= 20 and f"master_{skill.value}" not in self.crafting_achievements:
            self.crafting_achievements.add(f"master_{skill.value}")
        
        # Grand Master of all trades
        if all(lvl >= 20 for lvl in self.skill_levels.values()):
            self.crafting_achievements.add("grand_master_crafter")
    
    def discover_recipe(self, recipe_name: str) -> bool:
        """Discover a new recipe"""
        if recipe_name not in self.discovered_recipes:
            self.discovered_recipes.add(recipe_name)
            return True
        return False
    
    def learn_recipe(self, recipe_name: str) -> bool:
        """Alias for discover_recipe for consistency"""
        return self.discover_recipe(recipe_name)
    
    def can_craft(self, recipe_name: str, crafting_system: 'CraftingSystem') -> bool:
        """Check if player can craft a specific recipe"""
        if recipe_name not in self.discovered_recipes:
            return False
        
        if recipe_name not in crafting_system.recipes:
            return False
        
        recipe = crafting_system.recipes[recipe_name]
        
        # Check skill requirement (recipe has single skill, not multiple)
        if self.skill_levels[recipe.skill] < recipe.skill_level_required:
            return False
        
        return True
    
    def craft_item(self, recipe_name: str, crafting_system: 'CraftingSystem', materials: Dict[str, int] = None) -> Optional['CraftedItem']:
        """Attempt to craft an item"""
        if not self.can_craft(recipe_name, crafting_system):
            return None
        
        # Use the main crafting system to do the actual crafting
        result = crafting_system.craft_item(recipe_name, self.skill_levels, materials or {})
        
        if result['success']:
            # Gain experience for successful craft
            recipe = crafting_system.recipes[recipe_name]
            skill = recipe.skill  # Get the recipe's skill
            exp_gained = recipe.experience_reward  # Use recipe's experience reward
            
            self.gain_experience(skill, exp_gained)
            self.crafted_items_history.append({
                'item': recipe_name,
                'quality': result['item'].quality.value,
                'timestamp': 'now'  # Would use actual timestamp in real implementation
            })
            
            return result['item']
        
        return None
    
    def get_craftable_recipes(self, crafting_system: 'CraftingSystem') -> List[str]:
        """Get list of recipes the player can currently craft"""
        craftable = []
        for recipe_name in self.discovered_recipes:
            if self.can_craft(recipe_name, crafting_system):
                craftable.append(recipe_name)
        return craftable
    
    def get_skill_info(self, skill: CraftingSkill) -> Dict[str, Any]:
        """Get detailed information about a skill"""
        return {
            'level': self.skill_levels[skill],
            'experience': self.skill_experience[skill],
            'exp_to_next_level': self.get_exp_for_next_level(skill),
            'progress_percent': (self.skill_experience[skill] / self.get_exp_for_next_level(skill)) * 100
        }