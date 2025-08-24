"""
Terminal-based UI for Story Seed Generation in Cra-mud-gen
Provides interactive interface for creating story seeds using sliders, text, or random generation
"""
import os
import sys
import textwrap
from pathlib import Path
from typing import Optional, Dict, Any
from core.story_seed_generator import StorySeed, StorySeedGenerator


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    
    # Standard colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'


class SeedUI:
    """Terminal-based user interface for story seed generation"""
    
    def __init__(self, llm_interface=None, fallback_mode=False):
        """Initialize the UI system"""
        self.generator = StorySeedGenerator(llm_interface=llm_interface)
        self.current_seed = None
        self.fallback_mode = fallback_mode
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_welcome(self):
        """Display welcome screen and main menu"""
        self.clear_screen()
        
        print(f"{Colors.BRIGHT_CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}          Welcome to Cra-mud-gen Story Creation          {Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{'=' * 60}{Colors.RESET}")
        print()
        print(f"{Colors.YELLOW}Create your personalized dungeon adventure story!{Colors.RESET}")
        print()
    
    def get_generation_method(self) -> str:
        """Get user's preferred generation method"""
        
        print(f"{Colors.BRIGHT_BLUE}Story Generation Methods:{Colors.RESET}")
        print()
        print(f"  {Colors.BRIGHT_GREEN}1.{Colors.RESET} {Colors.CYAN}Custom Sliders{Colors.RESET} - Fine-tune mood, danger, mystery levels")
        print(f"  {Colors.BRIGHT_GREEN}2.{Colors.RESET} {Colors.YELLOW}Text Description{Colors.RESET} - Describe your story and let AI build it")
        print(f"  {Colors.BRIGHT_GREEN}3.{Colors.RESET} {Colors.MAGENTA}Random Generation{Colors.RESET} - Surprise me with something new!")
        print(f"  {Colors.BRIGHT_GREEN}4.{Colors.RESET} {Colors.WHITE}Load from File{Colors.RESET} - Use a previously saved seed")
        print()
        
        while True:
            choice = input(f"{Colors.BRIGHT_BLUE}Choose generation method (1-4): {Colors.RESET}")
            
            method_map = {
                '1': 'sliders',
                '2': 'text_only', 
                '3': 'random',
                '4': 'load_file'
            }
            
            if choice in method_map:
                return method_map[choice]
            else:
                print(f"{Colors.RED}Invalid choice. Please select 1-4.{Colors.RESET}")
    
    def get_slider_values(self) -> tuple:
        """Get slider values and custom text from user"""
        
        self.clear_screen()
        print(f"{Colors.BRIGHT_CYAN}Story Mood Configuration{Colors.RESET}")
        print(f"{Colors.YELLOW}Adjust the sliders to craft your perfect adventure tone{Colors.RESET}")
        print()
        
        sliders = {
            'danger': {'name': 'Danger Level', 'desc': 'Combat intensity and life-threatening situations', 'default': 6},
            'discovery': {'name': 'Discovery Factor', 'desc': 'Hidden secrets, lore, and exploration rewards', 'default': 7},
            'scary': {'name': 'Scary Factor', 'desc': 'Horror elements, jump scares, and creepy atmosphere', 'default': 4},
            'mystery': {'name': 'Mystery Level', 'desc': 'Puzzles, intrigue, and unknown elements', 'default': 5},
            'comedy': {'name': 'Comedy Level', 'desc': 'Humor, lighthearted moments, and funny NPCs', 'default': 2}
        }
        
        values = {}
        
        for key, info in sliders.items():
            print(f"{Colors.BRIGHT_BLUE}{info['name']}: {Colors.RESET}{info['desc']}")
            print(f"{Colors.GRAY}Default: {info['default']}{Colors.RESET}")
            
            while True:
                try:
                    user_input = input(f"{Colors.CYAN}Enter value (1-10) or press Enter for default: {Colors.RESET}")
                    
                    if user_input.strip() == '':
                        values[key] = info['default']
                        break
                    
                    value = int(user_input)
                    if 1 <= value <= 10:
                        values[key] = value
                        break
                    else:
                        print(f"{Colors.RED}Please enter a number between 1 and 10.{Colors.RESET}")
                        
                except ValueError:
                    print(f"{Colors.RED}Please enter a valid number.{Colors.RESET}")
            
            # Display the "slider" visually
            self._display_slider(info['name'], values[key])
            print()
        
        print(f"{Colors.BRIGHT_YELLOW}Current Settings Summary:{Colors.RESET}")
        for key, info in sliders.items():
            self._display_slider(info['name'], values[key], compact=True)
        print()
        
        # Get custom text
        print(f"{Colors.BRIGHT_BLUE}Custom Story Elements (Optional):{Colors.RESET}")
        print(f"{Colors.GRAY}Add any specific elements, themes, or inspirations{Colors.RESET}")
        print(f"{Colors.GRAY}Examples: 'Aliens movie but with comedic NPCs', 'Sci-fi haunted house'{Colors.RESET}")
        print()
        
        custom_text = input(f"{Colors.CYAN}Custom elements (press Enter to skip): {Colors.RESET}")
        
        return values, custom_text.strip()
    
    def _display_slider(self, name: str, value: int, compact: bool = False):
        """Display a visual slider representation"""
        bar_length = 10
        filled = '█' * value
        empty = '░' * (bar_length - value)
        
        if compact:
            print(f"  {Colors.CYAN}{name:15}{Colors.RESET} [{filled}{empty}] {value}/10")
        else:
            print(f"  {Colors.GREEN}[{filled}{empty}] {value}/10{Colors.RESET}")
    
    def get_text_input(self) -> str:
        """Get story description from user text input"""
        
        self.clear_screen()
        print(f"{Colors.BRIGHT_CYAN}Text-Based Story Creation{Colors.RESET}")
        print(f"{Colors.YELLOW}Describe your story idea and the AI will build a complete seed from it.{Colors.RESET}")
        print()
        print(f"{Colors.GRAY}Examples:{Colors.RESET}")
        print(f"  • {Colors.CYAN}'Space station where crew discovers alien parasites'{Colors.RESET}")
        print(f"  • {Colors.CYAN}'Medieval castle with a dragon and comedic knights'{Colors.RESET}")
        print(f"  • {Colors.CYAN}'Cyberpunk heist in a corporate megabuilding'{Colors.RESET}")
        print(f"  • {Colors.CYAN}'Horror mansion with friendly ghosts and dark secrets'{Colors.RESET}")
        print()
        
        while True:
            story_text = input(f"{Colors.BRIGHT_BLUE}Enter your story concept: {Colors.RESET}")
            
            if story_text.strip():
                return story_text.strip()
            else:
                print(f"{Colors.RED}Please enter a story description.{Colors.RESET}")
    
    def get_random_preferences(self) -> Optional[str]:
        """Get theme preference for random generation"""
        
        self.clear_screen()
        print(f"{Colors.BRIGHT_CYAN}Random Story Generation{Colors.RESET}")
        print(f"{Colors.YELLOW}Let the AI create a surprise adventure for you!{Colors.RESET}")
        print()
        print(f"{Colors.BRIGHT_BLUE}Theme Preferences:{Colors.RESET}")
        print(f"  {Colors.BRIGHT_GREEN}1.{Colors.RESET} {Colors.YELLOW}Fantasy{Colors.RESET} - Magic, dragons, and ancient mysteries")
        print(f"  {Colors.BRIGHT_GREEN}2.{Colors.RESET} {Colors.CYAN}Sci-Fi{Colors.RESET} - Space, technology, and alien encounters")
        print(f"  {Colors.BRIGHT_GREEN}3.{Colors.RESET} {Colors.RED}Horror{Colors.RESET} - Fear, suspense, and supernatural threats")
        print(f"  {Colors.BRIGHT_GREEN}4.{Colors.RESET} {Colors.MAGENTA}Cyberpunk{Colors.RESET} - Neon, hackers, and corporate intrigue")
        print(f"  {Colors.BRIGHT_GREEN}5.{Colors.RESET} {Colors.WHITE}Complete Surprise{Colors.RESET} - Randomly choose everything")
        print()
        
        choice = input(f"{Colors.BRIGHT_BLUE}Choose theme preference (1-5): {Colors.RESET}")
        
        theme_map = {
            '1': 'fantasy',
            '2': 'sci-fi', 
            '3': 'horror',
            '4': 'cyberpunk',
            '5': None
        }
        
        return theme_map.get(choice)
    
    def get_file_path(self) -> Optional[str]:
        """Get file path for loading a seed"""
        
        print(f"{Colors.BRIGHT_CYAN}Load Story Seed from File{Colors.RESET}")
        print()
        
        # Show available files in seeds directory if it exists
        seeds_dir = Path("seeds")
        if seeds_dir.exists() and seeds_dir.is_dir():
            seed_files = list(seeds_dir.glob("*.json"))
            if seed_files:
                print(f"{Colors.YELLOW}Available seed files:{Colors.RESET}")
                for i, file in enumerate(seed_files, 1):
                    print(f"  {Colors.BRIGHT_GREEN}{i}.{Colors.RESET} {Colors.CYAN}{file.name}{Colors.RESET}")
                print()
        
        filepath = input(f"{Colors.CYAN}Enter filename (or full path, or press Enter to cancel): {Colors.RESET}")
        
        if not filepath.strip():
            return None
        
        filepath = filepath.strip()
        
        # If it's just a filename, look in seeds directory first
        if not os.path.sep in filepath and not filepath.startswith(('./', '../')):
            seeds_path = seeds_dir / filepath
            if not filepath.endswith('.json'):
                seeds_path = seeds_dir / f"{filepath}.json"
            
            if seeds_path.exists():
                return str(seeds_path)
        
        # Otherwise return as-is (could be full path or relative path)
        return filepath
    
    def display_seed_preview(self, seed: StorySeed) -> Optional[bool]:
        """Display seed preview and get user confirmation"""
        
        self.clear_screen()
        
        print(f"{Colors.BRIGHT_CYAN}Generated Story Seed Preview{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}{'=' * 50}{Colors.RESET}")
        print()
        
        # Basic info
        print(f"{Colors.BRIGHT_YELLOW}Theme:{Colors.RESET} {Colors.CYAN}{seed.theme.title()}{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}Setting:{Colors.RESET} {Colors.GREEN}{seed.setting}{Colors.RESET}")
        print()
        
        # Mood sliders
        print(f"{Colors.BRIGHT_BLUE}Mood Profile:{Colors.RESET}")
        moods = [
            ('Danger', seed.danger_level),
            ('Discovery', seed.discovery_factor),
            ('Scary', seed.scary_factor),
            ('Mystery', seed.mystery_level),
            ('Comedy', seed.comedy_level)
        ]
        
        for name, value in moods:
            self._display_slider(name, value, compact=True)
        print()
        
        # Story elements
        if seed.conflict:
            print(f"{Colors.BRIGHT_YELLOW}Main Conflict:{Colors.RESET}")
            # Wrap text to prevent cutoff
            wrapped_lines = textwrap.wrap(seed.conflict, width=76, initial_indent="  ", subsequent_indent="  ")
            for line in wrapped_lines:
                print(f"{Colors.WHITE}{line}{Colors.RESET}")
            print()
        
        if seed.main_characters:
            print(f"{Colors.BRIGHT_YELLOW}Key Characters:{Colors.RESET}")
            for char in seed.main_characters[:3]:  # Show up to 3
                print(f"  • {Colors.CYAN}{char}{Colors.RESET}")
            print()
        
        if seed.story_beats:
            print(f"{Colors.BRIGHT_YELLOW}Story Progression:{Colors.RESET}")
            for i, beat in enumerate(seed.story_beats[:5], 1):  # Show up to 5
                # Wrap long story beats
                wrapped_lines = textwrap.wrap(beat, width=74, initial_indent=f"  {i}. ", subsequent_indent="     ")
                for j, line in enumerate(wrapped_lines):
                    if j == 0:
                        print(f"  {Colors.BRIGHT_GREEN}{i}.{Colors.RESET} {Colors.WHITE}{line[4:]}{Colors.RESET}")
                    else:
                        print(f"     {Colors.WHITE}{line[5:]}{Colors.RESET}")
            print()
        
        if seed.custom_text:
            print(f"{Colors.BRIGHT_YELLOW}Custom Elements:{Colors.RESET}")
            # Wrap custom text
            wrapped_lines = textwrap.wrap(seed.custom_text, width=76, initial_indent="  ", subsequent_indent="  ")
            for line in wrapped_lines:
                print(f"{Colors.GRAY}{line}{Colors.RESET}")
            print()
        
        # Generation info
        method_names = {
            'sliders': 'Custom Sliders + Text',
            'text_only': 'Text Input Only',
            'random': 'Random Generation',
            'custom': 'Custom Configuration'
        }
        
        print(f"{Colors.GRAY}Generated via: {method_names.get(seed.generation_method, seed.generation_method)}{Colors.RESET}")
        if seed.iteration_count > 0:
            print(f"{Colors.GRAY}AI Iterations: {seed.iteration_count}{Colors.RESET}")
        print()
        
        # User choice
        while True:
            print(f"{Colors.BRIGHT_BLUE}Options:{Colors.RESET}")
            print(f"  {Colors.BRIGHT_GREEN}1.{Colors.RESET} {Colors.YELLOW}Accept and Start Game{Colors.RESET}")
            print(f"  {Colors.BRIGHT_GREEN}2.{Colors.RESET} {Colors.CYAN}Regenerate with Same Settings{Colors.RESET}")
            print(f"  {Colors.BRIGHT_GREEN}3.{Colors.RESET} {Colors.MAGENTA}Go Back to Method Selection{Colors.RESET}")
            print(f"  {Colors.BRIGHT_GREEN}4.{Colors.RESET} {Colors.WHITE}Save Seed to File{Colors.RESET}")
            print()
            
            choice = input(f"{Colors.BRIGHT_BLUE}Choose option (1-4): {Colors.RESET}")
            
            if choice == '1':
                return True
            elif choice == '2':
                return False
            elif choice == '3':
                return None  # Signal to restart method selection
            elif choice == '4':
                self._save_seed_to_file(seed)
                print(f"{Colors.GREEN}Seed saved! Press Enter to continue...{Colors.RESET}")
                input()
                continue
            else:
                print(f"{Colors.RED}Invalid choice. Please select 1-4.{Colors.RESET}")
    
    def _save_seed_to_file(self, seed: StorySeed):
        """Save seed to user-specified file"""
        # Create seeds directory if it doesn't exist
        seeds_dir = Path("seeds")
        seeds_dir.mkdir(exist_ok=True)
        
        while True:
            filename = input(f"{Colors.CYAN}Enter filename (without .json): {Colors.RESET}")
            if filename.strip():
                filepath = seeds_dir / f"{filename.strip()}.json"
                if self.generator.export_seed(seed, str(filepath)):
                    print(f"{Colors.GREEN}Seed saved to {filepath}{Colors.RESET}")
                    return
                else:
                    print(f"{Colors.RED}Failed to save seed. Try a different filename.{Colors.RESET}")
            else:
                print(f"{Colors.RED}Please enter a valid filename.{Colors.RESET}")
    
    def display_generation_progress(self, method: str, iteration: int = 0):
        """Display progress while generating seed"""
        messages = {
            'sliders': [
                "Analyzing your mood preferences...",
                "Incorporating custom elements...",
                "Building story structure...",
                "Finalizing narrative details..."
            ],
            'text_only': [
                "Processing your story concept...",
                "Enhancing narrative complexity...",
                "Adding character depth...",
                "Polishing story details..."
            ],
            'random': [
                "Rolling cosmic dice...",
                "Consulting the story spirits...",
                "Weaving narrative threads...",
                "Adding surprise elements..."
            ]
        }
        
        method_messages = messages.get(method, messages['sliders'])
        
        if iteration < len(method_messages):
            message = method_messages[iteration]
            print(f"{Colors.BRIGHT_YELLOW}🎲 {message}{Colors.RESET}")
            print(f"{Colors.CYAN}{'.' * (iteration * 3 + 3)}{Colors.RESET}")
            print()
    
    def display_error(self, error_message: str):
        """Display error message"""
        print(f"{Colors.RED}Error: {error_message}{Colors.RESET}")
        print(f"{Colors.GRAY}Press Enter to continue...{Colors.RESET}")
        input()
    
    def run_seed_generation_flow(self) -> Optional[StorySeed]:
        """Run the complete seed generation flow"""
        
        while True:
            self.display_welcome()
            method = self.get_generation_method()
            
            try:
                seed = None
                
                if method == 'sliders':
                    slider_values, custom_text = self.get_slider_values()
                    self.clear_screen()
                    self.display_generation_progress('sliders', 0)
                    
                    seed = self.generator.generate_from_sliders(slider_values, custom_text)
                    
                elif method == 'text_only':
                    story_text = self.get_text_input()
                    self.clear_screen()
                    self.display_generation_progress('text_only', 0)
                    
                    seed = self.generator.generate_from_text(story_text)
                    
                elif method == 'random':
                    theme_pref = self.get_random_preferences()
                    self.clear_screen()
                    self.display_generation_progress('random', 0)
                    
                    seed = self.generator.generate_random(theme_pref)
                    
                elif method == 'load_file':
                    filepath = self.get_file_path()
                    if not filepath:
                        continue  # Back to method selection
                    
                    seed = self.generator.import_seed(filepath)
                    if not seed:
                        self.display_error("Failed to load seed from file")
                        continue
                
                if seed:
                    # Validate seed
                    is_valid, issues = self.generator.validate_seed(seed)
                    if not is_valid:
                        self.display_error(f"Generated seed has issues: {', '.join(issues)}")
                        continue
                    
                    # Show preview and get user decision
                    result = self.display_seed_preview(seed)
                    
                    if result is True:
                        # User accepted
                        self.current_seed = seed
                        return seed
                    elif result is False:
                        # Regenerate with same method
                        continue
                    elif result is None:
                        # Go back to method selection
                        continue
                    
            except Exception as e:
                self.display_error(f"An error occurred during generation: {str(e)}")
                continue
        
        return None
    
    def get_current_seed(self) -> Optional[StorySeed]:
        """Get the currently generated seed"""
        return self.current_seed