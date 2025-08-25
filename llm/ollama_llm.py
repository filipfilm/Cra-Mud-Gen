"""
Ollama LLM integration for Cra-mud-gen - using Mistral-Small
"""
import requests
import json
from typing import Dict, Any, Optional, List

class OllamaLLM:
    """
    Ollama LLM interface - connects to Mistral-Small model
    """
    
    def __init__(self, model_name: str = "mistral-small:22b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.is_model_loaded = self._check_model_availability()
        
        # Warm up the model on initialization
        if self.is_model_loaded:
            self._warmup_model()
        
    def _check_model_availability(self) -> bool:
        """
        Check if Ollama is running and the selected model is available
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                # Check for the specific model
                if self.model_name in model_names:
                    print(f"✓ {self.model_name} model is ready for adventure!")
                    return True
                elif models:
                    print(f"✗ {self.model_name} not found. Available models: {', '.join(model_names[:3])}")
                    return False
                else:
                    print(f"✗ No models found. Please install a model with: ollama pull <model-name>")
                    return False
        except:
            print("✗ Ollama not running. Start with: ollama serve")
            return False
    
    def _warmup_model(self) -> None:
        """
        Warm up the model with a simple hello world test to reduce first-generation latency
        """
        print("🔥 Warming up the AI model...")
        try:
            # Simple warmup query
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": "Hello",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 10  # Very short response
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Model warmed up and ready!")
            else:
                print("⚠️  Warmup completed with minor issues")
                
        except Exception:
            print("⚠️  Warmup skipped (model will load on first use)")
    
    @staticmethod
    def get_available_models(base_url: str = "http://localhost:11434") -> List[Dict]:
        """
        Get all available Ollama models with their details
        """
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                
                # Format model info for display
                formatted_models = []
                for model in models:
                    name = model.get("name", "Unknown")
                    size = model.get("size", 0)
                    modified = model.get("modified_at", "Unknown")
                    
                    # Convert size to human readable
                    if size > 1e9:
                        size_str = f"{size / 1e9:.1f}GB"
                    elif size > 1e6:
                        size_str = f"{size / 1e6:.1f}MB"
                    else:
                        size_str = f"{size}B"
                    
                    # Parse model family for better descriptions
                    model_family = name.split(':')[0].lower() if ':' in name else name.lower()
                    descriptions = {
                        "mistral": "Excellent for creative writing and storytelling",
                        "llama": "Great general purpose model, good balance",  
                        "codellama": "Optimized for code, may be verbose for stories",
                        "gemma": "Google's model, good for factual content",
                        "qwen": "Strong multilingual support and reasoning",
                        "phi": "Microsoft's efficient small model",
                        "tinyllama": "Very fast, basic responses",
                        "neural-chat": "Optimized for conversation",
                        "openhermes": "Fine-tuned for helpful responses",
                        "wizardcoder": "Code-focused, may be technical for adventure games",
                        "deepseek": "Good reasoning capabilities",
                        "starling": "Balanced performance model"
                    }
                    
                    description = descriptions.get(model_family, "General purpose language model")
                    
                    formatted_models.append({
                        "name": name,
                        "size": size_str,
                        "modified": modified,
                        "family": model_family,
                        "description": description,
                        "recommended": model_family in ["mistral", "llama", "neural-chat", "openhermes"]
                    })
                
                return sorted(formatted_models, key=lambda x: (not x["recommended"], x["name"]))
            else:
                return []
        except:
            return []
    
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
            system_message = f"""You are an immersive narrator for a {theme}-themed text adventure game.
            
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
                    "options": self._get_model_options()
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
    
    def generate_game_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Alias for generate_response to maintain compatibility with game engine
        """
        return self.generate_response(prompt, context)
    
    def generate_long_content(self, prompt: str, context: Dict[str, Any] = None, max_tokens: int = 800) -> str:
        """
        Generate longer content like story progression with extended token limits
        """
        if not self.is_available():
            return "The ancient magic remains silent..."
        
        try:
            theme = context.get("theme", "fantasy") if context else "fantasy"
            
            # Minimal system message for better content generation
            system_message = f"You are a creative writer for {theme} adventures. Generate clear, actionable content as requested."
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": f"{system_message}\n\n{prompt}",
                    "stream": False,
                    "options": {
                        "temperature": 0.75,
                        "top_p": 0.9,
                        "top_k": 40,
                        "num_predict": max_tokens,
                        "stop": []  # No early stopping for long content
                    }
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                
                if generated_text:
                    return generated_text
                else:
                    return "The creative energies remain dormant..."
            else:
                return "The storytelling magic flickers..."
                
        except requests.exceptions.Timeout:
            return "The narrative threads take time to weave..."
        except Exception as e:
            print(f"Error with long content generation: {e}")
            return "The storytelling forces waver..."
    
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
            
            system_prompt = f"""You are an ASCII art generator for a {theme}-themed adventure game.

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
                    "options": self._get_model_options(art_mode=True)
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
    
    def _get_model_options(self, art_mode: bool = False) -> Dict[str, Any]:
        """
        Get optimized options based on the model type
        """
        model_family = self.model_name.split(':')[0].lower() if ':' in self.model_name else self.model_name.lower()
        
        # Base options for different model families
        model_configs = {
            "mistral": {
                "temperature": 0.85,
                "top_p": 0.92,
                "top_k": 40,
                "num_predict": 300 if not art_mode else 100,
                "stop": ["\n\n", "Request:", "Response:"] if not art_mode else ["\n\n\n", "Explanation:", "Note:"]
            },
            "llama": {
                "temperature": 0.8,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 280 if not art_mode else 80,
                "stop": ["\n\n", "Human:", "Assistant:"] if not art_mode else ["\n\n\n", "Explanation:"]
            },
            "gemma": {
                "temperature": 0.75,
                "top_p": 0.9,
                "top_k": 30,
                "num_predict": 200 if not art_mode else 60,
                "stop": ["\n\n", "User:", "Model:"] if not art_mode else ["\n\n\n"]
            },
            "phi": {
                "temperature": 0.8,
                "top_p": 0.85,
                "top_k": 35,
                "num_predict": 180 if not art_mode else 50,
                "stop": ["\n\n"] if not art_mode else ["\n\n\n"]
            },
            "qwen": {
                "temperature": 0.8,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 250 if not art_mode else 80,
                "stop": ["\n\n", "Human:", "Assistant:"] if not art_mode else ["\n\n\n", "Explanation:"]
            },
            "neural-chat": {
                "temperature": 0.85,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": 260 if not art_mode else 90,
                "stop": ["\n\n", "User:", "Assistant:"] if not art_mode else ["\n\n\n", "Note:"]
            },
            "tinyllama": {
                "temperature": 0.9,
                "top_p": 0.95,
                "top_k": 50,
                "num_predict": 150 if not art_mode else 40,
                "stop": ["\n\n"] if not art_mode else ["\n\n\n"]
            }
        }
        
        # Get config for this model family, fallback to mistral config
        config = model_configs.get(model_family, model_configs["mistral"])
        
        # Art mode adjustments
        if art_mode:
            config = config.copy()
            config["temperature"] = max(0.3, config["temperature"] - 0.2)  # Lower temp for ASCII art
        
        return config