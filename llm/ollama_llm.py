"""
Ollama LLM integration for the MUD game - using Mistral-Small
"""
import requests
import json
from typing import Dict, Any, Optional

class OllamaLLM:
    """
    Ollama LLM interface - connects to Mistral-Small model
    """
    
    def __init__(self, model_name: str = "mistral-small:22b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.is_model_loaded = self._check_model_availability()
        
    def _check_model_availability(self) -> bool:
        """
        Check if Ollama is running and Mistral model is available
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                # Check for mistral-small specifically
                if any("mistral-small" in name for name in model_names):
                    print(f"✓ Mistral-Small model is ready for adventure!")
                    return True
                elif models:
                    print(f"✗ Mistral-Small not found. Available models: {', '.join(model_names[:3])}")
                    print(f"Please run: ollama pull mistral-small:22b")
                    return False
                else:
                    print(f"✗ No models found. Run: ollama pull mistral-small:22b")
                    return False
        except:
            print("✗ Ollama not running. Start with: ollama serve")
            return False
    
    def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a response using Mistral-Small
        """
        if not self.is_available():
            return "The ancient magic remains silent..."
        
        try:
            # Build context-aware prompt optimized for Mistral
            theme = context.get("theme", "fantasy") if context else "fantasy"
            
            # Mistral responds well to clear, structured prompts
            system_message = f"""You are an immersive narrator for a {theme}-themed MUD (text adventure) game.
            
            Style Guidelines:
            - Write in second person ("You see...", "You feel...")
            - Keep responses to 2-3 sentences maximum
            - Be atmospheric and descriptive
            - Match the {theme} theme perfectly
            - Focus on sensory details (sight, sound, smell, touch)
            - Never break character or mention game mechanics"""
            
            # For room descriptions, add extra context
            if "room" in prompt.lower() or "describe" in prompt.lower():
                if context and "room_description" in context:
                    prompt = f"{prompt}\nCurrent setting: {context['room_description']}"
            
            # Make the API call with Mistral-optimized parameters
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": f"{system_message}\n\nRequest: {prompt}\n\nResponse:",
                    "stream": False,
                    "options": {
                        "temperature": 0.85,  # Slightly higher for Mistral's creativity
                        "top_p": 0.92,
                        "top_k": 40,
                        "num_predict": 150,   # Token limit for responses
                        "stop": ["\n\n", "Request:", "Response:"]  # Stop sequences
                    }
                },
                timeout=15  # Mistral might need a bit more time
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                # Clean up any repeated text or artifacts
                if generated_text:
                    # Remove any accidental prompt leakage
                    generated_text = generated_text.replace("Request:", "").replace("Response:", "").strip()
                    return generated_text
                else:
                    return "The mystical energies swirl mysteriously..."
            else:
                return "The ancient forces stir but remain silent..."
                
        except requests.exceptions.Timeout:
            return "The mystical forces take time to gather..."
        except Exception as e:
            print(f"Error with Mistral generation: {e}")
            return "The mystical energies fade away..."
    
    def is_available(self) -> bool:
        """
        Check if Mistral model is available
        """
        if not self.is_model_loaded:
            self.is_model_loaded = self._check_model_availability()
        return self.is_model_loaded
    
    def generate_room_description(self, base_description: str, theme: str) -> str:
        """
        Special method for enhanced room descriptions using Mistral
        """
        context = {"theme": theme, "room_description": base_description}
        prompt = f"Enhance this {theme} room with vivid sensory details: {base_description}"
        return self.generate_response(prompt, context)
    
    def generate_movement_text(self, direction: str, theme: str) -> str:
        """
        Generate movement descriptions using Mistral
        """
        context = {"theme": theme}
        prompt = f"Describe the player moving {direction} through a {theme} environment"
        return self.generate_response(prompt, context)
    
    def generate_item_description(self, item: str, theme: str) -> str:
        """
        Generate item descriptions using Mistral
        """
        context = {"theme": theme}
        prompt = f"Describe finding or examining a {item} in a {theme} setting"
        return self.generate_response(prompt, context)
    
    def generate_ascii_art(self, subject: str, theme: str, art_type: str = "banner") -> str:
        """
        Generate ASCII art using Mistral for immersive visual elements
        
        Args:
            subject: What to create ASCII art of (e.g., "castle", "spaceship", "demon")
            theme: Game theme (fantasy, sci-fi, horror, cyberpunk)
            art_type: Type of art ("banner", "object", "decoration", "border")
        """
        if not self.is_available():
            return self._fallback_ascii_art(subject, theme, art_type)
        
        try:
            # Theme-specific ASCII art styles
            style_guide = {
                "fantasy": "Use medieval symbols: ⚔️🏰🗡️⚡✨. Include borders with ═, ║, ╔, ╗, ╚, ╝",
                "sci-fi": "Use tech symbols: ▄▀█▌▐▓░. Include angular shapes and circuit patterns",
                "horror": "Use dark symbols: ☠️👻🕷️. Include jagged edges and ominous shapes",
                "cyberpunk": "Use neon symbols: ▲▼◆◇●○. Include glitch effects and digital patterns"
            }
            
            art_instructions = {
                "banner": "Create a decorative banner/header (3-5 lines max, 50 chars wide max)",
                "object": "Create a simple ASCII representation of the object (5-8 lines max)",
                "decoration": "Create a small decorative element (2-3 lines max)",
                "border": "Create a decorative border or frame (single line pattern)"
            }
            
            system_prompt = f"""You are an ASCII art generator for a {theme}-themed MUD game.

Style: {style_guide.get(theme, style_guide['fantasy'])}
Task: {art_instructions.get(art_type, art_instructions['banner'])}

CRITICAL RULES:
- Return ONLY the ASCII art, no explanations or text
- Use ONLY basic ASCII characters: | - = + / \\ _ ( ) [ ] {{ }} < >
- NO Unicode symbols, NO emojis, NO special characters
- Keep it simple and clean (3-5 lines max for objects)
- Make it recognizable but minimal
- No borders or boxes unless specifically requested"""

            prompt = f"Create ASCII art of: {subject}"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": f"{system_prompt}\n\n{prompt}\n\nASCII Art:",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 200,
                        "stop": ["\n\n\n", "Explanation:", "Note:"]
                    }
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                ascii_art = result.get("response", "").strip()
                
                # Clean up the response
                ascii_art = ascii_art.replace("ASCII Art:", "").strip()
                lines = ascii_art.split('\n')
                
                # Remove any explanatory text after the art
                cleaned_lines = []
                for line in lines:
                    if any(word in line.lower() for word in ['explanation', 'note:', 'this represents', 'created']):
                        break
                    cleaned_lines.append(line)
                
                if cleaned_lines:
                    return '\n'.join(cleaned_lines)
            
        except Exception as e:
            print(f"Error generating ASCII art: {e}")
        
        # Fallback to simple ASCII art
        return self._fallback_ascii_art(subject, theme, art_type)
    
    def _fallback_ascii_art(self, subject: str, theme: str, art_type: str) -> str:
        """
        Fallback ASCII art when LLM is unavailable
        """
        fallbacks = {
            "fantasy": {
                "banner": "╔══════════════════════════════════════╗\n║           ⚔️ ADVENTURE AWAITS ⚔️        ║\n╚══════════════════════════════════════╝",
                "border": "═══════════════════════════════════════════════════════",
                "decoration": "    ⚡✨⚡✨⚡✨⚡"
            },
            "sci-fi": {
                "banner": "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄\n█   🚀 SPACE EXPLORATION ACTIVE 🚀   █\n▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀",
                "border": "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
                "decoration": "    ▲ ▼ ◆ ◇ ● ○ ▲ ▼"
            },
            "horror": {
                "banner": "┌─────────────────────────────────────┐\n│         👻 DARKNESS AWAITS 👻         │\n└─────────────────────────────────────┘",
                "border": "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
                "decoration": "    ☠️ 🕷️ ☠️ 🕷️ ☠️"
            },
            "cyberpunk": {
                "banner": "╭─────────────────────────────────────╮\n│    🌐 NEURAL INTERFACE ACTIVE 🌐    │\n╰─────────────────────────────────────╯",
                "border": "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "decoration": "    ◢ ◣ ◤ ◥ ◢ ◣ ◤ ◥"
            }
        }
        
        theme_fallbacks = fallbacks.get(theme, fallbacks["fantasy"])
        return theme_fallbacks.get(art_type, theme_fallbacks["decoration"])