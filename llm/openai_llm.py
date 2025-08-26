"""
OpenAI API integration for Cra-mud-gen - using GPT models via API
"""
import requests
import json
import os
from typing import Dict, Any, Optional, List

class OpenAILLM:
    """
    OpenAI LLM interface - connects to GPT models via OpenAI API
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1"
        self.is_model_loaded = self._check_api_availability()
        
        # Available models with descriptions
        self.available_models = {
            "gpt-3.5-turbo": "Fast, cost-effective model - great for gameplay",
            "gpt-4": "Most capable model - excellent for rich narratives", 
            "gpt-4-turbo": "Latest GPT-4 with improved performance",
            "gpt-4o": "Optimized GPT-4 for better efficiency",
            "gpt-4o-mini": "Smaller, faster GPT-4 variant"
        }
        
    def _check_api_availability(self) -> bool:
        """
        Check if OpenAI API is available and API key is valid
        """
        if not self.api_key:
            print("✗ OpenAI API key not found. Set OPENAI_API_KEY environment variable or provide during selection.")
            return False
            
        try:
            # Test API connection with a simple request
            response = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✓ OpenAI API connection successful!")
                return True
            elif response.status_code == 401:
                print("✗ Invalid OpenAI API key")
                return False
            else:
                print(f"✗ OpenAI API error: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Failed to connect to OpenAI API: {e}")
            return False
    
    def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a response using OpenAI GPT models
        """
        if not self.is_available():
            return "The digital oracle remains silent..."
        
        try:
            theme = context.get("theme", "fantasy") if context else "fantasy"
            
            # Create system message for game context
            system_message = f"""You are an immersive narrator for a {theme}-themed text adventure game.

Style Guidelines:
- Write in second person ("You see...", "You feel...")
- Keep responses to 2-3 sentences maximum
- Be atmospheric and descriptive
- Match the {theme} theme perfectly
- Focus on sensory details (sight, sound, smell, touch)
- Never break character or mention game mechanics"""

            # Build messages for ChatGPT format
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            # Add room context if available
            if context and "room_description" in context:
                messages.append({
                    "role": "system", 
                    "content": f"Current setting: {context['room_description']}"
                })
            
            # Make API call
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "max_tokens": 300,
                    "temperature": 0.8,
                    "top_p": 0.9
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    generated_text = result["choices"][0]["message"]["content"].strip()
                    return generated_text
                else:
                    return "The digital consciousness stirs mysteriously..."
            else:
                error_msg = response.json().get("error", {}).get("message", "Unknown error")
                print(f"OpenAI API error: {error_msg}")
                return "The digital oracle encounters interference..."
                
        except requests.exceptions.Timeout:
            return "The digital oracle takes time to process..."
        except Exception as e:
            print(f"Error with OpenAI generation: {e}")
            return "The digital energies fluctuate unexpectedly..."
    
    def is_available(self) -> bool:
        """
        Check if OpenAI model is available
        """
        return self.is_model_loaded and bool(self.api_key)
    
    def generate_room_description(self, base_description: str, theme: str) -> str:
        """
        Special method for enhanced room descriptions using OpenAI
        """
        context = {"theme": theme, "room_description": base_description}
        prompt = f"Enhance this {theme} room with vivid sensory details: {base_description}"
        return self.generate_response(prompt, context)
    
    def generate_movement_text(self, direction: str, theme: str) -> str:
        """
        Generate movement descriptions using OpenAI
        """
        context = {"theme": theme}
        prompt = f"Describe the player moving {direction} through a {theme} environment"
        return self.generate_response(prompt, context)
    
    def generate_item_description(self, item: str, theme: str) -> str:
        """
        Generate item descriptions using OpenAI
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
            return "The digital oracle remains silent..."
        
        try:
            theme = context.get("theme", "fantasy") if context else "fantasy"
            
            system_message = f"You are a creative writer for {theme} adventures. Generate clear, actionable content as requested."
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.75,
                    "top_p": 0.9
                },
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    generated_text = result["choices"][0]["message"]["content"].strip()
                    return generated_text
                else:
                    return "The creative digital energies remain dormant..."
            else:
                return "The storytelling magic encounters digital interference..."
                
        except requests.exceptions.Timeout:
            return "The narrative threads take time to weave through the digital realm..."
        except Exception as e:
            print(f"Error with long content generation: {e}")
            return "The storytelling forces encounter unexpected digital turbulence..."
    
    @staticmethod
    def get_available_models() -> List[Dict]:
        """
        Get available OpenAI models with their details
        """
        models = [
            {
                "name": "gpt-3.5-turbo",
                "description": "Fast, cost-effective model - great for gameplay",
                "family": "gpt-3.5",
                "recommended": True,
                "cost": "Low"
            },
            {
                "name": "gpt-4o-mini", 
                "description": "Smaller, faster GPT-4 variant - good balance",
                "family": "gpt-4",
                "recommended": True,
                "cost": "Medium"
            },
            {
                "name": "gpt-4o",
                "description": "Optimized GPT-4 for better efficiency",
                "family": "gpt-4", 
                "recommended": False,
                "cost": "High"
            },
            {
                "name": "gpt-4-turbo",
                "description": "Latest GPT-4 with improved performance",
                "family": "gpt-4",
                "recommended": False,
                "cost": "High"
            },
            {
                "name": "gpt-4",
                "description": "Most capable model - excellent for rich narratives",
                "family": "gpt-4",
                "recommended": False,
                "cost": "Very High"
            }
        ]
        
        return models
    
    def set_api_key(self, api_key: str):
        """
        Set or update the API key
        """
        self.api_key = api_key
        self.is_model_loaded = self._check_api_availability()