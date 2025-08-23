"""
ANSI Color and Effect System for Terminal UI
Provides colors, effects, and animations for Dun-Gen
"""
import time
import sys
import math
import random
from typing import Dict, List

class Colors:
    """ANSI color codes and text effects"""
    
    # Reset
    RESET = '\033[0m'
    CLEAR = '\033[2J\033[H'
    
    # Basic Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright Colors (Glowing Effect)
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background Colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Text Effects
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'           # Pulsing effect
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'
    
    # Special RGB Colors (256-color mode)
    ORANGE = '\033[38;5;214m'
    PURPLE = '\033[38;5;129m'
    PINK = '\033[38;5;213m'
    GOLD = '\033[38;5;220m'
    SILVER = '\033[38;5;250m'
    
    # Glowing RGB combinations
    GLOW_RED = '\033[91m\033[1m'        # Bright red + bold
    GLOW_GREEN = '\033[92m\033[1m'      # Bright green + bold  
    GLOW_BLUE = '\033[94m\033[1m'       # Bright blue + bold
    GLOW_YELLOW = '\033[93m\033[1m'     # Bright yellow + bold
    GLOW_MAGENTA = '\033[95m\033[1m'    # Bright magenta + bold
    GLOW_CYAN = '\033[96m\033[1m'       # Bright cyan + bold
    
    # Pulsing Glow (blink + bright + bold)
    PULSE_RED = '\033[91m\033[1m\033[5m'
    PULSE_GREEN = '\033[92m\033[1m\033[5m'
    PULSE_BLUE = '\033[94m\033[1m\033[5m'
    PULSE_YELLOW = '\033[93m\033[1m\033[5m'
    PULSE_MAGENTA = '\033[95m\033[1m\033[5m'
    
    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """Create RGB color (0-255 values)"""
        return f'\033[38;2;{r};{g};{b}m'
    
    @staticmethod
    def bg_rgb(r: int, g: int, b: int) -> str:
        """Create RGB background color"""
        return f'\033[48;2;{r};{g};{b}m'

class ColorThemes:
    """Color themes for different game elements"""
    
    # Health status colors
    HEALTH_CRITICAL = Colors.PULSE_RED      # < 25% health
    HEALTH_LOW = Colors.GLOW_RED           # < 50% health  
    HEALTH_MEDIUM = Colors.BRIGHT_YELLOW   # < 75% health
    HEALTH_GOOD = Colors.BRIGHT_GREEN      # >= 75% health
    
    # Item rarity colors
    ITEM_COMMON = Colors.WHITE
    ITEM_UNCOMMON = Colors.BRIGHT_GREEN
    ITEM_RARE = Colors.BRIGHT_BLUE
    ITEM_EPIC = Colors.BRIGHT_MAGENTA
    ITEM_LEGENDARY = Colors.GLOW_YELLOW
    ITEM_ARTIFACT = Colors.PULSE_MAGENTA
    
    # Game themes
    FANTASY = {
        'primary': Colors.BRIGHT_MAGENTA,
        'secondary': Colors.BRIGHT_YELLOW,
        'accent': Colors.BRIGHT_CYAN,
        'danger': Colors.BRIGHT_RED,
        'success': Colors.BRIGHT_GREEN
    }
    
    SCIFI = {
        'primary': Colors.BRIGHT_CYAN,
        'secondary': Colors.BRIGHT_BLUE, 
        'accent': Colors.BRIGHT_GREEN,
        'danger': Colors.BRIGHT_RED,
        'success': Colors.BRIGHT_GREEN
    }
    
    HORROR = {
        'primary': Colors.BRIGHT_RED,
        'secondary': Colors.DIM + Colors.WHITE,
        'accent': Colors.BRIGHT_BLACK,
        'danger': Colors.PULSE_RED,
        'success': Colors.DIM + Colors.GREEN
    }
    
    CYBERPUNK = {
        'primary': Colors.rgb(0, 255, 255),    # Neon cyan
        'secondary': Colors.rgb(255, 0, 255),  # Neon magenta
        'accent': Colors.rgb(255, 255, 0),     # Neon yellow
        'danger': Colors.rgb(255, 0, 0),       # Neon red
        'success': Colors.rgb(0, 255, 0)       # Neon green
    }

