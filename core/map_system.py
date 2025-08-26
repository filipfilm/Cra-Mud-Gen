"""
ASCII Map System for Cra-mud-gen
Tracks player movement and generates text-based maps
"""
from typing import Dict, List, Tuple, Set, Optional
import re

class Room:
    """Represents a room in the map system"""
    def __init__(self, room_id: str, x: int, y: int):
        self.room_id = room_id
        self.x = x
        self.y = y
        self.visited = False
        self.connections = {}  # direction -> connected_room_id
        self.room_type = "room"  # room, corridor, special, etc.

class MapSystem:
    """
    Handles ASCII map generation and room tracking for Cra-mud-gen
    """
    
    def __init__(self):
        self.rooms = {}  # room_id -> Room
        self.player_location = None
        self.visited_rooms = set()
        self.room_coordinates = {}  # room_id -> (x, y)
        
        # Map symbols
        self.symbols = {
            'player': '@',           # Current player location
            'visited_room': '■',     # Visited room
            'current_room': '●',     # Current room (alternative to player)
            'unvisited_room': '?',   # Known but unvisited room
            'corridor_h': '─',       # Horizontal corridor
            'corridor_v': '│',       # Vertical corridor
            'junction': '┼',         # Junction/intersection
            'corner_ul': '┌',        # Upper left corner
            'corner_ur': '┐',        # Upper right corner
            'corner_ll': '└',        # Lower left corner
            'corner_lr': '┘',        # Lower right corner
            'wall': '█',             # Wall/blocked area
            'empty': ' ',            # Empty space
            'start_room': 'S',       # Starting room
            'special_room': '*'      # Special/important rooms
        }
        
        # Initialize starting position
        self._initialize_starting_area()
    
    def _initialize_starting_area(self):
        """Initialize the starting room and basic layout"""
        # Start room at center (0, 0) - use correct room ID
        self.add_room("start_room", 0, 0)
        self.mark_visited("start_room")
        self.player_location = "start_room"
    
    def add_room(self, room_id: str, x: int, y: int):
        """Add a room to the map system"""
        if room_id not in self.rooms:
            room = Room(room_id, x, y)
            self.rooms[room_id] = room
            self.room_coordinates[room_id] = (x, y)
    
    def add_connection(self, from_room: str, direction: str, to_room: str):
        """Add a connection between rooms"""
        if from_room in self.rooms:
            self.rooms[from_room].connections[direction] = to_room
        
        # Add reverse connection
        reverse_dir = {
            'north': 'south', 'south': 'north',
            'east': 'west', 'west': 'east',
            'up': 'down', 'down': 'up'
        }
        
        if direction in reverse_dir and to_room in self.rooms:
            self.rooms[to_room].connections[reverse_dir[direction]] = from_room
    
    def mark_visited(self, room_id: str):
        """Mark a room as visited"""
        if room_id in self.rooms:
            self.rooms[room_id].visited = True
            self.visited_rooms.add(room_id)
    
    def move_player(self, new_room_id: str):
        """Update player location"""
        old_location = self.player_location
        self.player_location = new_room_id
        self.mark_visited(new_room_id)
        
        # Add room to map if it doesn't exist
        if new_room_id not in self.rooms:
            # Calculate position based on movement from previous room
            new_x, new_y = self._calculate_room_position(new_room_id, old_location)
            self.add_room(new_room_id, new_x, new_y)
    
    def set_player_location(self, room_id: str):
        """Set player location without movement tracking (for loading saves)"""
        self.player_location = room_id
        if room_id not in self.rooms:
            # Add room at origin if we don't know where it should be
            self.add_room(room_id, 0, 0)
        self.mark_visited(room_id)
    
    def _calculate_room_position(self, new_room_id: str, old_room_id: str) -> Tuple[int, int]:
        """Calculate room position based on movement direction"""
        if old_room_id not in self.room_coordinates:
            return (0, 0)
        
        old_x, old_y = self.room_coordinates[old_room_id]
        direction = None
        
        # Parse direction from room ID - handle multiple formats
        if "_" in new_room_id:
            # Format like "north_2" or "n1_s2" -> use first part
            direction = new_room_id.split("_")[0]
        else:
            # Handle compact format like "w1", "e2", "n1s2", etc.
            direction = self._extract_primary_direction(new_room_id)
        
        if not direction:
            return (old_x, old_y)  # Fallback to same position
        
        # Calculate new position based on direction
        direction_offsets = {
            "north": (0, -1), "n": (0, -1),
            "south": (0, 1), "s": (0, 1), 
            "east": (1, 0), "e": (1, 0),
            "west": (-1, 0), "w": (-1, 0),
            "up": (0, 0), "u": (0, 0),    # Same horizontal position
            "down": (0, 0), "d": (0, 0)   # Same horizontal position
        }
        
        dx, dy = direction_offsets.get(direction, (0, 0))
        return (old_x + dx, old_y + dy)
    
    def _extract_primary_direction(self, room_id: str) -> Optional[str]:
        """Extract the primary direction from compact room IDs like 'w1', 'e2', 'n1s2'"""
        import re
        
        # Look for direction letters at the start
        match = re.match(r'^([nsewud])', room_id.lower())
        if match:
            return match.group(1)
        
        # Handle multi-directional IDs by taking the first direction found
        directions_found = re.findall(r'([nsewud])\d*', room_id.lower())
        if directions_found:
            return directions_found[0]
        
        return None
    
    def discover_room_exits(self, room_id: str, connections: List[str]):
        """Discover potential exits from a room using connection strings"""
        if room_id not in self.rooms:
            return
            
        room_x, room_y = self.room_coordinates[room_id]
        
        for connection in connections:
            # Parse connection format: "direction_destination"
            if "_" in connection:
                direction, destination = connection.split("_", 1)
                
                # Calculate position for the destination room
                direction_offsets = {
                    "north": (0, -1),
                    "south": (0, 1), 
                    "east": (1, 0),
                    "west": (-1, 0),
                    "up": (0, 0),    # Same position for vertical movement
                    "down": (0, 0)   # Same position for vertical movement  
                }
                
                if destination not in self.rooms:
                    dx, dy = direction_offsets.get(direction, (0, 0))
                    self.add_room(destination, room_x + dx, room_y + dy)
                
                # Add bidirectional connection
                self.add_connection(room_id, direction, destination)
    
    def generate_ascii_map(self, width: int = 21, height: int = 15) -> str:
        """Generate ASCII map of explored areas"""
        # Create empty map grid
        map_grid = [[self.symbols['empty'] for _ in range(width)] for _ in range(height)]
        
        # Calculate map center
        center_x, center_y = width // 2, height // 2
        
        # Get player position for relative positioning
        if self.player_location and self.player_location in self.room_coordinates:
            player_x, player_y = self.room_coordinates[self.player_location]
        else:
            player_x, player_y = 0, 0
        
        # Place rooms on map
        for room_id, (room_x, room_y) in self.room_coordinates.items():
            # Calculate position relative to player
            map_x = center_x + (room_x - player_x)
            map_y = center_y + (room_y - player_y)
            
            # Check if position is within map bounds
            if 0 <= map_x < width and 0 <= map_y < height:
                room = self.rooms[room_id]
                
                if room_id == self.player_location:
                    map_grid[map_y][map_x] = self.symbols['player']
                elif room_id == "start_room":
                    map_grid[map_y][map_x] = self.symbols['start_room'] if room.visited else self.symbols['unvisited_room']
                elif room.visited:
                    map_grid[map_y][map_x] = self.symbols['visited_room']
                else:
                    map_grid[map_y][map_x] = self.symbols['unvisited_room']
        
        # Add connections (corridors) between adjacent rooms
        for room_id, room in self.rooms.items():
            if not room.visited:
                continue
                
            room_x, room_y = self.room_coordinates[room_id]
            map_x = center_x + (room_x - player_x)
            map_y = center_y + (room_y - player_y)
            
            for direction, connected_room_id in room.connections.items():
                if connected_room_id in self.rooms and self.rooms[connected_room_id].visited:
                    # Draw connection only if the space is empty
                    if direction == 'north' and map_y > 0 and 0 <= map_x < width:
                        if map_grid[map_y - 1][map_x] == self.symbols['empty']:
                            map_grid[map_y - 1][map_x] = self.symbols['corridor_v']
                    elif direction == 'south' and map_y < height - 1 and 0 <= map_x < width:
                        if map_grid[map_y + 1][map_x] == self.symbols['empty']:
                            map_grid[map_y + 1][map_x] = self.symbols['corridor_v']
                    elif direction == 'east' and map_x < width - 1 and 0 <= map_y < height:
                        if map_grid[map_y][map_x + 1] == self.symbols['empty']:
                            map_grid[map_y][map_x + 1] = self.symbols['corridor_h']
                    elif direction == 'west' and map_x > 0 and 0 <= map_y < height:
                        if map_grid[map_y][map_x - 1] == self.symbols['empty']:
                            map_grid[map_y][map_x - 1] = self.symbols['corridor_h']
        
        # Convert grid to string
        map_lines = [''.join(row) for row in map_grid]
        
        # Add border and title
        border = '═' * (width + 2)
        title = "DUNGEON MAP"
        
        result = [
            f"╔{border}╗",
            f"║{title.center(width)}║",
            f"╠{border}╣"
        ]
        
        for line in map_lines:
            result.append(f"║ {line} ║")
        
        result.append(f"╚{border}╝")
        
        # Add legend
        result.extend([
            "",
            "LEGEND:",
            f"  {self.symbols['player']} = You are here",
            f"  {self.symbols['start_room']} = Starting room", 
            f"  {self.symbols['visited_room']} = Visited room",
            f"  {self.symbols['unvisited_room']} = Known room",
            f"  {self.symbols['corridor_h']}{self.symbols['corridor_v']} = Passages"
        ])
        
        return '\n'.join(result)
    
    def get_room_info(self, room_id: str) -> Dict:
        """Get information about a specific room"""
        if room_id in self.rooms:
            room = self.rooms[room_id]
            return {
                'room_id': room.room_id,
                'coordinates': (room.x, room.y),
                'visited': room.visited,
                'connections': room.connections,
                'is_current': room_id == self.player_location
            }
        return {}
    
    def get_exploration_stats(self) -> Dict:
        """Get statistics about exploration progress"""
        total_discovered = len(self.rooms)
        total_visited = len(self.visited_rooms)
        
        return {
            'rooms_discovered': total_discovered,
            'rooms_visited': total_visited,
            'exploration_percentage': (total_visited / total_discovered * 100) if total_discovered > 0 else 0,
            'current_location': self.player_location
        }
    
    def debug_map_state(self) -> str:
        """Get debug information about map state"""
        debug_info = [
            f"Player Location: {self.player_location}",
            f"Total Rooms: {len(self.rooms)}",
            f"Visited Rooms: {len(self.visited_rooms)}",
            f"Room Coordinates: {self.room_coordinates}",
            "Room Details:"
        ]
        
        for room_id, room in self.rooms.items():
            debug_info.append(f"  {room_id}: pos=({room.x}, {room.y}), visited={room.visited}, connections={room.connections}")
        
        return '\n'.join(debug_info)
    
    def sync_with_world(self, world, player):
        """Synchronize map system with the current world state"""
        # Update player location
        if hasattr(player, 'location') and player.location:
            self.player_location = player.location
            
            # Ensure player location is in our rooms - try to get position from spatial navigator first
            if player.location not in self.rooms:
                x, y = self._get_room_position_from_world(player.location, world)
                self.add_room(player.location, x, y)
            
            self.mark_visited(player.location)
        
        # Sync all visited rooms from player
        if hasattr(player, 'visited_rooms'):
            for room_id in player.visited_rooms:
                if room_id not in self.rooms:
                    # Try to get position from spatial navigator, fallback to calculation
                    x, y = self._get_room_position_from_world(room_id, world)
                    self.add_room(room_id, x, y)
                self.mark_visited(room_id)
        
        # Update room connections from world
        if hasattr(world, 'rooms'):
            for room_id, world_room in world.rooms.items():
                if hasattr(world_room, 'connections') and room_id in self.rooms:
                    self.discover_room_exits(room_id, world_room.connections)
    
    def _get_room_position_from_world(self, room_id: str, world) -> Tuple[int, int]:
        """Get room position from world's spatial navigator, with fallback to calculation"""
        # Try to get from spatial navigator first
        if hasattr(world, 'spatial_navigator') and hasattr(world.spatial_navigator, 'room_positions'):
            if room_id in world.spatial_navigator.room_positions:
                pos = world.spatial_navigator.room_positions[room_id]
                return (pos[0], pos[1])  # Use x,y and ignore z
        
        # Fallback to calculation based on room ID
        if self.player_location and self.player_location in self.room_coordinates:
            return self._calculate_room_position(room_id, self.player_location)
        
        return (0, 0)  # Final fallback