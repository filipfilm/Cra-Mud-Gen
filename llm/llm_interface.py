"""
LLM Interface for Cra-mud-gen - connects to local language models
"""
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Import the new Ollama implementation
try:
    from .ollama_llm import OllamaLLM
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

class LLMInterface(ABC):
    """
    Abstract base class for LLM interfaces
    """
    
    @abstractmethod
    def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a response from the LLM based on the prompt and context
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the LLM is available and ready to use
        """
        pass

class MockLLM(LLMInterface):
    """
    Mock LLM implementation for testing and demonstration purposes
    This simulates the behavior of a real LLM without requiring actual model loading
    """
    
    def __init__(self):
        self.is_model_loaded = True
        
    def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a mock response based on the prompt and context
        """
        # Simple response generation logic for demonstration
        if "look" in prompt.lower() or "describe" in prompt.lower():
            return "You see a mysterious place with ancient artifacts and glowing runes."
        elif "go" in prompt.lower() or "move" in prompt.lower():
            return "You move carefully through the dimly lit corridors."
        elif "inventory" in prompt.lower() or "items" in prompt.lower():
            return "You are carrying some items."
        elif "help" in prompt.lower():
            return "Available commands: look, go [direction], inventory, take [item], use [item], help, quit"
        else:
            # Default response for unknown commands
            return "The ancient magic responds to your presence."
    
    def is_available(self) -> bool:
        """
        Check if the mock LLM is available
        """
        return self.is_model_loaded

class QwenLLM(LLMInterface):
    """
    Qwen LLM interface - connects to Qwen models via local inference
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path
        self.is_model_loaded = False
        # For demonstration, we'll assume the model is available
        # In a real implementation, this would attempt to load the model
        self.is_model_loaded = True
        
    def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a response using Qwen model
        """
        # In a real implementation, this would:
        # 1. Load the Qwen model if not already loaded
        # 2. Process the prompt with context
        # 3. Generate and return a response
        
        # For demonstration, we'll return a mock response
        if context:
            # Use context to make the response more relevant
            theme = context.get("theme", "fantasy")
            room_description = context.get("room_description", "a mysterious place")
            
            if "look" in prompt.lower():
                return f"You examine the {room_description} more closely. The {theme} elements seem to glow with ancient power."
            elif "go" in prompt.lower():
                return f"You move through the {theme} environment, feeling the magic of this world around you."
            else:
                return f"The {theme} world responds to your presence with ancient wisdom."
        else:
            # Default response if no context provided
            return "The ancient magic responds to your presence."
    
    def is_available(self) -> bool:
        """
        Check if the Qwen model is available
        """
        return self.is_model_loaded

class LLMIntegrationLayer:
    """
    Integration layer that manages LLM connections and responses
    """
    
    def __init__(self, model_name: str = None):
        # Try to use Ollama with the specified model, fallback to mock
        if OLLAMA_AVAILABLE:
            try:
                if model_name:
                    ollama_llm = OllamaLLM(model_name=model_name)
                else:
                    ollama_llm = OllamaLLM()
                    
                if ollama_llm.is_available():
                    self.llm = ollama_llm
                    print("✓ Using Ollama for AI responses")
                else:
                    self.llm = MockLLM()
                    print("⚠ Ollama not available, using mock responses")
            except Exception:
                self.llm = MockLLM()
                print("⚠ Failed to initialize Ollama, using mock responses")
        else:
            self.llm = MockLLM()
            print("⚠ Ollama module not found, using mock responses")
        
        self.context_manager = {}
        
    def set_llm(self, llm_type: str = "auto", model_path: Optional[str] = None):
        """
        Set the LLM to use for responses
        """
        if llm_type.lower() == "ollama" and OLLAMA_AVAILABLE:
            try:
                ollama_llm = OllamaLLM()
                if ollama_llm.is_available():
                    self.llm = ollama_llm
                    print("✓ Switched to Ollama for AI responses")
                else:
                    print("✗ Ollama not available, keeping current LLM")
            except Exception as e:
                print(f"✗ Failed to initialize Ollama: {e}")
        elif llm_type.lower() == "qwen":
            self.llm = QwenLLM(model_path)
        elif llm_type.lower() == "mock":
            self.llm = MockLLM()
        elif llm_type.lower() == "auto":
            # Auto-detect best available LLM
            if OLLAMA_AVAILABLE:
                try:
                    ollama_llm = OllamaLLM()
                    if ollama_llm.is_available():
                        self.llm = ollama_llm
                        print("✓ Auto-selected Ollama for AI responses")
                        return
                except Exception:
                    pass
            # Fallback to mock
            self.llm = MockLLM()
            print("⚠ Auto-selected mock responses (no AI available)")
        else:
            # Default to mock for unknown types
            self.llm = MockLLM()
            
    def generate_game_response(self, user_command: str, game_context: Dict[str, Any]) -> str:
        """
        Generate a game response using the LLM with appropriate context
        """
        # Prepare the prompt for the LLM
        prompt = self._create_prompt(user_command, game_context)
        
        # Generate response using the LLM
        response = self.llm.generate_response(prompt, game_context)
        
        return response
        
    def _create_prompt(self, user_command: str, game_context: Dict[str, Any]) -> str:
        """
        Create a well-structured prompt for the LLM based on game context
        """
        # Extract relevant information from game context
        theme = game_context.get("theme", "fantasy")
        room_description = game_context.get("room_description", "a mysterious place")
        player_location = game_context.get("player_location", "start_room")
        player_health = game_context.get("player_health", 100)
        
        # Create a structured prompt
        prompt = f"""
        You are an AI assistant in a {theme}-themed adventure game. 
        The player is currently at location '{player_location}' in a {room_description}.
        The player has {player_health} health.
        
        User command: "{user_command}"
        
        Please respond in a way that fits the {theme} theme and provides appropriate game context.
        Keep responses concise but descriptive, and maintain the immersive experience.
        """
        
        return prompt
        
    def update_context(self, key: str, value: Any):
        """
        Update the context manager with new information
        """
        self.context_manager[key] = value
        
    def get_context(self) -> Dict[str, Any]:
        """
        Get the current context
        """
        return self.context_manager.copy()