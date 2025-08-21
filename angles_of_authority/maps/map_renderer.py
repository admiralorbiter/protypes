"""
Map renderer for displaying tilemaps with different visual styles
Handles rendering of walls, floors, doors, and other tile types
"""

import pygame
from .tilemap import Tilemap, TileType

class MapRenderer:
    """Renders tilemaps with visual styling and effects"""
    
    def __init__(self, tilemap: Tilemap):
        self.tilemap = tilemap
        self.tile_size = tilemap.tile_size
        
        # Color scheme for different tile types
        self.tile_colors = {
            TileType.EMPTY: (0, 0, 0),      # Black
            TileType.WALL: (64, 64, 64),    # Dark gray
            TileType.FLOOR: (128, 128, 128), # Light gray
            TileType.DOOR: (139, 69, 19),   # Brown
            TileType.COVER: (34, 139, 34),  # Forest green
            TileType.SPAWN_POINT: (0, 255, 0), # Green
            TileType.EXIT: (255, 0, 0)      # Red
        }
        
        # Tile borders and effects
        self.show_grid = True
        self.grid_color = (40, 40, 40)
        self.border_color = (20, 20, 20)
    
    def render(self, screen: pygame.Surface, camera_offset: tuple = (0, 0)):
        """Render the entire tilemap"""
        # Calculate visible tile range based on camera
        screen_width, screen_height = screen.get_size()
        start_x = max(0, int(camera_offset[0] // self.tile_size))
        end_x = min(self.tilemap.width, int((camera_offset[0] + screen_width) // self.tile_size) + 1)
        start_y = max(0, int(camera_offset[1] // self.tile_size))
        end_y = min(self.tilemap.height, int((camera_offset[1] + screen_height) // self.tile_size) + 1)
        
        # Render visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                self._render_tile(screen, x, y, camera_offset)
    
    def _render_tile(self, screen: pygame.Surface, tile_x: int, tile_y: int, camera_offset: tuple):
        """Render a single tile"""
        tile = self.tilemap.get_tile(tile_x, tile_y)
        if not tile:
            return
        
        # Calculate screen position
        screen_x = (tile_x * self.tile_size) - camera_offset[0]
        screen_y = (tile_y * self.tile_size) - camera_offset[1]
        
        # Get tile color
        color = self.tile_colors.get(tile.tile_type, (255, 0, 255))  # Magenta for unknown types
        
        # Draw tile background
        tile_rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
        pygame.draw.rect(screen, color, tile_rect)
        
        # Draw tile border
        pygame.draw.rect(screen, self.border_color, tile_rect, 1)
        
        # Draw special tile indicators
        self._render_tile_indicators(screen, tile, screen_x, screen_y)
        
        # Draw grid lines if enabled
        if self.show_grid:
            pygame.draw.line(screen, self.grid_color, 
                           (screen_x, screen_y), 
                           (screen_x + self.tile_size, screen_y), 1)
            pygame.draw.line(screen, self.grid_color, 
                           (screen_x, screen_y), 
                           (screen_x, screen_y + self.tile_size), 1)
    
    def _render_tile_indicators(self, screen: pygame.Surface, tile: 'Tile', screen_x: int, screen_y: int):
        """Render special indicators for specific tile types"""
        center_x = screen_x + self.tile_size // 2
        center_y = screen_y + self.tile_size // 2
        
        if tile.tile_type == TileType.SPAWN_POINT:
            # Draw green circle for spawn points
            pygame.draw.circle(screen, (0, 200, 0), (center_x, center_y), 4)
            pygame.draw.circle(screen, (0, 100, 0), (center_x, center_y), 4, 1)
        
        elif tile.tile_type == TileType.EXIT:
            # Draw red X for exit points
            size = 6
            pygame.draw.line(screen, (200, 0, 0), 
                           (center_x - size, center_y - size), 
                           (center_x + size, center_y + size), 2)
            pygame.draw.line(screen, (200, 0, 0), 
                           (center_x + size, center_y - size), 
                           (center_x - size, center_y + size), 2)
        
        elif tile.tile_type == TileType.DOOR:
            # Draw door handle
            handle_x = center_x + 4
            handle_y = center_y
            pygame.draw.circle(screen, (139, 69, 19), (handle_x, handle_y), 2)
        
        elif tile.tile_type == TileType.COVER:
            # Draw cover pattern (diagonal lines)
            for i in range(0, self.tile_size, 4):
                start_x = screen_x + i
                start_y = screen_y
                end_x = start_x + 4
                end_y = start_y + 4
                if start_x < screen_x + self.tile_size and start_y < screen_y + self.tile_size:
                    pygame.draw.line(screen, (20, 100, 20), 
                                   (start_x, start_y), (end_x, end_y), 1)
    
    def set_tile_color(self, tile_type: TileType, color: tuple):
        """Set custom color for a tile type"""
        self.tile_colors[tile_type] = color
    
    def toggle_grid(self):
        """Toggle grid display on/off"""
        self.show_grid = not self.show_grid
    
    def get_tile_at_screen_pos(self, screen_x: int, screen_y: int, camera_offset: tuple) -> tuple:
        """Convert screen coordinates to tile coordinates"""
        world_x = screen_x + camera_offset[0]
        world_y = screen_y + camera_offset[1]
        return self.tilemap.world_to_tile(world_x, world_y)
    
    def render_minimap(self, screen: pygame.Surface, minimap_rect: pygame.Rect):
        """Render a minimap in the specified rectangle"""
        # Calculate scale factor
        scale_x = minimap_rect.width / self.tilemap.width
        scale_y = minimap_rect.height / self.tilemap.height
        scale = min(scale_x, scale_y)
        
        # Calculate minimap position (centered)
        minimap_width = int(self.tilemap.width * scale)
        minimap_height = int(self.tilemap.height * scale)
        minimap_x = minimap_rect.x + (minimap_rect.width - minimap_width) // 2
        minimap_y = minimap_rect.y + (minimap_rect.height - minimap_height) // 2
        
        # Draw minimap background
        pygame.draw.rect(screen, (20, 20, 20), minimap_rect)
        
        # Render minimap tiles
        for y in range(self.tilemap.height):
            for x in range(self.tilemap.width):
                tile = self.tilemap.get_tile(x, y)
                if tile:
                    color = self.tile_colors.get(tile.tile_type, (255, 0, 255))
                    minimap_tile_x = minimap_x + int(x * scale)
                    minimap_tile_y = minimap_y + int(y * scale)
                    minimap_tile_size = max(1, int(scale))
                    
                    tile_rect = pygame.Rect(minimap_tile_x, minimap_tile_y, 
                                          minimap_tile_size, minimap_tile_size)
                    pygame.draw.rect(screen, color, tile_rect)
        
        # Draw minimap border
        pygame.draw.rect(screen, (100, 100, 100), 
                        (minimap_x, minimap_y, minimap_width, minimap_height), 1)
