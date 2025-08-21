"""
Map builder system for creating complex maps from smaller templates
Allows procedural generation and composition of room layouts
"""

import os
import random
from typing import List, Dict, Tuple, Optional
from .tilemap import Tilemap, TileType, Tile

class MapTemplate:
    """Represents a small map template that can be combined with others"""
    
    def __init__(self, name: str, width: int, height: int):
        self.name = name
        self.width = width
        self.height = height
        self.tiles: List[List[TileType]] = []
        self.spawn_points: List[Tuple[int, int]] = []
        self.exit_points: List[Tuple[int, int]] = []
        self.connection_points: List[Tuple[int, int, str]] = []  # x, y, direction
    
    def add_row(self, row: List[TileType]):
        """Add a row of tiles to the template"""
        if len(row) != self.width:
            raise ValueError(f"Row width {len(row)} doesn't match template width {self.width}")
        self.tiles.append(row)
    
    def add_spawn_point(self, x: int, y: int):
        """Add a spawn point to the template"""
        self.spawn_points.append((x, y))
    
    def add_exit_point(self, x: int, y: int):
        """Add an exit point to the template"""
        self.exit_points.append((x, y))
    
    def add_connection_point(self, x: int, y: int, direction: str):
        """Add a connection point for joining with other templates"""
        self.connection_points.append((x, y, direction))