class Effects:
    """Advanced special effects and animations"""
    
    @staticmethod
    def typewriter(text: str, delay: float = 0.03, color: str = Colors.WHITE):
        """Typewriter effect - prints text character by character"""
        colored_text = f"{color}{text}{Colors.RESET}"
        for i, char in enumerate(colored_text):
            if char == '\033':  # Skip ANSI escape sequences
                # Find the end of the escape sequence
                end = colored_text.find('m', i)
                if end != -1:
                    sys.stdout.write(colored_text[i:end+1])
                    sys.stdout.flush()
                    continue
            sys.stdout.write(char)
            sys.stdout.flush()
            if char not in ['\033', '[', ';'] and not char.isdigit() and char != 'm':
                time.sleep(delay)
    
    @staticmethod
    def glow_pulse(text: str, color: str = Colors.GLOW_RED, cycles: int = 3):
        """Creates a pulsing glow effect"""
        for i in range(cycles):
            # Bright phase
            print(f"\r{color}{text}{Colors.RESET}", end='', flush=True)
            time.sleep(0.3)
            # Dim phase  
            print(f"\r{Colors.DIM}{text}{Colors.RESET}", end='', flush=True)
            time.sleep(0.3)
        print(f"\r{color}{text}{Colors.RESET}")
    
    @staticmethod
    def shimmer_pond(text: str, duration: float = 3.0):
        """Shimmering water effect with rippling blues and cyans"""
        colors = [
            Colors.rgb(0, 100, 200),    # Deep blue
            Colors.rgb(0, 150, 255),    # Medium blue
            Colors.rgb(100, 200, 255),  # Light blue
            Colors.rgb(150, 255, 255),  # Cyan
            Colors.rgb(200, 255, 255),  # Light cyan
            Colors.rgb(100, 255, 255),  # Bright cyan
            Colors.rgb(0, 200, 255),    # Blue-cyan
            Colors.rgb(0, 150, 200)     # Back to deep
        ]
        
        end_time = time.time() + duration
        frame = 0
        
        while time.time() < end_time:
            # Create wave effect by shifting colors
            colored_chars = []
            for i, char in enumerate(text):
                if char == ' ':
                    colored_chars.append(' ')
                else:
                    color_idx = (i + frame) % len(colors)
                    colored_chars.append(f"{colors[color_idx]}{char}")
            
            ripple_text = ''.join(colored_chars) + Colors.RESET
            print(f"\r{ripple_text}", end='', flush=True)
            
            time.sleep(0.15)
            frame += 1
            
        print()  # New line at end
    
    @staticmethod
    def burning_flame(text: str, duration: float = 2.5):
        """Flickering flame effect with dynamic red/orange/yellow"""
        import random
        
        # Flame colors from hot to cool
        flame_colors = [
            Colors.rgb(255, 255, 100),  # Hot yellow
            Colors.rgb(255, 200, 0),    # Orange-yellow
            Colors.rgb(255, 150, 0),    # Orange
            Colors.rgb(255, 100, 0),    # Red-orange
            Colors.rgb(255, 50, 0),     # Red
            Colors.rgb(200, 0, 0),      # Deep red
        ]
        
        end_time = time.time() + duration
        
        while time.time() < end_time:
            # Each character flickers independently
            colored_chars = []
            for char in text:
                if char == ' ':
                    colored_chars.append(' ')
                else:
                    # Random flicker intensity
                    flicker_level = random.randint(0, len(flame_colors) - 1)
                    color = flame_colors[flicker_level]
                    
                    # Add brightness variation
                    if random.random() < 0.3:  # 30% chance of extra bright
                        colored_chars.append(f"{color}{Colors.BOLD}{char}")
                    else:
                        colored_chars.append(f"{color}{char}")
            
            flame_text = ''.join(colored_chars) + Colors.RESET
            print(f"\r{flame_text}", end='', flush=True)
            
            # Variable flicker speed
            time.sleep(random.uniform(0.08, 0.20))
            
        print()
    
    @staticmethod
    def lightning_strike(text: str, strikes: int = 3):
        """Lightning effect with sudden bright flashes"""
        for i in range(strikes):
            # Darkness before strike
            if i > 0:
                print(f"\r{Colors.DIM}{Colors.BLUE}{text}{Colors.RESET}", end='', flush=True)
                time.sleep(random.uniform(0.3, 0.8))
            
            # Lightning flash - multiple rapid flickers
            for flash in range(random.randint(2, 4)):
                print(f"\r{Colors.rgb(255, 255, 255)}{Colors.BOLD}{text}{Colors.RESET}", end='', flush=True)
                time.sleep(0.05)
                print(f"\r{Colors.rgb(200, 200, 255)}{text}{Colors.RESET}", end='', flush=True)
                time.sleep(0.03)
            
            # Thunder roll (fading)
            fade_colors = [
                Colors.rgb(150, 150, 255),
                Colors.rgb(100, 100, 255),
                Colors.rgb(50, 50, 200),
                Colors.rgb(0, 0, 150)
            ]
            
            for fade_color in fade_colors:
                print(f"\r{fade_color}{text}{Colors.RESET}", end='', flush=True)
                time.sleep(0.1)
                
        print()
    
    @staticmethod
    def crystal_sparkle(text: str, duration: float = 2.0):
        """Sparkling crystal effect with random bright spots"""
        import random
        
        sparkle_chars = ['✦', '✧', '★', '☆', '✯', '✨', '⭐', '💎']
        end_time = time.time() + duration
        
        while time.time() < end_time:
            display_chars = []
            
            for i, char in enumerate(text):
                if char == ' ':
                    display_chars.append(' ')
                elif random.random() < 0.15:  # 15% chance of sparkle
                    sparkle = random.choice(sparkle_chars)
                    sparkle_color = random.choice([
                        Colors.rgb(255, 255, 255),  # White
                        Colors.rgb(200, 200, 255),  # Blue-white
                        Colors.rgb(255, 200, 255),  # Pink-white
                        Colors.rgb(200, 255, 200),  # Green-white
                    ])
                    display_chars.append(f"{sparkle_color}{Colors.BOLD}{sparkle}")
                else:
                    # Base crystal color
                    crystal_color = Colors.rgb(150, 150, 255)
                    display_chars.append(f"{crystal_color}{char}")
            
            sparkle_text = ''.join(display_chars) + Colors.RESET
            print(f"\r{sparkle_text}", end='', flush=True)
            time.sleep(0.1)
            
        print()
    
    @staticmethod
    def toxic_bubble(text: str, duration: float = 2.5):
        """Bubbling toxic/poison effect with greens"""
        import random
        
        toxic_colors = [
            Colors.rgb(0, 255, 0),      # Bright green
            Colors.rgb(50, 255, 50),    # Light green
            Colors.rgb(0, 200, 0),      # Medium green
            Colors.rgb(100, 255, 0),    # Yellow-green
            Colors.rgb(0, 255, 100),    # Blue-green
        ]
        
        end_time = time.time() + duration
        bubble_frame = 0
        
        while time.time() < end_time:
            colored_chars = []
            
            for i, char in enumerate(text):
                if char == ' ':
                    colored_chars.append(' ')
                else:
                    # Create bubbling effect
                    bubble_intensity = abs(int(3 * math.sin(bubble_frame * 0.3 + i * 0.5))) % len(toxic_colors)
                    color = toxic_colors[bubble_intensity]
                    
                    # Random bubble pop effect
                    if random.random() < 0.1:
                        colored_chars.append(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}○{Colors.RESET}")
                    else:
                        colored_chars.append(f"{color}{char}")
            
            bubble_text = ''.join(colored_chars) + Colors.RESET
            print(f"\r{bubble_text}", end='', flush=True)
            
            time.sleep(0.12)
            bubble_frame += 1
            
        print()
    
    @staticmethod
    def void_corruption(text: str, duration: float = 2.0):
        """Dark void corruption with purple/black tendrils"""
        import random
        
        void_colors = [
            Colors.rgb(50, 0, 50),      # Dark purple
            Colors.rgb(80, 0, 80),      # Medium purple
            Colors.rgb(100, 0, 100),    # Purple
            Colors.rgb(150, 0, 150),    # Bright purple
            Colors.rgb(0, 0, 0),        # Black
            Colors.rgb(30, 0, 30),      # Very dark purple
        ]
        
        corruption_chars = ['▓', '▒', '░', '█', '▄', '▀', '◆', '◇']
        end_time = time.time() + duration
        
        while time.time() < end_time:
            display_chars = []
            
            for i, char in enumerate(text):
                if char == ' ':
                    display_chars.append(' ')
                elif random.random() < 0.2:  # 20% corruption chance
                    corrupt_char = random.choice(corruption_chars)
                    corrupt_color = random.choice(void_colors)
                    display_chars.append(f"{corrupt_color}{corrupt_char}")
                else:
                    # Fading original text
                    fade_color = random.choice(void_colors[2:4])  # Medium fade
                    display_chars.append(f"{fade_color}{char}")
            
            corrupt_text = ''.join(display_chars) + Colors.RESET
            print(f"\r{corrupt_text}", end='', flush=True)
            time.sleep(0.15)
            
        print()
        
    @staticmethod
    def aurora_dance(text: str, duration: float = 3.0):
        """Northern lights aurora effect with flowing colors"""
        import math
        
        end_time = time.time() + duration
        frame = 0
        
        while time.time() < end_time:
            colored_chars = []
            
            for i, char in enumerate(text):
                if char == ' ':
                    colored_chars.append(' ')
                else:
                    # Create flowing aurora colors
                    wave1 = math.sin(frame * 0.1 + i * 0.3) * 127 + 128
                    wave2 = math.sin(frame * 0.15 + i * 0.2) * 127 + 128
                    wave3 = math.sin(frame * 0.12 + i * 0.4) * 127 + 128
                    
                    r = int(wave1 * 0.3)
                    g = int(wave2 * 0.8)
                    b = int(wave3 * 0.9)
                    
                    # Ensure colors stay in aurora range
                    r = max(0, min(255, r + 50))
                    g = max(0, min(255, g + 100))
                    b = max(0, min(255, b + 150))
                    
                    color = Colors.rgb(r, g, b)
                    colored_chars.append(f"{color}{char}")
            
            aurora_text = ''.join(colored_chars) + Colors.RESET
            print(f"\r{aurora_text}", end='', flush=True)
            
            time.sleep(0.08)
            frame += 1
            
        print()
    
    @staticmethod
    def rainbow_text(text: str) -> str:
        """Apply rainbow colors to text"""
        colors = [
            Colors.BRIGHT_RED,
            Colors.BRIGHT_YELLOW, 
            Colors.BRIGHT_GREEN,
            Colors.BRIGHT_CYAN,
            Colors.BRIGHT_BLUE,
            Colors.BRIGHT_MAGENTA
        ]
        result = ""
        for i, char in enumerate(text):
            if char != ' ':
                result += colors[i % len(colors)] + char
            else:
                result += char
        return result + Colors.RESET
    
    @staticmethod
    def fire_text(text: str) -> str:
        """Create fire effect with red/orange/yellow"""
        colors = [Colors.BRIGHT_RED, Colors.ORANGE, Colors.BRIGHT_YELLOW]
        result = ""
        for i, char in enumerate(text):
            if char != ' ':
                result += colors[i % len(colors)] + char
            else:
                result += char
        return result + Colors.RESET
    
    @staticmethod
    def matrix_text(text: str) -> str:
        """Matrix-style green text effect"""
        return f"{Colors.BRIGHT_GREEN}{Colors.BOLD}{text}{Colors.RESET}"
    
    @staticmethod
    def horror_text(text: str) -> str:
        """Creepy horror text effect"""
        return f"{Colors.DIM}{Colors.RED}{text}{Colors.RESET}"
    
    @staticmethod
    def snow_fall(text: str, duration: float = 3.0):
        """Falling snow effect with white particles"""
        snow_chars = ['❄', '❅', '❆', '*', '·', '∘', '○']
        end_time = time.time() + duration
        
        while time.time() < end_time:
            # Create snow overlay
            display_chars = []
            
            for i, char in enumerate(text):
                if char == ' ' and random.random() < 0.15:
                    # Random snowflake
                    snow = random.choice(snow_chars)
                    snow_color = random.choice([
                        Colors.BRIGHT_WHITE,
                        Colors.rgb(240, 240, 255),
                        Colors.rgb(200, 200, 255)
                    ])
                    display_chars.append(f"{snow_color}{snow}")
                else:
                    # Original text with slight blue tint (cold)
                    cold_color = Colors.rgb(200, 220, 255)
                    display_chars.append(f"{cold_color}{char}")
            
            snow_text = ''.join(display_chars) + Colors.RESET
            print(f"\r{snow_text}", end='', flush=True)
            time.sleep(0.2)
            
        print()
    
    @staticmethod
    def lava_flow(text: str, duration: float = 2.5):
        """Molten lava flow effect"""
        lava_colors = [
            Colors.rgb(255, 0, 0),      # Bright red
            Colors.rgb(255, 100, 0),    # Orange-red
            Colors.rgb(255, 150, 0),    # Orange
            Colors.rgb(255, 255, 0),    # Yellow (hottest)
            Colors.rgb(200, 0, 0),      # Dark red
            Colors.rgb(150, 0, 0),      # Darker red
        ]
        
        end_time = time.time() + duration
        flow_frame = 0
        
        while time.time() < end_time:
            colored_chars = []
            
            for i, char in enumerate(text):
                if char == ' ':
                    colored_chars.append(' ')
                else:
                    # Create flowing effect
                    heat_level = int((math.sin(flow_frame * 0.2 + i * 0.4) + 1) * 3) % len(lava_colors)
                    color = lava_colors[heat_level]
                    
                    # Random spark effect
                    if random.random() < 0.08:
                        colored_chars.append(f"{Colors.BRIGHT_YELLOW}{Colors.BOLD}*")
                    else:
                        colored_chars.append(f"{color}{char}")
            
            lava_text = ''.join(colored_chars) + Colors.RESET
            print(f"\r{lava_text}", end='', flush=True)
            
            time.sleep(0.1)
            flow_frame += 1
            
        print()
    
    @staticmethod
    def electric_storm(text: str, duration: float = 2.0):
        """Electric/energy storm effect"""
        electric_chars = ['⚡', '※', '⟐', '⟡', '⟢', '☇', '∞', '≋']
        electric_colors = [
            Colors.rgb(100, 100, 255),  # Blue electric
            Colors.rgb(150, 150, 255),  # Light blue
            Colors.rgb(255, 255, 255),  # White spark
            Colors.rgb(200, 200, 255),  # Blue-white
        ]
        
        end_time = time.time() + duration
        
        while time.time() < end_time:
            display_chars = []
            
            for i, char in enumerate(text):
                if random.random() < 0.2:  # 20% electric chance
                    spark = random.choice(electric_chars)
                    spark_color = random.choice(electric_colors)
                    display_chars.append(f"{spark_color}{Colors.BOLD}{spark}")
                else:
                    # Base electric glow
                    base_color = Colors.rgb(150, 150, 255)
                    display_chars.append(f"{base_color}{char}")
            
            electric_text = ''.join(display_chars) + Colors.RESET
            print(f"\r{electric_text}", end='', flush=True)
            time.sleep(0.12)
            
        print()
    
    @staticmethod
    def smoke_drift(text: str, duration: float = 2.5):
        """Drifting smoke effect"""
        smoke_chars = ['░', '▒', '▓', '▄', '▀', '■', '▪', '▫']
        smoke_colors = [
            Colors.rgb(100, 100, 100),  # Gray
            Colors.rgb(150, 150, 150),  # Light gray
            Colors.rgb(80, 80, 80),     # Dark gray
            Colors.rgb(60, 60, 60),     # Very dark gray
        ]
        
        end_time = time.time() + duration
        drift_frame = 0
        
        while time.time() < end_time:
            display_chars = []
            
            for i, char in enumerate(text):
                # Create drifting smoke pattern
                smoke_density = math.sin(drift_frame * 0.15 + i * 0.3) + 1
                
                if smoke_density > 1.3 and random.random() < 0.3:
                    smoke = random.choice(smoke_chars)
                    smoke_color = random.choice(smoke_colors)
                    display_chars.append(f"{smoke_color}{smoke}")
                else:
                    # Faded original text
                    fade_color = Colors.rgb(120, 120, 120)
                    display_chars.append(f"{fade_color}{char}")
            
            smoke_text = ''.join(display_chars) + Colors.RESET
            print(f"\r{smoke_text}", end='', flush=True)
            
            time.sleep(0.15)
            drift_frame += 1
            
        print()
    
    @staticmethod
    def matrix_rain(text: str, duration: float = 2.5):
        """Matrix digital rain effect"""
        matrix_chars = ['0', '1', '｜', '¦', '︙', '⁞', '⸽', '𝟶', '𝟷', '𝟸', '𝟹']
        
        end_time = time.time() + duration
        rain_frame = 0
        
        while time.time() < end_time:
            display_chars = []
            
            for i, char in enumerate(text):
                # Rain drops at different positions
                rain_position = (rain_frame + i * 3) % 8
                
                if rain_position < 2 and random.random() < 0.4:
                    drop = random.choice(matrix_chars)
                    drop_intensity = random.choice([
                        Colors.BRIGHT_GREEN,
                        Colors.GREEN,
                        Colors.rgb(0, 255, 100)
                    ])
                    display_chars.append(f"{drop_intensity}{drop}")
                elif char == ' ':
                    display_chars.append(' ')
                else:
                    # Fading green text
                    fade_color = Colors.rgb(0, 150, 0)
                    display_chars.append(f"{fade_color}{char}")
            
            matrix_text = ''.join(display_chars) + Colors.RESET
            print(f"\r{matrix_text}", end='', flush=True)
            
            time.sleep(0.1)
            rain_frame += 1
            
        print()
    
    @staticmethod
    def neon_glow(text: str, r: int = 0, g: int = 255, b: int = 255) -> str:
        """Neon glow effect with custom RGB"""
        glow_color = Colors.rgb(r, g, b)
        return f"{glow_color}{Colors.BOLD}{text}{Colors.RESET}"

class StatusBar:
    """Animated status bars and indicators"""
    
    @staticmethod
    def health_bar(current: int, maximum: int, width: int = 20) -> str:
        """Animated health bar with colors"""
        percentage = current / maximum
        filled = int(width * percentage)
        empty = width - filled
        
        # Choose color based on health percentage
        if percentage < 0.25:
            color = ColorThemes.HEALTH_CRITICAL
        elif percentage < 0.5:
            color = ColorThemes.HEALTH_LOW
        elif percentage < 0.75:
            color = ColorThemes.HEALTH_MEDIUM
        else:
            color = ColorThemes.HEALTH_GOOD
        
        bar = f"{color}{'█' * filled}{Colors.DIM}{'░' * empty}{Colors.RESET}"
        return f"[{bar}] {current}/{maximum}"
    
    @staticmethod
    def loading_animation(message: str, duration: float = 2.0):
        """Spinning loading animation"""
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for char in chars:
                print(f"\r{Colors.BRIGHT_CYAN}{char} {message}...{Colors.RESET}", end='', flush=True)
                time.sleep(0.1)
                if time.time() >= end_time:
                    break
        
        print(f"\r{Colors.BRIGHT_GREEN}✓ {message} complete!{Colors.RESET}")