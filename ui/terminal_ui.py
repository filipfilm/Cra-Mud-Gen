"""
Terminal-based user interface for the MUD game
"""
import os
import sys
from typing import Dict, Any

class TerminalUI:
    """
    Text-based user interface for the MUD game
    """
    
    def __init__(self):
        self.clear_command = "clear" if os.name != "nt" else "cls"
        
    def get_input(self) -> str:
        """
        Get input from the user
        """
        try:
            return input("\n> ")
        except EOFError:
            return "quit"
        except KeyboardInterrupt:
            print("\nGame interrupted. Type 'quit' to exit.")
            return "quit"
            
    def display_welcome(self):
        """
        Display welcome message
        """
        self.clear_screen()
        print("=" * 60)
        print("           Welcome to Procedural MUD")
        print("=" * 60)
        print("An offline text-based adventure game with AI-powered responses")
        print("and procedural generation.")
        print()
        
    def get_theme_selection(self) -> str:
        """
        Get theme selection from the user
        """
        print("Choose a game theme:")
        print("1. Fantasy")
        print("2. Sci-Fi") 
        print("3. Horror")
        print("4. Cyberpunk")
        
        while True:
            try:
                choice = input("Enter your choice (1-4): ").strip()
                if choice == "1":
                    return "fantasy"
                elif choice == "2":
                    return "sci-fi"
                elif choice == "3":
                    return "horror"
                elif choice == "4":
                    return "cyberpunk"
                else:
                    print("Invalid choice. Please enter 1, 2, 3, or 4.")
            except (EOFError, KeyboardInterrupt):
                print("\nGame interrupted. Exiting...")
                sys.exit(0)
                
    def display_room(self, room, player):
        """
        Display the current room description
        """
        print("\n" + "=" * 60)
        print(f"Location: {room.room_id}")
        print("=" * 60)
        print(room.get_description())
        
        # Show items if any
        items = room.get_items()
        if items:
            print("\nItems in this room:")
            for item in items:
                print(f"  - {item}")
                
        # Show NPCs if any
        npcs = room.get_npcs()
        if npcs:
            print("\nNPCs here:")
            for npc in npcs:
                print(f"  - {npc}")
                
        # Show exits
        exits = room.get_exits()
        if exits:
            print("\nExits:")
            for exit in exits:
                print(f"  - {exit}")
                
        # Show player status
        print(f"\n{player.get_status()}")
        
    def display_error(self, message: str):
        """
        Display an error message
        """
        print(f"\nError: {message}")
        
    def display_goodbye(self):
        """
        Display goodbye message
        """
        print("\nThank you for playing Procedural MUD!")
        print("Come back soon for another adventure!")
        
    def clear_screen(self):
        """
        Clear the terminal screen
        """
        os.system(self.clear_command)
        
    def display_message(self, message: str):
        """
        Display a simple message
        """
        print(message)
        
    def display_help(self, help_text: str):
        """
        Display help text
        """
        print(help_text)