class MapBuilder:
    """Builds complex maps from templates and procedural generation"""
    
    def __init__(self):
        self.templates: Dict[str, MapTemplate] = {}
        self._create_basic_templates()
    
    def _create_basic_templates(self):
        """Create basic room templates"""
        self._create_empty_room_template()
        self._create_hallway_template()
        self._create_corner_room_template()
        self._create_apartment_room_template()
    
    def _create_empty_room_template(self):
        """Create a simple empty room template"""
        template = MapTemplate("empty_room", 8, 6)
        
        # Add walls around perimeter, floor inside
        for y in range(6):
            row = []
            for x in range(8):
                if x == 0 or x == 7 or y == 0 or y == 5:
                    row.append(TileType.WALL)
                else:
                    row.append(TileType.FLOOR)
            template.add_row(row)
        
        # Add connection points on each wall
        template.add_connection_point(4, 0, "north")  # Top wall
        template.add_connection_point(4, 5, "south")  # Bottom wall
        template.add_connection_point(0, 3, "west")   # Left wall
        template.add_connection_point(7, 3, "east")   # Right wall
        
        self.templates["empty_room"] = template
    
    def _create_hallway_template(self):
        """Create a hallway template"""
        template = MapTemplate("hallway", 8, 3)
        
        # Horizontal hallway
        for y in range(3):
            row = []
            for x in range(8):
                if y == 0 or y == 2:
                    row.append(TileType.WALL)
                else:
                    row.append(TileType.FLOOR)
            template.add_row(row)
        
        # Connection points at ends
        template.add_connection_point(0, 1, "west")
        template.add_connection_point(7, 1, "east")
        
        self.templates["hallway"] = template
    
    def _create_corner_room_template(self):
        """Create an L-shaped corner room"""
        template = MapTemplate("corner_room", 6, 6)
        
        # L-shaped room
        layout = [
            [1, 1, 1, 1, 0, 0],
            [1, 2, 2, 1, 0, 0],
            [1, 2, 2, 1, 0, 0],
            [1, 1, 1, 1, 1, 1],
            [0, 0, 0, 1, 2, 1],
            [0, 0, 0, 1, 1, 1]
        ]
        
        for row_data in layout:
            row = [TileType(val) for val in row_data]
            template.add_row(row)
        
        # Add some cover
        template.tiles[1][2] = TileType.COVER
        template.tiles[4][4] = TileType.COVER
        
        self.templates["corner_room"] = template
    
    def _create_apartment_room_template(self):
        """Create a furnished apartment room"""
        template = MapTemplate("apartment_room", 10, 8)
        
        # Room with furniture/cover
        for y in range(8):
            row = []
            for x in range(10):
                if x == 0 or x == 9 or y == 0 or y == 7:
                    row.append(TileType.WALL)
                else:
                    row.append(TileType.FLOOR)
            template.add_row(row)
        
        # Add furniture/cover
        template.tiles[2][2] = TileType.COVER  # Couch
        template.tiles[2][3] = TileType.COVER
        template.tiles[5][6] = TileType.COVER  # Table
        template.tiles[6][6] = TileType.COVER
        
        # Add door
        template.tiles[0][4] = TileType.DOOR
        
        # Add spawn point
        template.add_spawn_point(8, 6)
        
        self.templates["apartment_room"] = template
    
    def create_simple_apartment(self, width: int = 20, height: int = 15) -> Tilemap:
        """Create a simple apartment layout"""
        tilemap = Tilemap(width, height, 32)
        
        # Fill with walls first
        for y in range(height):
            for x in range(width):
                tilemap.set_tile(x, y, TileType.WALL)
        
        # Create main room (interior)
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                tilemap.set_tile(x, y, TileType.FLOOR)
        
        # Add interesting features
        self._add_apartment_features(tilemap, width, height)
        
        return tilemap
    
    def _add_apartment_features(self, tilemap: Tilemap, width: int, height: int):
        """Add doors, cover, spawn points to apartment"""
        # Add spawn point near entrance
        tilemap.set_tile(1, 1, TileType.SPAWN_POINT)
        
        # Add some doors
        tilemap.set_tile(width // 2, 0, TileType.DOOR)  # Top wall door
        tilemap.set_tile(0, height // 2, TileType.DOOR)  # Left wall door
        
        # Add cover objects (furniture)
        cover_positions = [
            (3, 3), (4, 3),  # Couch
            (width - 4, 3), (width - 3, 3),  # Another couch
            (width // 2, height // 2),  # Center table
            (width - 3, height - 3),  # Corner furniture
        ]
        
        for x, y in cover_positions:
            if 0 < x < width - 1 and 0 < y < height - 1:
                tilemap.set_tile(x, y, TileType.COVER)
        
        # Add exit point
        tilemap.set_tile(width - 2, height - 2, TileType.EXIT)
    
    def create_complex_apartment(self, width: int = 25, height: int = 20) -> Tilemap:
        """Create a more complex apartment with multiple rooms"""
        tilemap = Tilemap(width, height, 32)
        
        # Fill with walls first
        for y in range(height):
            for x in range(width):
                tilemap.set_tile(x, y, TileType.WALL)
        
        # Create multiple rooms
        self._create_living_room(tilemap, 1, 1, 12, 8)
        self._create_bedroom(tilemap, 14, 1, 10, 8)
        self._create_kitchen(tilemap, 1, 10, 8, 9)
        self._create_hallway(tilemap, 10, 10, 14, 3)
        
        # Connect rooms with doors
        tilemap.set_tile(12, 4, TileType.DOOR)  # Living room to hallway
        tilemap.set_tile(14, 4, TileType.DOOR)  # Hallway to bedroom
        tilemap.set_tile(8, 10, TileType.DOOR)  # Kitchen to hallway
        
        # Add entrance
        tilemap.set_tile(6, 0, TileType.DOOR)
        
        return tilemap
    
    def _create_living_room(self, tilemap: Tilemap, start_x: int, start_y: int, w: int, h: int):
        """Create a living room area"""
        # Floor
        for y in range(start_y, start_y + h):
            for x in range(start_x, start_x + w):
                if start_x < x < start_x + w - 1 and start_y < y < start_y + h - 1:
                    tilemap.set_tile(x, y, TileType.FLOOR)
        
        # Furniture
        tilemap.set_tile(start_x + 2, start_y + 2, TileType.COVER)  # Couch
        tilemap.set_tile(start_x + 3, start_y + 2, TileType.COVER)
        tilemap.set_tile(start_x + 6, start_y + 4, TileType.COVER)  # Table
        
        # Spawn point
        tilemap.set_tile(start_x + 1, start_y + 1, TileType.SPAWN_POINT)
    
    def _create_bedroom(self, tilemap: Tilemap, start_x: int, start_y: int, w: int, h: int):
        """Create a bedroom area"""
        # Floor
        for y in range(start_y, start_y + h):
            for x in range(start_x, start_x + w):
                if start_x < x < start_x + w - 1 and start_y < y < start_y + h - 1:
                    tilemap.set_tile(x, y, TileType.FLOOR)
        
        # Bed (cover)
        tilemap.set_tile(start_x + 2, start_y + 2, TileType.COVER)
        tilemap.set_tile(start_x + 3, start_y + 2, TileType.COVER)
        tilemap.set_tile(start_x + 2, start_y + 3, TileType.COVER)
        tilemap.set_tile(start_x + 3, start_y + 3, TileType.COVER)
        
        # Dresser
        tilemap.set_tile(start_x + 6, start_y + 1, TileType.COVER)
    
    def _create_kitchen(self, tilemap: Tilemap, start_x: int, start_y: int, w: int, h: int):
        """Create a kitchen area"""
        # Floor
        for y in range(start_y, start_y + h):
            for x in range(start_x, start_x + w):
                if start_x < x < start_x + w - 1 and start_y < y < start_y + h - 1:
                    tilemap.set_tile(x, y, TileType.FLOOR)
        
        # Kitchen island
        tilemap.set_tile(start_x + 3, start_y + 4, TileType.COVER)
        tilemap.set_tile(start_x + 4, start_y + 4, TileType.COVER)
        
        # Exit point
        tilemap.set_tile(start_x + 1, start_y + h - 2, TileType.EXIT)
    
    def _create_hallway(self, tilemap: Tilemap, start_x: int, start_y: int, w: int, h: int):
        """Create a hallway area"""
        # Floor
        for y in range(start_y, start_y + h):
            for x in range(start_x, start_x + w):
                if start_x < x < start_x + w - 1 and start_y < y < start_y + h - 1:
                    tilemap.set_tile(x, y, TileType.FLOOR)
    
    def save_map_to_csv(self, tilemap: Tilemap, filename: str):
        """Save a tilemap to CSV file"""
        filepath = f"maps/{filename}"
        with open(filepath, 'w', newline='') as f:
            for y in range(tilemap.height):
                row = []
                for x in range(tilemap.width):
                    tile = tilemap.get_tile(x, y)
                    row.append(str(tile.tile_type.value))
                f.write(','.join(row) + '\n')
        print(f"Map saved to {filepath}")
    
    def get_template(self, name: str) -> Optional[MapTemplate]:
        """Get a template by name"""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all available template names"""
        return list(self.templates.keys())
