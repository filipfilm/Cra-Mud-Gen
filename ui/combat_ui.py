"""
Combat UI Display System
Manages combat visualization, health bars, and combat feedback
"""
import sys
import time
from typing import List, Dict, Any
from .colors import Colors
# Effects can be added later if needed


class CombatUI:
    """Manages combat display and visualization"""
    
    def __init__(self):
        self.combat_width = 80
        self.health_bar_width = 20
    
    def display_combat_start(self, enemies: List, player_name: str = "Player"):
        """Display combat encounter start screen"""
        print(Colors.BOLD + Colors.RED + "⚔️  COMBAT ENGAGED! ⚔️" + Colors.RESET)
        print("═" * self.combat_width)
        
        enemy_names = [enemy.name for enemy in enemies]
        if len(enemies) == 1:
            print(f"{Colors.YELLOW}A {enemy_names[0]} blocks your path!{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}Multiple enemies appear: {', '.join(enemy_names)}!{Colors.RESET}")
        
        print("═" * self.combat_width)
        print()
    
    def display_combat_status(self, player, enemies: List):
        """Display current combat status with health bars"""
        print(Colors.BOLD + "COMBAT STATUS:" + Colors.RESET)
        print("─" * self.combat_width)
        
        # Player status
        player_health_bar = self._create_health_bar(player.current_health, player.max_health)
        print(f"{Colors.GREEN}{player.name:15}{Colors.RESET} {player_health_bar} "
              f"({player.current_health}/{player.max_health}) HP")
        
        # Status effects
        if hasattr(player, 'status_effects') and player.status_effects:
            effects = ', '.join(player.status_effects.keys())
            print(f"{Colors.CYAN}   Status: {effects}{Colors.RESET}")
        
        print()
        
        # Enemy status
        living_enemies = [e for e in enemies if not e.is_dead]
        for enemy in living_enemies:
            enemy_health_bar = self._create_health_bar(enemy.current_health, enemy.max_health)
            print(f"{Colors.RED}{enemy.name:15}{Colors.RESET} {enemy_health_bar} "
                  f"({enemy.current_health}/{enemy.max_health}) HP")
            
            # Enemy status effects
            if hasattr(enemy, 'status_effects') and enemy.status_effects:
                effects = ', '.join(enemy.status_effects.keys())
                print(f"{Colors.CYAN}   Status: {effects}{Colors.RESET}")
        
        print("─" * self.combat_width)
        print()
    
    def display_combat_actions(self):
        """Display available combat actions"""
        print(Colors.BOLD + "COMBAT OPTIONS:" + Colors.RESET)
        print(f"{Colors.YELLOW}  attack <target>{Colors.RESET} - Attack an enemy")
        print(f"{Colors.BLUE}  defend        {Colors.RESET} - Take defensive stance (-50% damage)")
        print(f"{Colors.MAGENTA}  heal          {Colors.RESET} - Use healing potion (if available)")
        print(f"{Colors.RED}  flee          {Colors.RESET} - Attempt to escape combat")
        print()
    
    def display_attack_result(self, attacker_name: str, target_name: str, damage: int, 
                             is_critical: bool = False, is_miss: bool = False):
        """Display attack results with visual effects"""
        if is_miss:
            print(f"{Colors.GRAY}{attacker_name} swings at {target_name} but misses!{Colors.RESET}")
            return
        
        if is_critical:
            # Critical hit effect
            crit_text = f"{Colors.BOLD}{Colors.RED}💥 CRITICAL HIT! 💥{Colors.RESET}"
            damage_text = f"{Colors.BOLD}{Colors.RED}{damage}{Colors.RESET}"
            print(f"{Colors.YELLOW}{attacker_name}{Colors.RESET} strikes {Colors.RED}{target_name}{Colors.RESET} "
                  f"for {damage_text} damage! {crit_text}")
        else:
            # Normal hit
            damage_text = f"{Colors.RED}{damage}{Colors.RESET}"
            print(f"{Colors.YELLOW}{attacker_name}{Colors.RESET} attacks {Colors.RED}{target_name}{Colors.RESET} "
                  f"for {damage_text} damage!")
    
    def display_death(self, character_name: str, is_player: bool = False):
        """Display death message"""
        if is_player:
            print(f"{Colors.BOLD}{Colors.RED}💀 {character_name} has fallen in battle! 💀{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}⚰️  {character_name} has been defeated! ⚰️{Colors.RESET}")
    
    def display_combat_victory(self, rewards: Dict[str, Any]):
        """Display victory screen with rewards"""
        print()
        print(Colors.BOLD + Colors.GREEN + "🎉 VICTORY! 🎉" + Colors.RESET)
        print("═" * self.combat_width)
        
        if rewards.get('experience', 0) > 0:
            exp_text = f"{Colors.CYAN}Experience gained: +{rewards['experience']}{Colors.RESET}"
            print(exp_text)
        
        if rewards.get('gold', 0) > 0:
            gold_text = f"{Colors.YELLOW}Gold found: +{rewards['gold']}{Colors.RESET}"
            print(gold_text)
        
        if rewards.get('loot'):
            loot_items = rewards['loot']
            print(f"{Colors.MAGENTA}Items found:{Colors.RESET}")
            for item in loot_items:
                item_text = f"  • {item}"
                print(item_text)
        
        print("═" * self.combat_width)
        print()
    
    def display_combat_defeat(self):
        """Display defeat screen"""
        print()
        print(Colors.BOLD + Colors.RED + "💀 DEFEAT 💀" + Colors.RESET)
        print("═" * self.combat_width)
        print(f"{Colors.RED}You have been defeated in combat...{Colors.RESET}")
        print(f"{Colors.YELLOW}The dungeon claims another adventurer.{Colors.RESET}")
        print("═" * self.combat_width)
        print()
    
    def display_flee_success(self):
        """Display successful flee message"""
        flee_text = f"{Colors.GREEN}You successfully escape from combat!{Colors.RESET}"
        print(flee_text)
        print()
    
    def display_flee_failure(self):
        """Display failed flee attempt"""
        print(f"{Colors.RED}You cannot escape! The enemies block your path!{Colors.RESET}")
        print()
    
    def display_healing(self, character_name: str, amount: int):
        """Display healing effect"""
        heal_text = f"{Colors.GREEN}{character_name} recovers {amount} health!{Colors.RESET}"
        print(heal_text)
    
    def display_status_effect(self, character_name: str, effect: str, is_applied: bool = True):
        """Display status effect application or removal"""
        if is_applied:
            effect_text = f"{Colors.MAGENTA}{character_name} is affected by {effect}!{Colors.RESET}"
        else:
            effect_text = f"{Colors.CYAN}{character_name} recovers from {effect}!{Colors.RESET}"
        
        print(effect_text)
    
    def display_level_up(self, player_name: str, old_level: int, new_level: int, benefits: List[str]):
        """Display level up celebration"""
        print()
        print(Colors.BOLD + Colors.YELLOW + "🌟 LEVEL UP! 🌟" + Colors.RESET)
        print("═" * self.combat_width)
        
        level_text = f"{player_name} advances from level {old_level} to level {new_level}!"
        print(level_text)
        
        print(f"{Colors.CYAN}Benefits gained:{Colors.RESET}")
        for benefit in benefits:
            benefit_text = f"  • {benefit}"
            print(benefit_text)
        
        print("═" * self.combat_width)
        print()
    
    def _create_health_bar(self, current: int, maximum: int) -> str:
        """Create a colored health bar"""
        if maximum <= 0:
            return f"[{Colors.GRAY}{'─' * self.health_bar_width}{Colors.RESET}]"
        
        health_ratio = current / maximum
        filled_bars = int(health_ratio * self.health_bar_width)
        empty_bars = self.health_bar_width - filled_bars
        
        # Color based on health percentage
        if health_ratio > 0.6:
            color = Colors.GREEN
        elif health_ratio > 0.3:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        
        filled = color + "█" * filled_bars + Colors.RESET
        empty = Colors.GRAY + "░" * empty_bars + Colors.RESET
        
        return f"[{filled}{empty}]"
    
    def prompt_combat_action(self, enemies: List) -> str:
        """Prompt player for combat action with context"""
        if len(enemies) > 1:
            enemy_list = ", ".join([f"{i+1}.{e.name}" for i, e in enumerate(enemies) if not e.is_dead])
            print(f"{Colors.CYAN}Available targets: {enemy_list}{Colors.RESET}")
        
        return input(f"{Colors.BOLD}Combat action > {Colors.RESET}").strip().lower()
    
    def clear_combat_screen(self):
        """Clear screen for combat display"""
        # Simple clear - could be enhanced with actual screen clearing
        print("\n" * 3)
    
    def display_turn_separator(self, turn_number: int):
        """Display turn separator"""
        print(f"{Colors.CYAN}--- Turn {turn_number} ---{Colors.RESET}")
        print()