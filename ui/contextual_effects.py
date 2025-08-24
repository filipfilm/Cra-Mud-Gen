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
    def apply_room_effect(
        room_description: str, theme: str, duration: float = 1.5, llm=None, fallback_mode=False
    ):
        """
        Apply visual effects based on room description keywords
        """
        description_lower = room_description.lower()

        # Water/pond/lake effects
        if any(
            word in description_lower
            for word in ["pond", "lake", "water", "pool", "spring", "fountain"]
        ):
            message = ContextualEffects._generate_effect_message(
                llm, "water", theme, room_description, fallback_mode=fallback_mode
            )
            Effects.shimmer_pond(message, duration)
            return True

        # Fire/flame/burning effects
        if any(
            word in description_lower
            for word in [
                "fire",
                "flame",
                "burning",
                "torch",
                "brazier",
                "lava",
                "molten",
            ]
        ):
            if "lava" in description_lower or "molten" in description_lower:
                message = ContextualEffects._generate_effect_message(
                    llm, "lava", theme, room_description, fallback_mode=fallback_mode
                )
                Effects.lava_flow(message, duration)
            else:
                message = ContextualEffects._generate_effect_message(
                    llm, "fire", theme, room_description, fallback_mode=fallback_mode
                )
                Effects.burning_flame(message, duration)
            return True

        # Crystal/gem/magical effects
        if any(
            word in description_lower
            for word in [
                "crystal",
                "gem",
                "jewel",
                "sparkle",
                "glitter",
                "magical",
                "enchanted",
            ]
        ):
            message = ContextualEffects._generate_effect_message(
                llm, "magical", theme, room_description, fallback_mode=fallback_mode
            )
            Effects.crystal_sparkle(message, duration)
            return True

        # Lightning/storm/electric effects
        if any(
            word in description_lower
            for word in ["lightning", "storm", "electric", "spark", "energy", "power"]
        ):
            message = ContextualEffects._generate_effect_message(
                llm, "lightning", theme, room_description, fallback_mode=fallback_mode
            )
            Effects.lightning_strike(message, 2)
            return True

        # Poison/toxic/corruption effects
        if any(
            word in description_lower
            for word in [
                "poison",
                "toxic",
                "corruption",
                "decay",
                "rot",
                "putrid",
                "bubble",
            ]
        ):
            message = ContextualEffects._generate_effect_message(
                llm, "poison", theme, room_description, fallback_mode=fallback_mode
            )
            Effects.toxic_bubble(message, duration)
            return True

        # Void/shadow/dark effects
        if any(
            word in description_lower
            for word in [
                "void",
                "shadow",
                "dark",
                "corruption",
                "evil",
                "curse",
                "nightmare",
            ]
        ):
            message = ContextualEffects._generate_effect_message(
                llm, "shadow", theme, room_description, fallback_mode=fallback_mode
            )
            Effects.void_corruption(message, duration)
            return True

        # Snow/ice/cold effects
        if any(
            word in description_lower
            for word in ["snow", "ice", "frost", "frozen", "cold", "winter", "blizzard"]
        ):
            message = ContextualEffects._generate_effect_message(
                llm, "ice", theme, room_description, fallback_mode=fallback_mode
            )
            Effects.snow_fall(message, duration)
            return True

        # Smoke/mist/fog effects
        if any(
            word in description_lower
            for word in ["smoke", "mist", "fog", "haze", "vapor", "steam"]
        ):
            message = ContextualEffects._generate_effect_message(
                llm, "smoke", theme, room_description, fallback_mode=fallback_mode
            )
            Effects.smoke_drift(message, duration)
            return True

        # Aurora/celestial effects
        if any(
            word in description_lower
            for word in [
                "aurora",
                "celestial",
                "starlight",
                "cosmic",
                "stellar",
                "nebula",
            ]
        ):
            message = ContextualEffects._generate_effect_message(
                llm, "aurora", theme, room_description, fallback_mode=fallback_mode
            )
            Effects.aurora_dance(message, duration)
            return True

        # Matrix/digital/tech effects (Sci-fi theme)
        if theme == "sci-fi" and any(
            word in description_lower
            for word in ["data", "digital", "matrix", "code", "neural", "cyber"]
        ):
            Effects.matrix_rain("⟩ Data streams flow ⟨", duration)
            return True

        return False

    @staticmethod
    def _generate_effect_message(
        llm, effect_type: str, theme: str, context: str, fallback_mode: bool = False
    ) -> str:
        """
        Generate dynamic effect message using LLM
        """
        if not llm:
            if not fallback_mode:
                raise RuntimeError("LLM is required for contextual effects (fallback mode disabled)")
            # Fallback to simple dynamic messages if no LLM
            fallbacks = {
                "water": [
                    "~ Water ripples softly ~",
                    "~ Liquid reflects light ~",
                    "~ Moisture glints nearby ~",
                ],
                "fire": [
                    "≈ Heat shimmers in the air ≈",
                    "≈ Warm light flickers ≈",
                    "≈ Embers glow softly ≈",
                ],
                "lava": [
                    "≈ Molten currents flow ≈",
                    "≈ Volcanic heat radiates ≈",
                    "≈ Liquid rock bubbles ≈",
                ],
                "magical": [
                    "✧ Energy pulses gently ✧",
                    "✧ Mystical forces stir ✧",
                    "✧ Power hums quietly ✧",
                ],
                "lightning": [
                    "⚡ Static fills the air ⚡",
                    "⚡ Electrical energy crackles ⚡",
                    "⚡ Power surges nearby ⚡",
                ],
                "poison": [
                    "≈ Toxic vapors drift ≈",
                    "≈ Noxious fumes rise ≈",
                    "≈ Corruption seeps ≈",
                ],
                "shadow": [
                    "▓ Darkness shifts ▓",
                    "▓ Shadows dance ▓",
                    "▓ Gloom deepens ▓",
                ],
                "ice": [
                    "❅ Cold air swirls ❅",
                    "❅ Frost forms ❅",
                    "❅ Chill winds blow ❅",
                ],
                "smoke": [
                    "≋ Vapor drifts past ≋",
                    "≋ Wisps curl upward ≋",
                    "≋ Haze obscures ≋",
                ],
                "aurora": [
                    "✦ Light patterns shift ✦",
                    "✦ Colors dance above ✦",
                    "✦ Radiance flows ✦",
                ],
            }
            return random.choice(fallbacks.get(effect_type, ["~ Something stirs ~"]))

        prompt = f"""Create a short atmospheric effect message for a {theme} setting.

Effect type: {effect_type}
Context: {context}

Generate a brief atmospheric message (3-6 words) that describes this environmental effect.
Format it with appropriate symbols like:
- Water: ~ message ~
- Fire/lava: ≈ message ≈ 
- Magic: ✧ message ✧
- Lightning: ⚡ message ⚡
- Poison: ≈ message ≈
- Shadow: ▓ message ▓
- Ice: ❅ message ❅
- Smoke: ≋ message ≋
- Aurora: ✦ message ✦

Keep it evocative and thematic. Only return the formatted message."""

        try:
            response = llm.generate_response(prompt)
            # Clean response and ensure it has symbols
            cleaned = response.strip()
            if not any(
                symbol in cleaned
                for symbol in ["~", "≈", "✧", "⚡", "▓", "❅", "≋", "✦"]
            ):
                # Add fallback symbols if LLM didn't include them
                symbols = {
                    "water": "~",
                    "fire": "≈",
                    "lava": "≈",
                    "magical": "✧",
                    "lightning": "⚡",
                    "poison": "≈",
                    "shadow": "▓",
                    "ice": "❅",
                    "smoke": "≋",
                    "aurora": "✦",
                }
                symbol = symbols.get(effect_type, "~")
                cleaned = f"{symbol} {cleaned} {symbol}"
            return cleaned
        except Exception as e:
            if not fallback_mode:
                raise RuntimeError(f"LLM contextual effect generation failed and fallback mode disabled: {e}")
            # Fallback if LLM fails
            fallbacks = {
                "water": "~ Water ripples softly ~",
                "fire": "≈ Flames dance nearby ≈",
                "lava": "≈ Molten rock flows ≈",
                "magical": "✧ Mystical energy swirls ✧",
                "lightning": "⚡ Energy crackles ⚡",
                "poison": "≈ Toxic vapors rise ≈",
                "shadow": "▓ Darkness shifts ▓",
                "ice": "❅ Frost gathers ❅",
                "smoke": "≋ Mist swirls ≋",
                "aurora": "✦ Light dances ✦",
            }
            return fallbacks.get(effect_type, "~ Something stirs ~")

    @staticmethod
    def apply_item_effect(
        item_name: str, theme: str, action: str = "examine", llm=None, fallback_mode: bool = False
    ):
        """
        Apply effects based on item examination or interaction
        """
        item_lower = item_name.lower()

        # Legendary/artifact items get special effects
        if any(
            word in item_lower
            for word in ["legendary", "artifact", "divine", "cosmic", "eternal"]
        ):
            if theme == "fantasy":
                message = ContextualEffects._generate_item_effect_message(
                    llm, "legendary", item_name, theme, fallback_mode=fallback_mode
                )
                Effects.crystal_sparkle(message, 2.5)
            elif theme == "sci-fi":
                message = ContextualEffects._generate_item_effect_message(
                    llm, "legendary", item_name, theme, fallback_mode=fallback_mode
                )
                Effects.electric_storm(message, 2.0)
            elif theme == "horror":
                message = ContextualEffects._generate_item_effect_message(
                    llm, "legendary", item_name, theme, fallback_mode=fallback_mode
                )
                Effects.void_corruption(message, 2.0)
            elif theme == "cyberpunk":
                message = ContextualEffects._generate_item_effect_message(
                    llm, "legendary", item_name, theme, fallback_mode=fallback_mode
                )
                Effects.matrix_rain(message, 2.0)
            return True

        # Fire-based items
        if any(
            word in item_lower
            for word in ["flame", "fire", "burning", "torch", "ember"]
        ):
            message = ContextualEffects._generate_item_effect_message(
                llm, "fire", item_name, theme, fallback_mode=fallback_mode
            )
            Effects.burning_flame(message, 2.0)
            return True

        # Crystal/magical items
        if any(
            word in item_lower
            for word in ["crystal", "gem", "magical", "enchanted", "glowing"]
        ):
            message = ContextualEffects._generate_item_effect_message(
                llm, "magical", item_name, theme, fallback_mode=fallback_mode
            )
            Effects.crystal_sparkle(message, 2.0)
            return True

        # Tech/electric items
        if any(
            word in item_lower
            for word in ["electric", "plasma", "energy", "quantum", "neural"]
        ):
            message = ContextualEffects._generate_item_effect_message(
                llm, "electric", item_name, theme, fallback_mode=fallback_mode
            )
            Effects.electric_storm(message, 1.5)
            return True

        # Cursed/dark items
        if any(
            word in item_lower
            for word in ["cursed", "dark", "shadow", "void", "nightmare"]
        ):
            message = ContextualEffects._generate_item_effect_message(
                llm, "cursed", item_name, theme, fallback_mode=fallback_mode
            )
            Effects.void_corruption(message, 2.0)
            return True

        return False

    @staticmethod
    def _generate_item_effect_message(
        llm, effect_type: str, item_name: str, theme: str, fallback_mode: bool = False
    ) -> str:
        """Generate dynamic item effect message using LLM"""
        if not llm:
            if not fallback_mode:
                raise RuntimeError("LLM is required for item effects (fallback mode disabled)")
            templates = {
                "legendary": f"✧ The {item_name} radiates power ✧",
                "fire": f"≈ The {item_name} flickers with flame ≈",
                "magical": f"✧ The {item_name} sparkles ✧",
                "electric": f"⚡ The {item_name} hums with energy ⚡",
                "cursed": f"▓ The {item_name} emanates darkness ▓",
            }
            return templates.get(effect_type, f"~ The {item_name} seems special ~")

        try:
            prompt = f"""Create a short atmospheric effect message for examining a {effect_type} item in a {theme} setting.

Item: {item_name}
Effect type: {effect_type}

Generate a brief effect message (4-8 words) describing this item's properties.
Format with symbols: ✧ for legendary/magical, ≈ for fire, ⚡ for electric, ▓ for cursed.
Mention the item name. Only return the formatted message."""

            response = llm.generate_response(prompt)
            return response.strip()
        except Exception as e:
            if not fallback_mode:
                raise RuntimeError(f"LLM item effect generation failed and fallback mode disabled: {e}")
            templates = {
                "legendary": f"✧ The {item_name} radiates ancient power ✧",
                "fire": f"≈ The {item_name} flickers with inner flame ≈",
                "magical": f"✧ The {item_name} sparkles with magic ✧",
                "electric": f"⚡ The {item_name} crackles with energy ⚡",
                "cursed": f"▓ The {item_name} whispers darkness ▓",
            }
            return templates.get(effect_type, f"~ The {item_name} seems special ~")

    @staticmethod
    def apply_combat_effect(event_type: str, theme: str, llm=None):
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
    def apply_death_effect(cause: str, theme: str, llm=None):
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
    def random_ambient_effect(theme: str, intensity: float = 0.1, llm=None):
        """
        Randomly apply ambient atmospheric effects
        """
        if random.random() < intensity:  # Default 10% chance
            effects_by_theme = {
                "fantasy": [
                    lambda: Effects.crystal_sparkle(
                        "✧ Magic shimmers in the air ✧", 1.5
                    ),
                    lambda: Effects.aurora_dance("✦ Mystical energies flow ✦", 2.0),
                ],
                "sci-fi": [
                    lambda: Effects.electric_storm(
                        "⚡ Energy patterns fluctuate ⚡", 1.5
                    ),
                    lambda: Effects.matrix_rain("⟩ Data streams pass by ⟨", 2.0),
                ],
                "horror": [
                    lambda: Effects.void_corruption("▓ Shadows writhe nearby ▓", 1.5),
                    lambda: Effects.smoke_drift("≋ Ominous mist gathers ≋", 2.0),
                ],
                "cyberpunk": [
                    lambda: Effects.matrix_rain("⟩ Digital rain falls ⟨", 2.0),
                    lambda: Effects.electric_storm("⚡ Neon flickers ⚡", 1.5),
                ],
            }

            theme_effects = effects_by_theme.get(theme, effects_by_theme["fantasy"])
            effect = random.choice(theme_effects)
            effect()
            return True

        return False
