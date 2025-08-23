#!/usr/bin/env python3
"""
Simple test to verify Dun-Gen components work together
"""
import sys
import os

# Add dun_gen to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from core.mud_engine import GameEngine
        from core.player import Player
        from core.world import World
        from core.room import Room
        from core.command_processor import CommandProcessor
        from ui.terminal_ui import TerminalUI
        from core.theme_manager import ThemeManager
        from llm.llm_interface import LLMIntegrationLayer, MockLLM
        from image_generation.image_bridge import ImageGenerationBridge, MockImageBridge
        
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import modules: {e}")
        return False

def test_core_components():
    """Test basic functionality of core components"""
    try:
        from core.player import Player
        from core.world import World
        from core.room import Room
        from core.theme_manager import ThemeManager
        
        # Test Player
        player = Player()
        assert player.location == "start_room"
        assert player.theme == "fantasy"
        print("✓ Player component works")
        
        # Test World
        world = World()
        assert world.theme == "fantasy"
        print("✓ World component works")
        
        # Test Room
        room = Room(
            room_id="test_room",
            description="A test room",
            items=["sword", "shield"],
            npcs=["orc", "goblin"],
            connections=["start_room"]
        )
        assert room.room_id == "test_room"
        assert "sword" in room.get_items()
        print("✓ Room component works")
        
        # Test ThemeManager
        theme_manager = ThemeManager()
        themes = theme_manager.get_theme_names()
        assert "fantasy" in themes
        assert "sci-fi" in themes
        print("✓ ThemeManager component works")
        
        return True
    except Exception as e:
        print(f"✗ Core component test failed: {e}")
        return False

def test_command_processing():
    """Test basic command processing"""
    try:
        from core.command_processor import CommandProcessor
        from core.player import Player
        from core.world import World
        
        processor = CommandProcessor()
        player = Player()
        world = World()
        
        # Test parsing a simple command
        result = processor.parse("look", player, world)
        assert result["type"] == "look"
        print("✓ Command processor works")
        
        # Test parsing a quit command
        result = processor.parse("quit", player, world)
        assert result["type"] == "exit"
        print("✓ Command processor handles quit")
        
        return True
    except Exception as e:
        print(f"✗ Command processing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running Dun-Gen component tests...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_core_components,
        test_command_processing
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())