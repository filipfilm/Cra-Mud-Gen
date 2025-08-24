"""
Image generation bridge for Cra-mud-gen - connects to ComfyUI
"""
import requests
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path
import os

class ImageGenerationBridge:
    """
    Bridge to communicate with ComfyUI for text-to-image generation
    """
    
    def __init__(self, comfyui_url: str = "http://localhost:8188", cache_dir: str = "./image_cache"):
        self.comfyui_url = comfyui_url
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def generate_image(self, prompt: str, game_element: str = "room") -> Optional[str]:
        """
        Generate an image from a text prompt using ComfyUI
        """
        # Check if we have a cached version
        cache_key = self._generate_cache_key(prompt, game_element)
        cached_image_path = self.cache_dir / f"{cache_key}.png"
        
        if cached_image_path.exists():
            print(f"Using cached image for '{prompt}'")
            return str(cached_image_path)
        
        try:
            # In a real implementation, this would:
            # 1. Send the prompt to ComfyUI
            # 2. Wait for image generation
            # 3. Save the image to cache
            # 4. Return the path to the generated image
            
            # For demonstration, we'll simulate image generation
            print(f"Generating image for: '{prompt}'")
            
            # Simulate processing time
            time.sleep(1)
            
            # Create a placeholder image path (in real implementation, this would be the actual generated image)
            image_path = str(cached_image_path)
            
            # For demonstration, we'll create a simple placeholder file
            # In a real implementation, this would be the actual generated image from ComfyUI
            with open(image_path, 'w') as f:
                f.write(f"Placeholder image for: {prompt}")
            
            print(f"Image generated and cached at: {image_path}")
            return image_path
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    def _generate_cache_key(self, prompt: str, game_element: str) -> str:
        """
        Generate a cache key from the prompt and game element
        """
        # Simple hash-like approach for demonstration
        import hashlib
        key_string = f"{prompt}_{game_element}"
        return hashlib.md5(key_string.encode()).hexdigest()[:10]
    
    def is_comfyui_available(self) -> bool:
        """
        Check if ComfyUI is available and responding
        """
        try:
            response = requests.get(f"{self.comfyui_url}/prompt", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """
        Get information about available workflows in ComfyUI
        """
        try:
            response = requests.get(f"{self.comfyui_url}/workflow", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {"error": "Could not connect to ComfyUI"}
    
    def generate_room_image(self, room_description: str, theme: str) -> Optional[str]:
        """
        Generate an image specifically for a room description
        """
        # Create a more descriptive prompt based on room and theme
        prompt = f"{theme} themed room: {room_description}"
        
        # In a real implementation, you would:
        # 1. Format the prompt properly for ComfyUI
        # 2. Use appropriate workflow nodes
        # 3. Handle image generation and caching
        
        return self.generate_image(prompt, "room")
    
    def generate_npc_image(self, npc_description: str, theme: str) -> Optional[str]:
        """
        Generate an image for an NPC
        """
        prompt = f"{theme} themed NPC: {npc_description}"
        return self.generate_image(prompt, "npc")
    
    def generate_item_image(self, item_description: str, theme: str) -> Optional[str]:
        """
        Generate an image for a game item
        """
        prompt = f"{theme} themed item: {item_description}"
        return self.generate_image(prompt, "item")

class MockImageBridge:
    """
    Mock image bridge for testing when ComfyUI is not available
    """
    
    def __init__(self):
        self.cache_dir = Path("./mock_image_cache")
        self.cache_dir.mkdir(exist_ok=True)
    
    def generate_image(self, prompt: str, game_element: str = "room") -> Optional[str]:
        """
        Generate a mock image for testing
        """
        # For demonstration, we'll just return a placeholder path
        cache_key = self._generate_cache_key(prompt, game_element)
        image_path = self.cache_dir / f"{cache_key}.png"
        
        # Create a placeholder file
        with open(image_path, 'w') as f:
            f.write(f"Mock image for: {prompt}")
            
        return str(image_path)
    
    def _generate_cache_key(self, prompt: str, game_element: str) -> str:
        """
        Generate a cache key from the prompt and game element
        """
        import hashlib
        key_string = f"{prompt}_{game_element}"
        return hashlib.md5(key_string.encode()).hexdigest()[:10]
    
    def is_comfyui_available(self) -> bool:
        """
        Mock implementation - always returns True for testing
        """
        return True
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """
        Mock workflow info
        """
        return {"mock": "workflow_info"}

# Factory function to create the appropriate image bridge
def create_image_bridge(use_mock: bool = False, comfyui_url: str = "http://localhost:8188") -> ImageGenerationBridge:
    """
    Create an image bridge instance
    """
    if use_mock:
        return MockImageBridge()
    else:
        return ImageGenerationBridge(comfyui_url)