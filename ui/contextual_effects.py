"""
Contextual Effects System
Automatically applies visual effects based on game content
"""
import random
from .colors import Effects, Colors

class ContextualEffects:
    """
    Applies appropriate visual effects based on game context
    """
    
    @staticmethod
    def apply_room_effect(room_description: str, theme: str, duration: float = 1.5):
        """
        Apply visual effects based on room description keywords
        """
        description_lower = room_description.lower()
        
        # Water/pond/lake effects
        if any(word in description_lower for word in ['pond', 'lake', 'water', 'pool', 'spring', 'fountain']):
            Effects.shimmer_pond("~ The water shimmers mysteriously ~", duration)
            return True
        
        # Fire/flame/burning effects  
        if any(word in description_lower for word in ['fire', 'flame', 'burning', 'torch', 'brazier', 'lava', 'molten']):
            if 'lava' in description_lower or 'molten' in description_lower:
                Effects.lava_flow("≈ Molten rock flows nearby ≈", duration)
            else:
                Effects.burning_flame("≈ Flames dance in the darkness ≈", duration)
            return True
        
        # Crystal/gem/magical effects
        if any(word in description_lower for word in ['crystal', 'gem', 'jewel', 'sparkle', 'glitter', 'magical', 'enchanted']):
            Effects.crystal_sparkle("✧ Magical energies swirl around ✧", duration)
            return True
        
        # Lightning/storm/electric effects
        if any(word in description_lower for word in ['lightning', 'storm', 'electric', 'spark', 'energy', 'power']):
            Effects.lightning_strike("⚡ Energy crackles through the air ⚡", 2)
            return True
        
        # Poison/toxic/corruption effects
        if any(word in description_lower for word in ['poison', 'toxic', 'corruption', 'decay', 'rot', 'putrid', 'bubble']):
            Effects.toxic_bubble("≈ Noxious vapors rise ≈", duration)
            return True
        
        # Void/shadow/dark effects
        if any(word in description_lower for word in ['void', 'shadow', 'dark', 'corruption', 'evil', 'curse', 'nightmare']):
            Effects.void_corruption("▓ Darkness seeps from the walls ▓", duration)
            return True
        
        # Snow/ice/cold effects
        if any(word in description_lower for word in ['snow', 'ice', 'frost', 'frozen', 'cold', 'winter', 'blizzard']):
            Effects.snow_fall("❅ Frost gathers in the air ❅", duration)
            return True
        
        # Smoke/mist/fog effects
        if any(word in description_lower for word in ['smoke', 'mist', 'fog', 'haze', 'vapor', 'steam']):
            Effects.smoke_drift("≋ Mist swirls about ≋", duration)
            return True
        
        # Aurora/celestial effects
        if any(word in description_lower for word in ['aurora', 'celestial', 'starlight', 'cosmic', 'stellar', 'nebula']):
            Effects.aurora_dance("✦ Celestial lights dance ✦", duration)
            return True
        
        # Matrix/digital/tech effects (Sci-fi theme)
        if theme == 'sci-fi' and any(word in description_lower for word in ['data', 'digital', 'matrix', 'code', 'neural', 'cyber']):
            Effects.matrix_rain("⟩ Data streams flow ⟨", duration)
            return True
        
        return False
    
    @staticmethod
    def apply_item_effect(item_name: str, theme: str, action: str = "examine"):
        """
        Apply effects based on item examination or interaction
        """
        item_lower = item_name.lower()
        
        # Legendary/artifact items get special effects
        if any(word in item_lower for word in ['legendary', 'artifact', 'divine', 'cosmic', 'eternal']):
            if theme == "fantasy":
                Effects.crystal_sparkle(f"✧ The {item_name} radiates ancient power ✧", 2.5)
            elif theme == "sci-fi":
                Effects.electric_storm(f"⚡ The {item_name} pulses with energy ⚡", 2.0)
            elif theme == "horror":
                Effects.void_corruption(f"▓ The {item_name} whispers dark secrets ▓", 2.0)
            elif theme == "cyberpunk":
                Effects.matrix_rain(f"⟩ The {item_name} interfaces with reality ⟨", 2.0)
            return True
        
        # Fire-based items
        if any(word in item_lower for word in ['flame', 'fire', 'burning', 'torch', 'ember']):
            Effects.burning_flame(f"≈ The {item_name} flickers with inner fire ≈", 2.0)
            return True
        
        # Crystal/magical items
        if any(word in item_lower for word in ['crystal', 'gem', 'magical', 'enchanted', 'glowing']):
            Effects.crystal_sparkle(f"✧ The {item_name} sparkles brilliantly ✧", 2.0)
            return True
        
        # Tech/electric items
        if any(word in item_lower for word in ['electric', 'plasma', 'energy', 'quantum', 'neural']):
            Effects.electric_storm(f"⚡ The {item_name} hums with power ⚡", 1.5)
            return True
        
        # Cursed/dark items
        if any(word in item_lower for word in ['cursed', 'dark', 'shadow', 'void', 'nightmare']):
            Effects.void_corruption(f"▓ The {item_name} emanates malevolent energy ▓", 2.0)
            return True
        
        return False
    
    @staticmethod
    def apply_combat_effect(event_type: str, theme: str):
        """
        Apply effects during combat events
        """
        if event_type == "player_hit":
            Effects.lightning_strike("⚡ IMPACT ⚡", 1)
        elif event_type == "enemy_death":
            if theme == "fantasy":
                Effects.crystal_sparkle("✧ Victory achieved ✧", 1.5)
            elif theme == "sci-fi":
                Effects.electric_storm("⚡ Target eliminated ⚡", 1.5)
            elif theme == "horror":
                Effects.void_corruption("▓ The darkness recedes ▓", 1.5)
            elif theme == "cyberpunk":
                Effects.matrix_rain("⟩ System compromised ⟨", 1.5)
        elif event_type == "level_up":
            Effects.aurora_dance("✦ ✧ LEVEL UP! ✧ ✦", 3.0)
        elif event_type == "critical_hit":
            Effects.lightning_strike("⚡ CRITICAL STRIKE ⚡", 2)
        elif event_type == "magic_spell":
            if theme == "fantasy":
                Effects.crystal_sparkle("✧ Magical energy surges ✧", 2.0)
            else:
                Effects.aurora_dance("✦ Power flows through you ✦", 2.0)
    
    @staticmethod
    def apply_death_effect(cause: str, theme: str):
        """
        Apply dramatic death effects
        """
        if "fire" in cause.lower() or "burn" in cause.lower():
            Effects.burning_flame("≈ ≈ ≈ CONSUMED BY FLAMES ≈ ≈ ≈", 3.0)
        elif "poison" in cause.lower() or "toxic" in cause.lower():
            Effects.toxic_bubble("≈ ≈ ≈ POISONED ≈ ≈ ≈", 3.0)
        elif "electric" in cause.lower() or "lightning" in cause.lower():
            Effects.lightning_strike("⚡ ⚡ ⚡ ELECTROCUTED ⚡ ⚡ ⚡", 3)
        elif "void" in cause.lower() or "shadow" in cause.lower():
            Effects.void_corruption("▓ ▓ ▓ CONSUMED BY DARKNESS ▓ ▓ ▓", 3.0)
        elif "ice" in cause.lower() or "frozen" in cause.lower():
            Effects.snow_fall("❅ ❅ ❅ FROZEN SOLID ❅ ❅ ❅", 3.0)
        else:
            # Generic death effect
            Effects.aurora_dance("✦ Your adventure ends here ✦", 3.0)
    
    @staticmethod
    def random_ambient_effect(theme: str, intensity: float = 0.1):
        """
        Randomly apply ambient atmospheric effects
        """
        if random.random() < intensity:  # Default 10% chance
            effects_by_theme = {
                "fantasy": [
                    lambda: Effects.crystal_sparkle("✧ Magic shimmers in the air ✧", 1.5),
                    lambda: Effects.aurora_dance("✦ Mystical energies flow ✦", 2.0)
                ],
                "sci-fi": [
                    lambda: Effects.electric_storm("⚡ Energy patterns fluctuate ⚡", 1.5),
                    lambda: Effects.matrix_rain("⟩ Data streams pass by ⟨", 2.0)
                ],
                "horror": [
                    lambda: Effects.void_corruption("▓ Shadows writhe nearby ▓", 1.5),
                    lambda: Effects.smoke_drift("≋ Ominous mist gathers ≋", 2.0)
                ],
                "cyberpunk": [
                    lambda: Effects.matrix_rain("⟩ Digital rain falls ⟨", 2.0),
                    lambda: Effects.electric_storm("⚡ Neon flickers ⚡", 1.5)
                ]
            }
            
            theme_effects = effects_by_theme.get(theme, effects_by_theme["fantasy"])
            effect = random.choice(theme_effects)
            effect()
            return True
            
        return False