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
    Let user select which Ollama model to use
    """
    try:
        # Import here to handle potential import errors gracefully
        from llm.ollama_llm import OllamaLLM
        from ui.terminal_ui import TerminalUI
        
        ui = TerminalUI()
        available_models = OllamaLLM.get_available_models()
        if available_models:
            return ui.get_model_selection(available_models)
        else:
            print("\n❌ No Ollama models found!")
            print("Please install a model first. Popular options:")
            print("  • ollama pull mistral           (7B - Good for storytelling)")
            print("  • ollama pull llama3.1          (8B - Great general purpose)")
            print("  • ollama pull gemma2:2b         (2B - Fast and lightweight)")
            print("\nAfter installing a model, restart the game.")
            sys.exit(0)
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        print("Make sure Ollama is running: ollama serve")
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
        
        # Step 1: Select LLM model first
        print("Selecting LLM model...")
        selected_model = _select_model()
        llm_interface = LLMIntegrationLayer(model_name=selected_model)
        
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