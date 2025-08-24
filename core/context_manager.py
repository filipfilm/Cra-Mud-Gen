"""
Context Management System for Cra-mud-gen
Maintains spatial consistency and manages LLM context with FIFO
"""
from typing import Dict, List, Any, Optional
from collections import deque
import time

class RoomContext:
    """Represents the context of a single room"""
    def __init__(self, room_id: str, description: str, items: List[str], npcs: List[str], theme: str):
        self.room_id = room_id
        self.description = description
        self.items = items.copy()
        self.npcs = npcs.copy()
        self.theme = theme
        self.timestamp = time.time()
        self.visit_count = 1
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'room_id': self.room_id,
            'description': self.description,
            'items': self.items,
            'npcs': self.npcs,
            'theme': self.theme,
            'visit_count': self.visit_count
        }

class MovementContext:
    """Represents a movement between rooms"""
    def __init__(self, from_room: str, to_room: str, direction: str, description: str):
        self.from_room = from_room
        self.to_room = to_room
        self.direction = direction
        self.description = description
        self.timestamp = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'from_room': self.from_room,
            'to_room': self.to_room,
            'direction': self.direction,
            'description': self.description
        }

class ContextManager:
    """
    Manages game context with FIFO system to maintain spatial consistency
    """
    
    def __init__(self, max_room_history: int = 10, max_movement_history: int = 15):
        self.max_room_history = max_room_history
        self.max_movement_history = max_movement_history
        
        # FIFO queues for context
        self.room_history = deque(maxlen=max_room_history)
        self.movement_history = deque(maxlen=max_movement_history)
        
        # Current state
        self.current_room_context = None
        self.room_contexts = {}  # room_id -> RoomContext
        
        # Spatial relationships
        self.room_connections = {}  # room_id -> {direction -> room_id}
        self.room_types = {}  # room_id -> room_type for consistency
        
    def add_room_context(self, room_id: str, description: str, items: List[str], 
                        npcs: List[str], theme: str, room_type: str = "chamber"):
        """Add or update room context"""
        
        if room_id in self.room_contexts:
            # Update existing room
            context = self.room_contexts[room_id]
            context.visit_count += 1
            context.items = items.copy()
            context.npcs = npcs.copy()
            context.timestamp = time.time()
        else:
            # Create new room context
            context = RoomContext(room_id, description, items, npcs, theme)
            self.room_contexts[room_id] = context
            self.room_types[room_id] = room_type
            
            # Add to FIFO history
            self.room_history.append(room_id)
        
        self.current_room_context = context
    
    def add_movement(self, from_room: str, to_room: str, direction: str, description: str):
        """Add movement context"""
        movement = MovementContext(from_room, to_room, direction, description)
        self.movement_history.append(movement)
        
        # Update spatial connections
        if from_room not in self.room_connections:
            self.room_connections[from_room] = {}
        self.room_connections[from_room][direction] = to_room
        
        # Add reverse connection
        reverse_dir = {
            'north': 'south', 'south': 'north',
            'east': 'west', 'west': 'east',
            'up': 'down', 'down': 'up'
        }
        
        if direction in reverse_dir:
            if to_room not in self.room_connections:
                self.room_connections[to_room] = {}
            self.room_connections[to_room][reverse_dir[direction]] = from_room
    
    def get_spatial_context(self, current_room: str) -> Dict[str, Any]:
        """Get spatial context for the current room"""
        context = {
            'current_room': current_room,
            'adjacent_rooms': {},
            'recent_rooms': [],
            'recent_movements': []
        }
        
        # Get adjacent rooms and their types
        if current_room in self.room_connections:
            for direction, room_id in self.room_connections[current_room].items():
                room_info = {
                    'room_id': room_id,
                    'room_type': self.room_types.get(room_id, 'unknown'),
                    'visited': room_id in self.room_contexts
                }
                
                if room_id in self.room_contexts:
                    room_context = self.room_contexts[room_id]
                    room_info['description_summary'] = room_context.description[:100] + "..." if len(room_context.description) > 100 else room_context.description
                
                context['adjacent_rooms'][direction] = room_info
        
        # Get recent room history (last 5)
        for room_id in list(self.room_history)[-5:]:
            if room_id in self.room_contexts:
                context['recent_rooms'].append(self.room_contexts[room_id].to_dict())
        
        # Get recent movements (last 3)
        for movement in list(self.movement_history)[-3:]:
            context['recent_movements'].append(movement.to_dict())
        
        return context
    
    def get_llm_context(self, current_room: str, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get optimized context for LLM with FIFO management"""
        
        base_context = {
            'theme': player_data.get('theme', 'fantasy'),
            'player_health': player_data.get('health', 100),
            'player_location': current_room,
            'inventory': player_data.get('inventory', []),
            'inventory_description': player_data.get('inventory_description', 'empty')
        }
        
        # Add current room context
        if self.current_room_context:
            base_context.update({
                'current_room_description': self.current_room_context.description,
                'current_room_items': self.current_room_context.items,
                'current_room_npcs': self.current_room_context.npcs,
                'room_visit_count': self.current_room_context.visit_count
            })
        
        # Add spatial awareness
        spatial_context = self.get_spatial_context(current_room)
        base_context['spatial_context'] = spatial_context
        
        return base_context
    
    def suggest_room_type(self, room_id: str, from_room: str = None, direction: str = None) -> str:
        """Suggest a room type based on spatial context"""
        
        # If we have a previous room, try to maintain consistency
        if from_room and from_room in self.room_types:
            from_type = self.room_types[from_room]
            
            # Simple spatial logic for consistency
            if from_type == "hallway":
                return "chamber"
            elif from_type == "chamber":
                if direction in ["up", "down"]:
                    return "stairwell"
                else:
                    return "hallway"
            elif from_type == "cavern":
                return "tunnel"
            elif from_type == "forest":
                return "clearing"
            else:
                return "chamber"
        
        # Default room types
        room_types = ["chamber", "hallway", "cavern", "library", "armory", "shrine"]
        return room_types[hash(room_id) % len(room_types)]
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current context state"""
        return {
            'rooms_in_context': len(self.room_contexts),
            'recent_room_history': len(self.room_history),
            'movement_history': len(self.movement_history),
            'spatial_connections': len(self.room_connections),
            'current_room': self.current_room_context.room_id if self.current_room_context else None
        }
    
    def cleanup_old_context(self):
        """Clean up old context that's no longer in FIFO queues"""
        
        # Keep only rooms that are in recent history or connected to recent rooms
        rooms_to_keep = set(self.room_history)
        
        # Also keep rooms connected to recent rooms
        for room_id in list(self.room_history):
            if room_id in self.room_connections:
                rooms_to_keep.update(self.room_connections[room_id].values())
        
        # Remove old room contexts
        rooms_to_remove = set(self.room_contexts.keys()) - rooms_to_keep
        for room_id in rooms_to_remove:
            if room_id in self.room_contexts:
                del self.room_contexts[room_id]
            if room_id in self.room_types:
                del self.room_types[room_id]
            if room_id in self.room_connections:
                del self.room_connections[room_id]