"""
Terminal-based user interface for Cra-mud-gen
"""
import os
import sys
from typing import Dict, Any, List
from .colors import Colors, ColorThemes, Effects, StatusBar
from .contextual_effects import ContextualEffects

class TerminalUI:
    """
    Text-based user interface for Cra-mud-gen
    """
    
    def __init__(self, fallback_mode=False):
        self.clear_command = "clear" if os.name != "nt" else "cls"
        self.fallback_mode = fallback_mode
        
    def get_input(self) -> str:
        """
        Get input from the user
        """
        try:
            return input("\n> ")
        except EOFError:
            return "quit"
        except KeyboardInterrupt:
            print("\nGame interrupted. Type 'quit' to exit.")
            return "quit"
            
    def display_welcome(self):
        """
        Display welcome message with colorful effects
        """
        self.clear_screen()
        
        # Animated title with rainbow effect
        title = "Welcome to Cra-mud-gen"
        rainbow_title = Effects.rainbow_text(title)
        
        print(f"{Colors.BRIGHT_CYAN}{'=' * 60}{Colors.RESET}")
        print(f"           {rainbow_title}")
        print(f"{Colors.BRIGHT_CYAN}{'=' * 60}{Colors.RESET}")
        
        # Glowing description
        print(f"{Colors.GLOW_YELLOW}An offline text-based adventure game with AI-powered responses{Colors.RESET}")
        print(f"{Colors.GLOW_CYAN}and procedural generation.{Colors.RESET}")
        print()
        
    def get_theme_selection(self) -> str:
        """
        Get theme selection from the user with colorful theme preview
        """
        print(f"{Colors.BRIGHT_WHITE}Choose a game theme:{Colors.RESET}")
        print()
        
        # Show themes with their signature colors
        print(f"1. {Effects.fire_text('Fantasy')}     {Colors.DIM}(Magic, dragons, medieval adventure){Colors.RESET}")
        print(f"2. {Effects.matrix_text('Sci-Fi')}      {Colors.DIM}(Space, technology, future worlds){Colors.RESET}")
        print(f"3. {Effects.horror_text('Horror')}     {Colors.DIM}(Dark, creepy, supernatural terror){Colors.RESET}")
        print(f"4. {Effects.neon_glow('Cyberpunk', 0, 255, 255)}  {Colors.DIM}(Neon, hackers, dystopian future){Colors.RESET}")
        print()
        
        while True:
            try:
                choice = input(f"{Colors.BRIGHT_YELLOW}Enter your choice (1-4): {Colors.RESET}").strip()
                
                if choice == "1":
                    self._last_theme = "fantasy"
                    print(f"{Colors.GLOW_MAGENTA}✓ Fantasy theme selected!{Colors.RESET}")
                    Effects.crystal_sparkle("Prepare for magical adventures!", 2.0)
                    return "fantasy"
                elif choice == "2":
                    self._last_theme = "sci-fi"
                    print(f"{Colors.GLOW_CYAN}✓ Sci-Fi theme selected!{Colors.RESET}")
                    Effects.electric_storm("Welcome to the future!", 1.5)
                    return "sci-fi"
                elif choice == "3":
                    self._last_theme = "horror"
                    print(f"{Colors.GLOW_RED}✓ Horror theme selected!{Colors.RESET}")
                    Effects.void_corruption("Enter if you dare...", 2.0)
                    return "horror"
                elif choice == "4":
                    self._last_theme = "cyberpunk"
                    print(f"{Colors.rgb(0, 255, 255)}{Colors.BOLD}✓ Cyberpunk theme selected!{Colors.RESET}")
                    Effects.matrix_rain("Jacking into the matrix...", 2.0)
                    return "cyberpunk"
                else:
                    print(f"{Colors.BRIGHT_RED}Invalid choice. Please enter 1, 2, 3, or 4.{Colors.RESET}")
            except (EOFError, KeyboardInterrupt):
                print(f"\n{Colors.BRIGHT_RED}Game interrupted. Exiting...{Colors.RESET}")
                sys.exit(0)
                
    def display_room(self, room, player, llm=None):
        """
        Display the current room description with colors and effects
        """
        # Get theme colors
        theme_colors = self._get_theme_colors(player.theme)
        
        print(f"\n{theme_colors['primary']}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}Location: {theme_colors['accent']}{room.room_id}{Colors.RESET}")
        print(f"{theme_colors['primary']}{'=' * 60}{Colors.RESET}")
        
        # Room description with theme-appropriate styling
        description = room.get_description()
        print(f"{Colors.BRIGHT_WHITE}{description}{Colors.RESET}")
        
        # Apply contextual visual effects based on room description
        ContextualEffects.apply_room_effect(description, player.theme, 1.5, llm, fallback_mode=self.fallback_mode)
        
        # Show items with rarity colors
        items = room.get_items()
        if items:
            print(f"\n{Colors.GLOW_YELLOW}Items in this room:{Colors.RESET}")
            for item in items:
                item_color = self._get_item_color(item)
                print(f"  {Colors.BRIGHT_WHITE}•{Colors.RESET} {item_color}{item}{Colors.RESET}")
                
        # Show NPCs with danger indication
        npcs = room.get_npcs()
        if npcs:
            print(f"\n{Colors.GLOW_RED}NPCs here:{Colors.RESET}")
            for npc in npcs:
                if any(word in npc.lower() for word in ['goblin', 'orc', 'demon', 'enemy']):
                    print(f"  {Colors.BRIGHT_RED}⚔{Colors.RESET} {Colors.BRIGHT_RED}{npc}{Colors.RESET}")
                else:
                    print(f"  {Colors.BRIGHT_GREEN}♦{Colors.RESET} {Colors.BRIGHT_CYAN}{npc}{Colors.RESET}")
                
        # Show exits with directional indicators
        exits = room.get_exits()
        if exits:
            print(f"\n{theme_colors['secondary']}Exits:{Colors.RESET}")
            for exit in exits:
                direction = exit.split('_')[0] if '_' in exit else exit
                direction_symbol = self._get_direction_symbol(direction)
                print(f"  {theme_colors['accent']}{direction_symbol}{Colors.RESET} {Colors.BRIGHT_WHITE}{exit}{Colors.RESET}")
                
        # Show enhanced player status with health bar
        self._display_player_status(player, theme_colors)
    
    def _get_theme_colors(self, theme: str) -> Dict[str, str]:
        """Get color scheme based on game theme"""
        if theme == "fantasy":
            return ColorThemes.FANTASY
        elif theme == "sci-fi":
            return ColorThemes.SCIFI
        elif theme == "horror":
            return ColorThemes.HORROR
        elif theme == "cyberpunk":
            return ColorThemes.CYBERPUNK
        else:
            return ColorThemes.FANTASY
    
    def _get_item_color(self, item: str) -> str:
        """Determine item rarity color based on keywords"""
        item_lower = item.lower()
        
        if any(word in item_lower for word in ['artifact', 'divine', 'cosmic', 'legendary']):
            return ColorThemes.ITEM_ARTIFACT
        elif any(word in item_lower for word in ['dragon', 'phoenix', 'world', 'essence']):
            return ColorThemes.ITEM_LEGENDARY
        elif any(word in item_lower for word in ['ancient', 'magical', 'enchanted', 'crystal']):
            return ColorThemes.ITEM_EPIC
        elif any(word in item_lower for word in ['glowing', 'mystical', 'blessed']):
            return ColorThemes.ITEM_RARE
        elif any(word in item_lower for word in ['fine', 'quality', 'silver']):
            return ColorThemes.ITEM_UNCOMMON
        else:
            return ColorThemes.ITEM_COMMON
    
    def _get_direction_symbol(self, direction: str) -> str:
        """Get symbol for direction"""
        symbols = {
            'north': '↑', 'south': '↓', 'east': '→', 'west': '←',
            'up': '⇧', 'down': '⇩'
        }
        return symbols.get(direction.lower(), '→')
    
    def _display_player_status(self, player, theme_colors: Dict[str, str]):
        """Display enhanced player status with health bar and colors"""
        health_bar = StatusBar.health_bar(player.health, 100, 20)
        
        print(f"\n{theme_colors['primary']}{'─' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}Health:{Colors.RESET} {health_bar} " + 
              f"{Colors.BRIGHT_WHITE}Level: {Colors.GLOW_YELLOW}{player.level}{Colors.RESET} " +
              f"{Colors.BRIGHT_WHITE}Gold: {Colors.GOLD}{player.gold}{Colors.RESET} " +
              f"{Colors.BRIGHT_WHITE}Items: {Colors.BRIGHT_CYAN}{len(player.inventory)}/20{Colors.RESET}")
        print(f"{theme_colors['primary']}{'─' * 60}{Colors.RESET}")
        
    def display_error(self, message: str):
        """
        Display an error message with pulsing red effect
        """
        print(f"\n{Colors.PULSE_RED}❌ Error: {message}{Colors.RESET}")
        
    def display_goodbye(self):
        """
        Display goodbye message with colorful farewell
        """
        farewell_text = "Thank you for playing Dun-Gen!"
        rainbow_farewell = Effects.rainbow_text(farewell_text)
        
        print(f"\n{rainbow_farewell}")
        print(f"{Colors.GLOW_CYAN}Come back soon for another adventure!{Colors.RESET}")
        
        # Spectacular farewell effect based on last theme
        farewell_msg = "✨ Until next time, brave adventurer! ✨"
        if hasattr(self, '_last_theme'):
            if self._last_theme == "fantasy":
                Effects.crystal_sparkle(farewell_msg, 2.5)
            elif self._last_theme == "sci-fi":
                Effects.electric_storm(farewell_msg, 2.0)
            elif self._last_theme == "horror":
                Effects.void_corruption(farewell_msg, 2.0)
            elif self._last_theme == "cyberpunk":
                Effects.matrix_rain(farewell_msg, 2.5)
            else:
                Effects.aurora_dance(farewell_msg, 2.0)
        else:
            Effects.aurora_dance(farewell_msg, 2.0)
        
    def clear_screen(self):
        """
        Clear the terminal screen
        """
        os.system(self.clear_command)
        
    def display_message(self, message: str):
        """
        Display a simple message
        """
        print(message)
        
    def display_help(self, help_text: str):
        """
        Display help text
        """
        print(help_text)
    
    def get_model_selection(self, available_models: List[Dict]) -> str:
        """
        Display available Ollama models and get user selection
        """
        if not available_models:
            print("\n❌ No Ollama models found!")
            print("Please install a model first. Popular options:")
            print("  • ollama pull mistral           (7B - Good for storytelling)")
            print("  • ollama pull llama3.1          (8B - Great general purpose)")
            print("  • ollama pull gemma2:2b         (2B - Fast and lightweight)")
            print("  • ollama pull neural-chat       (7B - Optimized for conversation)")
            print("\nAfter installing a model, restart the game.")
            sys.exit(0)
        
        print(f"\n{Colors.BRIGHT_CYAN}{'=' * 60}{Colors.RESET}")
        brain_title = Effects.neon_glow("🧠 SELECT AI MODEL", 0, 255, 255)
        print(f"           {brain_title}")
        print(f"{Colors.BRIGHT_CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.GLOW_YELLOW}Available Ollama models for your adventure:{Colors.RESET}\n")
        
        # Show recommended models first
        recommended = [m for m in available_models if m.get("recommended", False)]
        others = [m for m in available_models if not m.get("recommended", False)]
        
        all_models = recommended + others
        
        for i, model in enumerate(all_models, 1):
            if model.get("recommended", False):
                status = f"{Colors.GLOW_YELLOW}⭐ RECOMMENDED{Colors.RESET}"
                name_color = Colors.GLOW_GREEN
            else:
                status = f"{Colors.DIM}  Available{Colors.RESET}"
                name_color = Colors.BRIGHT_WHITE
                
            print(f"{Colors.BRIGHT_CYAN}{i:2d}.{Colors.RESET} {name_color}{model['name']:<25}{Colors.RESET} " +
                  f"{Colors.DIM}({model['size']:<8}){Colors.RESET} {status}")
            print(f"    {Colors.DIM}{model['description']}{Colors.RESET}")
            print()
        
        print(f"{Colors.BRIGHT_CYAN}{'=' * 60}{Colors.RESET}")
        
        while True:
            try:
                choice = input(f"{Colors.BRIGHT_MAGENTA}Select model (1-{len(all_models)}): {Colors.RESET}").strip()
                
                if not choice:
                    continue
                    
                index = int(choice) - 1
                if 0 <= index < len(all_models):
                    selected_model = all_models[index]
                    model_name = selected_model['name']
                    
                    print(f"\n{Colors.GLOW_GREEN}✓ Selected: {Colors.BRIGHT_WHITE}{model_name}{Colors.RESET}")
                    if selected_model.get("recommended", False):
                        print(f"  {Colors.BRIGHT_MAGENTA}Great choice for adventures! 🎮{Colors.RESET}")
                    else:
                        print(f"  {Colors.BRIGHT_YELLOW}This model may work differently - experiment and have fun! 🔬{Colors.RESET}")
                    
                    # Brief loading animation
                    StatusBar.loading_animation("Initializing model", 1.0)
                    
                    return model_name
                else:
                    print(f"{Colors.BRIGHT_RED}Please enter a number between 1 and {len(all_models)}{Colors.RESET}")
                    
            except ValueError:
                print(f"{Colors.BRIGHT_RED}Please enter a valid number{Colors.RESET}")
            except KeyboardInterrupt:
                print(f"\n\n{Colors.GLOW_CYAN}Goodbye!{Colors.RESET}")
                sys.exit(0)
    
    def display_examine_result(self, result: str, item_name: str, theme: str, llm=None):
        """
        Display examination result with contextual effects
        """
        print(result)
        # Apply item-specific visual effects
        ContextualEffects.apply_item_effect(item_name, theme, "examine", llm, fallback_mode=self.fallback_mode)
    
    def display_combat_event(self, event_type: str, theme: str, message: str = "", llm=None):
        """
        Display combat events with spectacular effects
        """
        if message:
            print(message)
        ContextualEffects.apply_combat_effect(event_type, theme, llm)
    
    def display_death(self, cause: str, theme: str, llm=None):
        """
        Display dramatic death sequence
        """
        print(f"\n{Colors.PULSE_RED}💀 GAME OVER 💀{Colors.RESET}")
        print(f"{Colors.DIM}Cause of death: {cause}{Colors.RESET}")
        ContextualEffects.apply_death_effect(cause, theme, llm)
    
    def maybe_ambient_effect(self, theme: str, llm=None):
        """
        Randomly apply atmospheric ambient effects
        """
        ContextualEffects.random_ambient_effect(theme, 0.05, llm)  # 5% chance