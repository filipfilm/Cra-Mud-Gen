#!/usr/bin/env python3
"""
Main entry point for Cra-mud-gen
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    Main function to start Cra-mud-gen
    """
    try:
        # Import here to handle potential import errors gracefully
        from core.mud_engine import GameEngine
        from ui.seed_ui import SeedUI
        
        print("Starting Cra-mud-gen...")
        
        # Initialize seed generation UI
        seed_ui = SeedUI()
        
        # Run seed generation flow
        print("Initializing story seed generation...")
        story_seed = seed_ui.run_seed_generation_flow()
        
        if story_seed is None:
            print("Story seed generation cancelled. Exiting...")
            return
        
        # Create and run the game engine with the story seed
        engine = GameEngine(story_seed=story_seed)
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