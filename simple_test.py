#!/usr/bin/env python3
"""
Simple test to verify the MUD game core components work
"""
import sys
import os

def test_core_components():
    """Test basic functionality of core components"""
    try:
        from core.player import Player
        from core.world import World
        from core.room import Room
        from core.theme_manager import ThemeManager
        from core.command_processor import CommandProcessor
        
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
        
        # Test CommandProcessor
        processor = CommandProcessor()
        result = processor.parse("look", player, world)
        assert result["type"] == "look"
        print("✓ CommandProcessor component works")
        
        return True
    except Exception as e:
        print(f"✗ Core component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the simple test"""
    print("Running MUD game core component tests...")
    print("=" * 50)
    
    if test_core_components():
        print("=" * 50)
        print("✓ All core tests passed!")
        return 0
    else:
        print("=" * 50)
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())