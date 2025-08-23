"""
Save/Load System for Dun-Gen
Handles game state persistence with JSON serialization
"""
import json
import os
import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class SaveSystem:
    """Manages game state saving and loading"""
    
    def __init__(self, save_directory: str = "saves"):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(exist_ok=True)
        self.autosave_file = "autosave.json"
        self.quicksave_file = "quicksave.json"
    
    def save_game(self, player, world, story_engine=None, combat_system=None, 
                  conversation_system=None, save_name: str = None) -> bool:
        """Save complete game state to file"""
        try:
            # Generate save filename if not provided
            if save_name is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                save_name = f"game_save_{timestamp}.json"
            
            # Ensure .json extension
            if not save_name.endswith('.json'):
                save_name += '.json'
            
            save_path = self.save_directory / save_name
            
            # Build comprehensive save data
            save_data = {
                'metadata': {
                    'save_version': '1.0',
                    'timestamp': datetime.datetime.now().isoformat(),
                    'game_version': 'Dun-Gen v1.0',
                    'save_name': save_name
                },
                'player': self._serialize_player(player),
                'world': self._serialize_world(world),
                'story': self._serialize_story_engine(story_engine),
                'combat': self._serialize_combat_system(combat_system),
                'conversation': self._serialize_conversation_system(conversation_system)
            }
            
            # Write to file with pretty formatting
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"Game saved successfully to: {save_path}")
            return True
            
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False
    
    def load_game(self, save_name: str = None) -> Optional[Dict[str, Any]]:
        """Load game state from file"""
        try:
            if save_name is None:
                save_name = self.autosave_file
            
            # Ensure .json extension
            if not save_name.endswith('.json'):
                save_name += '.json'
            
            save_path = self.save_directory / save_name
            
            if not save_path.exists():
                print(f"Save file not found: {save_path}")
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Validate save data
            if not self._validate_save_data(save_data):
                print("Invalid save file format")
                return None
            
            print(f"Game loaded successfully from: {save_path}")
            return save_data
            
        except Exception as e:
            print(f"Failed to load game: {e}")
            return None
    
    def quick_save(self, player, world, story_engine=None, combat_system=None, 
                   conversation_system=None) -> bool:
        """Quick save to dedicated slot"""
        return self.save_game(player, world, story_engine, combat_system, 
                            conversation_system, self.quicksave_file)
    
    def quick_load(self) -> Optional[Dict[str, Any]]:
        """Quick load from dedicated slot"""
        return self.load_game(self.quicksave_file)
    
    def autosave(self, player, world, story_engine=None, combat_system=None, 
                 conversation_system=None) -> bool:
        """Automatic save (called periodically)"""
        return self.save_game(player, world, story_engine, combat_system, 
                            conversation_system, self.autosave_file)
    
    def list_saves(self) -> List[Dict[str, str]]:
        """List all available save files with metadata"""
        saves = []
        
        for save_file in self.save_directory.glob("*.json"):
            try:
                with open(save_file, 'r', encoding='utf-8') as f:
                    save_data = json.load(f)
                
                metadata = save_data.get('metadata', {})
                saves.append({
                    'filename': save_file.name,
                    'display_name': metadata.get('save_name', save_file.name),
                    'timestamp': metadata.get('timestamp', 'Unknown'),
                    'version': metadata.get('game_version', 'Unknown'),
                    'player_level': save_data.get('player', {}).get('stats', {}).get('level', 1),
                    'location': save_data.get('player', {}).get('location', 'Unknown')
                })
            except Exception as e:
                print(f"Error reading save file {save_file}: {e}")
        
        # Sort by timestamp (newest first)
        saves.sort(key=lambda x: x['timestamp'], reverse=True)
        return saves
    
    def delete_save(self, save_name: str) -> bool:
        """Delete a save file"""
        try:
            if not save_name.endswith('.json'):
                save_name += '.json'
            
            save_path = self.save_directory / save_name
            
            if save_path.exists():
                save_path.unlink()
                print(f"Save file deleted: {save_name}")
                return True
            else:
                print(f"Save file not found: {save_name}")
                return False
                
        except Exception as e:
            print(f"Failed to delete save: {e}")
            return False
    
    def _serialize_player(self, player) -> Dict[str, Any]:
        """Serialize player data"""
        return {
            'location': player.location,
            'current_room_id': player.current_room_id,
            'theme': player.theme,
            'inventory': player.inventory.copy(),
            'stats': player.stats.copy(),
            'combat_stats': getattr(player, 'combat_stats', {}),
            'health': getattr(player, 'current_health', getattr(player, 'max_health', 100)),
            'max_health': getattr(player, 'max_health', 100),
            'level': getattr(player, 'level', 1),
            'is_dead': getattr(player, 'is_dead', False)
        }
    
    def _serialize_world(self, world) -> Dict[str, Any]:
        """Serialize world data"""
        serialized_rooms = {}
        for room_id, room in world.rooms.items():
            serialized_rooms[room_id] = {
                'room_id': room.room_id,
                'description': room.description,
                'items': room.items.copy(),
                'npcs': room.npcs.copy(),
                'connections': room.connections.copy(),
                'visited': getattr(room, 'visited', False),
                'depth': getattr(room, 'depth', 0)
            }
        
        return {
            'theme': world.theme,
            'rooms': serialized_rooms,
            'room_counter': getattr(world, 'room_counter', 0),
            'generated_depth': getattr(world, 'generated_depth', 1)
        }
    
    def _serialize_story_engine(self, story_engine) -> Dict[str, Any]:
        """Serialize story engine data"""
        if not story_engine:
            return {}
        
        return {
            'story_threads': [
                {
                    'id': thread.id,
                    'title': thread.title,
                    'description': thread.description,
                    'theme': thread.theme,
                    'tone': thread.tone.value,
                    'complexity': thread.complexity,
                    'player_choices': thread.player_choices.copy(),
                    'consequences': thread.consequences.copy(),
                    'npcs_involved': thread.npcs_involved.copy(),
                    'locations_involved': thread.locations_involved.copy(),
                    'is_active': thread.is_active,
                    'completion_percentage': thread.completion_percentage
                }
                for thread in story_engine.story_threads
            ],
            'player_history': story_engine.player_history.copy(),
            'world_state': story_engine.world_state.copy(),
            'narrative_memory': story_engine.narrative_memory.copy()
        }
    
    def _serialize_combat_system(self, combat_system) -> Dict[str, Any]:
        """Serialize combat system data"""
        if not combat_system:
            return {}
        
        return {
            'experience_system': getattr(combat_system, 'experience_system', {}),
            'health_system': getattr(combat_system, 'health_system', {})
        }
    
    def _serialize_conversation_system(self, conversation_system) -> Dict[str, Any]:
        """Serialize conversation system data"""
        if not conversation_system:
            return {}
        
        return {
            'context': {
                'current_npc': conversation_system.context.current_npc,
                'conversation_history': conversation_system.context.conversation_history.copy(),
                'npc_memory': conversation_system.context.npc_memory.copy(),
                'last_topic': conversation_system.context.last_topic,
                'conversation_active': conversation_system.context.conversation_active
            }
        }
    
    def _validate_save_data(self, save_data: Dict[str, Any]) -> bool:
        """Validate save data structure"""
        required_keys = ['metadata', 'player', 'world']
        
        if not all(key in save_data for key in required_keys):
            return False
        
        # Validate player data
        player_data = save_data['player']
        required_player_keys = ['location', 'theme', 'inventory', 'stats']
        if not all(key in player_data for key in required_player_keys):
            return False
        
        # Validate world data
        world_data = save_data['world']
        required_world_keys = ['theme', 'rooms']
        if not all(key in world_data for key in required_world_keys):
            return False
        
        return True
    
    def get_save_info(self, save_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a save file without loading it"""
        try:
            if not save_name.endswith('.json'):
                save_name += '.json'
            
            save_path = self.save_directory / save_name
            
            if not save_path.exists():
                return None
            
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            metadata = save_data.get('metadata', {})
            player_data = save_data.get('player', {})
            
            return {
                'filename': save_name,
                'timestamp': metadata.get('timestamp', 'Unknown'),
                'game_version': metadata.get('game_version', 'Unknown'),
                'player_level': player_data.get('stats', {}).get('level', 1),
                'player_location': player_data.get('location', 'Unknown'),
                'player_theme': player_data.get('theme', 'Unknown'),
                'player_health': player_data.get('health', 100),
                'player_gold': player_data.get('stats', {}).get('gold', 0),
                'inventory_count': len(player_data.get('inventory', []))
            }
            
        except Exception as e:
            print(f"Error reading save info: {e}")
            return None