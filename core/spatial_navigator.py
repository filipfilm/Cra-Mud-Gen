"""
Spatial Navigation System for Cra-mud-gen
Ensures logical consistency in dungeon layout and navigation
"""
from typing import Dict, List, Tuple, Optional, Set
import random

class SpatialNavigator:
    """
    Manages spatial consistency and logical navigation in the dungeon
    """
    
    def __init__(self):
        # Track room positions in a coordinate system
        self.room_positions: Dict[str, Tuple[int, int, int]] = {}  # room_id -> (x, y, z)
        self.position_rooms: Dict[Tuple[int, int, int], str] = {}  # (x, y, z) -> room_id
        self.room_connections: Dict[str, Dict[str, str]] = {}  # room_id -> {direction: target_room}
        
        # Direction vectors for movement
        self.direction_vectors = {
            "north": (0, 1, 0),   # +Y is north
            "south": (0, -1, 0),  # -Y is south  
            "east": (1, 0, 0),    # +X is east
            "west": (-1, 0, 0),   # -X is west
            "up": (0, 0, 1),      # +Z is up
            "down": (0, 0, -1)    # -Z is down
        }
        
        # Opposite directions for backtracking
        self.opposite_directions = {
            "north": "south", "south": "north",
            "east": "west", "west": "east", 
            "up": "down", "down": "up"
        }
        
        # Initialize with starting room at origin
        self.add_room("start_room", 0, 0, 0)
    
    def add_room(self, room_id: str, x: int, y: int, z: int = 0):
        """Add a room at specific coordinates"""
        position = (x, y, z)
        self.room_positions[room_id] = position
        self.position_rooms[position] = room_id
        
        if room_id not in self.room_connections:
            self.room_connections[room_id] = {}
    
    def get_room_position(self, room_id: str) -> Optional[Tuple[int, int, int]]:
        """Get the position of a room"""
        return self.room_positions.get(room_id)
    
    def get_room_at_position(self, x: int, y: int, z: int = 0) -> Optional[str]:
        """Get the room at a specific position"""
        return self.position_rooms.get((x, y, z))
    
    def create_connection(self, from_room: str, direction: str, to_room: str):
        """Create a bidirectional connection between two rooms"""
        # Add forward connection
        self.room_connections[from_room][direction] = to_room
        
        # Add reverse connection
        opposite = self.opposite_directions.get(direction)
        if opposite:
            if to_room not in self.room_connections:
                self.room_connections[to_room] = {}
            self.room_connections[to_room][opposite] = from_room
    
    def generate_connected_room(self, from_room: str, direction: str, depth: int) -> str:
        """
        Generate a new room in the specified direction with proper spatial consistency
        """
        if from_room not in self.room_positions:
            raise ValueError(f"Source room {from_room} not found in spatial navigator")
        
        # Get source position
        from_x, from_y, from_z = self.room_positions[from_room]
        
        # Calculate target position
        dx, dy, dz = self.direction_vectors[direction]
        to_x, to_y, to_z = from_x + dx, from_y + dy, from_z + dz
        
        # Check if room already exists at target position
        existing_room = self.get_room_at_position(to_x, to_y, to_z)
        if existing_room:
            # Connect to existing room
            self.create_connection(from_room, direction, existing_room)
            return existing_room
        
        # Generate new room ID based on position and depth
        new_room_id = self._generate_room_id(to_x, to_y, to_z, depth)
        
        # Add new room and create connection
        self.add_room(new_room_id, to_x, to_y, to_z)
        self.create_connection(from_room, direction, new_room_id)
        
        return new_room_id
    
    def _generate_room_id(self, x: int, y: int, z: int, depth: int) -> str:
        """Generate a descriptive room ID based on position"""
        # Create descriptive name based on relative position to start
        descriptors = []
        
        if y > 0:
            descriptors.append(f"n{y}")
        elif y < 0:
            descriptors.append(f"s{abs(y)}")
            
        if x > 0:
            descriptors.append(f"e{x}")
        elif x < 0:
            descriptors.append(f"w{abs(x)}")
            
        if z > 0:
            descriptors.append(f"u{z}")
        elif z < 0:
            descriptors.append(f"d{abs(z)}")
        
        if descriptors:
            return "_".join(descriptors)
        else:
            return f"room_{depth}"
    
    def generate_logical_exits(self, room_id: str, max_exits: int = 3, 
                              came_from_direction: str = None) -> List[str]:
        """
        Generate logical exits for a room that maintain spatial consistency
        """
        if room_id not in self.room_positions:
            return []
        
        available_directions = list(self.direction_vectors.keys())
        
        # Remove the direction we came from (to avoid immediate backtrack as new exit)
        if came_from_direction:
            opposite = self.opposite_directions.get(came_from_direction)
            if opposite in available_directions:
                available_directions.remove(opposite)
        
        # Remove directions that already have connections
        existing_connections = self.room_connections.get(room_id, {})
        for direction in list(existing_connections.keys()):
            if direction in available_directions:
                available_directions.remove(direction)
        
        # Select random directions for new exits
        num_exits = min(random.randint(1, max_exits), len(available_directions))
        selected_directions = random.sample(available_directions, num_exits)
        
        return selected_directions
    
    def get_room_connections(self, room_id: str) -> Dict[str, str]:
        """Get all connections for a room"""
        return self.room_connections.get(room_id, {}).copy()
    
    def get_connection_list(self, room_id: str) -> List[str]:
        """Get connections in the format expected by the existing system"""
        connections = self.room_connections.get(room_id, {})
        return [f"{direction}_{target}" for direction, target in connections.items()]
    
    def validate_connections(self) -> Dict[str, List[str]]:
        """Validate that all connections are bidirectional"""
        issues = {
            "missing_reverse": [],
            "position_mismatch": [],
            "dangling_connections": []
        }
        
        for room_id, connections in self.room_connections.items():
            for direction, target_room in connections.items():
                # Check if target room exists
                if target_room not in self.room_positions:
                    issues["dangling_connections"].append(f"{room_id} -> {direction} -> {target_room}")
                    continue
                
                # Check if reverse connection exists
                opposite = self.opposite_directions.get(direction)
                if opposite:
                    target_connections = self.room_connections.get(target_room, {})
                    if target_connections.get(opposite) != room_id:
                        issues["missing_reverse"].append(f"{room_id} <-> {target_room} ({direction})")
                
                # Check if spatial positions are consistent
                from_pos = self.room_positions[room_id]
                to_pos = self.room_positions[target_room] 
                expected_vector = self.direction_vectors[direction]
                
                actual_vector = (
                    to_pos[0] - from_pos[0],
                    to_pos[1] - from_pos[1], 
                    to_pos[2] - from_pos[2]
                )
                
                if actual_vector != expected_vector:
                    issues["position_mismatch"].append(
                        f"{room_id} -> {target_room}: expected {expected_vector}, got {actual_vector}"
                    )
        
        return issues
    
    def fix_connections(self):
        """Attempt to fix connection issues"""
        issues = self.validate_connections()
        
        # Fix missing reverse connections
        for issue in issues["missing_reverse"]:
            room_parts = issue.split(" <-> ")
            if len(room_parts) == 2:
                room1, rest = room_parts
                room2_and_dir = rest.split(" (")
                if len(room2_and_dir) == 2:
                    room2 = room2_and_dir[0]
                    direction = room2_and_dir[1].rstrip(")")
                    opposite = self.opposite_directions.get(direction)
                    
                    if opposite and room2 in self.room_connections:
                        self.room_connections[room2][opposite] = room1
    
    def get_debug_info(self) -> str:
        """Get debug information about the spatial state"""
        info = [
            f"Total rooms: {len(self.room_positions)}",
            f"Total positions: {len(self.position_rooms)}",
            "\nRoom positions:"
        ]
        
        for room_id, position in sorted(self.room_positions.items()):
            connections = list(self.room_connections.get(room_id, {}).keys())
            info.append(f"  {room_id}: {position} -> {connections}")
        
        # Validation issues
        issues = self.validate_connections()
        if any(issues.values()):
            info.append("\nValidation issues:")
            for issue_type, problems in issues.items():
                if problems:
                    info.append(f"  {issue_type}: {len(problems)} issues")
                    for problem in problems[:3]:  # Show first 3
                        info.append(f"    {problem}")
        
        return "\n".join(info)