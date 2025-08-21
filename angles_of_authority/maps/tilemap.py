"""
Tilemap system for loading and managing CSV-based maps
Supports different tile types and collision detection
"""

import csv
import os
from typing import List, Dict, Tuple, Optional
from enum import Enum

class TileType(Enum):
    """Types of tiles in the map"""
    EMPTY = 0
    WALL = 1
    FLOOR = 2
    DOOR = 3
    COVER = 4
    SPAWN_POINT = 5
    EXIT = 6

class Tile:
    """Represents a single tile in the map"""
    
    def __init__(self, x: int, y: int, tile_type: TileType, properties: Dict = None):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.properties = properties or {}
        self.occupied = False  # Whether an entity is on this tile
        self.visible = True    # Whether this tile blocks vision
    
    def is_walkable(self) -> bool:
        """Check if entities can walk on this tile"""
        return self.tile_type in [TileType.FLOOR, TileType.SPAWN_POINT, TileType.EXIT]
    
    def is_collision(self) -> bool:
        """Check if this tile blocks movement"""
        return self.tile_type in [TileType.WALL, TileType.DOOR, TileType.COVER]
    
    def blocks_vision(self) -> bool:
        """Check if this tile blocks line of sight"""
        return self.tile_type in [TileType.WALL, TileType.DOOR] and self.visible
    
    def __str__(self) -> str:
        return f"Tile({self.x}, {self.y}, {self.tile_type.name})"

class Tilemap:
    """Manages a grid-based tilemap loaded from CSV"""
    
    def __init__(self, width: int, height: int, tile_size: int = 32):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.tiles: List[List[Tile]] = []
        self.spawn_points: List[Tuple[int, int]] = []
        self.exit_points: List[Tuple[int, int]] = []
        
        # Initialize empty tilemap
        self._initialize_empty_map()
    
    def _initialize_empty_map(self):
        """Initialize the tilemap with empty tiles"""
        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile = Tile(x, y, TileType.EMPTY)
                row.append(tile)
            self.tiles.append(row)
    
    def load_from_csv(self, filepath: str) -> bool:
        """Load tilemap from a CSV file"""
        if not os.path.exists(filepath):
            print(f"Error: Map file not found: {filepath}")
            return False
        
        try:
            with open(filepath, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
                
                if not rows:
                    print("Error: Empty CSV file")
                    return False
                
                # Validate dimensions
                if len(rows) != self.height:
                    print(f"Error: CSV height ({len(rows)}) doesn't match expected height ({self.height})")
                    return False
                
                for y, row in enumerate(rows):
                    if len(row) != self.width:
                        print(f"Error: Row {y} width ({len(row)}) doesn't match expected width ({self.width})")
                        return False
                    
                    for x, cell in enumerate(row):
                        tile_type = self._parse_tile_cell(cell)
                        properties = self._parse_tile_properties(cell)
                        
                        tile = Tile(x, y, tile_type, properties)
                        self.tiles[y][x] = tile
                        
                        # Track special tiles
                        if tile_type == TileType.SPAWN_POINT:
                            self.spawn_points.append((x, y))
                        elif tile_type == TileType.EXIT:
                            self.exit_points.append((x, y))
                
                print(f"Successfully loaded map: {self.width}x{self.height} tiles")
                print(f"Found {len(self.spawn_points)} spawn points and {len(self.exit_points)} exit points")
                return True
                
        except Exception as e:
            print(f"Error loading map: {e}")
            return False
    
    def _parse_tile_cell(self, cell: str) -> TileType:
        """Parse a CSV cell into a tile type"""
        cell = cell.strip().upper()
        
        # Map cell values to tile types
        tile_mapping = {
            '0': TileType.EMPTY,
            '1': TileType.WALL,
            '2': TileType.FLOOR,
            '3': TileType.DOOR,
            '4': TileType.COVER,
            '5': TileType.SPAWN_POINT,
            '6': TileType.EXIT,
            'W': TileType.WALL,
            'F': TileType.FLOOR,
            'D': TileType.DOOR,
            'C': TileType.COVER,
            'S': TileType.SPAWN_POINT,
            'E': TileType.EXIT,
            '': TileType.EMPTY
        }
        
        return tile_mapping.get(cell, TileType.EMPTY)
    
    def _parse_tile_properties(self, cell: str) -> Dict:
        """Parse additional properties from a tile cell"""
        properties = {}
        
        # Check for special properties (e.g., "3:closed" for closed door)
        if ':' in cell:
            parts = cell.split(':')
            if len(parts) == 2:
                properties['state'] = parts[1].strip()
        
        return properties
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get a tile at specific coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
    
    def set_tile(self, x: int, y: int, tile_type: TileType, properties: Dict = None):
        """Set a tile at specific coordinates"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = Tile(x, y, tile_type, properties or {})
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a position is walkable"""
        tile = self.get_tile(x, y)
        return tile.is_walkable() if tile else False
    
    def is_collision(self, x: int, y: int) -> bool:
        """Check if a position has collision"""
        tile = self.get_tile(x, y)
        return tile.is_collision() if tile else False
    
    def blocks_vision(self, x: int, y: int) -> bool:
        """Check if a position blocks vision"""
        tile = self.get_tile(x, y)
        return tile.blocks_vision() if tile else False
    
    def world_to_tile(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convert world coordinates to tile coordinates"""
        tile_x = int(world_x // self.tile_size)
        tile_y = int(world_y // self.tile_size)
        return tile_x, tile_y
    
    def tile_to_world(self, tile_x: int, tile_y: int) -> Tuple[float, float]:
        """Convert tile coordinates to world coordinates (center of tile)"""
        world_x = (tile_x * self.tile_size) + (self.tile_size / 2)
        world_y = (tile_y * self.tile_size) + (self.tile_size / 2)
        return world_x, world_y
    
    def get_random_spawn_point(self) -> Optional[Tuple[int, int]]:
        """Get a random spawn point"""
        import random
        if self.spawn_points:
            return random.choice(self.spawn_points)
        return None
    
    def get_nearest_spawn_point(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Get the nearest spawn point to given coordinates"""
        if not self.spawn_points:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for spawn_x, spawn_y in self.spawn_points:
            distance = ((x - spawn_x) ** 2 + (y - spawn_y) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest = (spawn_x, spawn_y)
        
        return nearest
    
    def debug_info(self) -> str:
        """Get debug information about the tilemap"""
        info = f"Tilemap: {self.width}x{self.height} tiles ({self.tile_size}px each)\n"
        info += f"Spawn points: {len(self.spawn_points)}\n"
        info += f"Exit points: {len(self.exit_points)}\n"
        
        # Count tile types
        tile_counts = {}
        for row in self.tiles:
            for tile in row:
                tile_type = tile.tile_type.name
                tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
        
        info += "Tile distribution:\n"
        for tile_type, count in tile_counts.items():
            info += f"  {tile_type}: {count}\n"
        
        return info
