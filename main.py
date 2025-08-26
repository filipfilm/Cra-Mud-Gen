#!/usr/bin/env python3
"""
Main entry point for Cra-mud-gen
"""
import sys
import os
import argparse

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def _select_model():
    """
    Let user select which AI model to use (Ollama or OpenAI)
    """
    try:
        from ui.terminal_ui import TerminalUI
        
        ui = TerminalUI()
        return ui.get_ai_model_selection()
    except Exception as e:
        print(f"❌ Error during model selection: {e}")
        sys.exit(0)

def main():
    """
    Main function to start Cra-mud-gen
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Cra-mud-gen: AI-powered MUD game')
    parser.add_argument('--fallback-mode', action='store_true', default=False,
                        help='Enable fallback mode when LLM fails (default: False - strict LLM mode)')
    args = parser.parse_args()
    
    try:
        # Import here to handle potential import errors gracefully
        from core.mud_engine import GameEngine
        from ui.seed_ui import SeedUI
        from llm.llm_interface import LLMIntegrationLayer
        
        print("Starting Cra-mud-gen...")
        
        # Step 1: Select AI model first
        print("Selecting AI model...")
        model_info = _select_model()
        
        # Extract model info and create LLM interface
        if isinstance(model_info, dict):
            model_name = model_info.get("name")
            llm_type = model_info.get("type", "auto")
            api_key = model_info.get("api_key")
            llm_interface = LLMIntegrationLayer(model_name=model_name, llm_type=llm_type, api_key=api_key)
        else:
            # Backward compatibility - assume it's just a model name
            llm_interface = LLMIntegrationLayer(model_name=model_info)
        
        # Step 2: Initialize seed generation UI with LLM
        seed_ui = SeedUI(llm_interface=llm_interface, fallback_mode=args.fallback_mode)
        
        # Step 3: Run seed generation flow (now with 3-iteration LLM support)
        print("Initializing story seed generation with LLM...")
        story_seed = seed_ui.run_seed_generation_flow()
        
        if story_seed is None:
            print("Story seed generation cancelled. Exiting...")
            return
        
        # Step 4: Create and run the game engine with the story seed and LLM
        engine = GameEngine(story_seed=story_seed, llm_interface=llm_interface, fallback_mode=args.fallback_mode)
        engine.run()
        
    except ImportError as e:
        print(f"Failed to import game modules: {e}")
        print("Please ensure all required files are in the correct location.")
        print("\nDebug info:")
        print(f"Current directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        print(f"Directory contents: {os.listdir('.')}")
        if os.path.exists('dun_gen'):
            print(f"dun_gen contents: {os.listdir('dun_gen')}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while running the game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()