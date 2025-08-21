"""
Camera system for managing viewport and following entities
Handles scrolling, zooming, and viewport boundaries
"""

import pygame
from typing import Tuple, Optional
from ecs.entity import Entity

class Camera:
    """Camera system for managing the game viewport"""
    
    def __init__(self, screen_width: int, screen_height: int, world_width: int, world_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height
        
        # Camera position (top-left corner of viewport)
        self.x = 0
        self.y = 0
        
        # Camera settings
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        
        # Smooth following
        self.follow_target: Optional[Entity] = None
        self.follow_speed = 5.0  # Pixels per second
        self.follow_offset = (0, 0)  # Offset from target center
    
    def set_position(self, x: float, y: float):
        """Set camera position directly"""
        self.x = max(0, min(x, self.world_width - self.screen_width))
        self.y = max(0, min(y, self.world_height - self.screen_height))
    
    def move(self, dx: float, dy: float):
        """Move camera by delta amounts"""
        self.set_position(self.x + dx, self.y + dy)
    
    def center_on(self, x: float, y: float):
        """Center camera on a world position"""
        center_x = x - (self.screen_width / 2)
        center_y = y - (self.screen_height / 2)
        self.set_position(center_x, center_y)
    
    def follow_entity(self, entity: Entity, offset: Tuple[float, float] = (0, 0)):
        """Set camera to follow an entity"""
        self.follow_target = entity
        self.follow_offset = offset
    
    def stop_following(self):
        """Stop following any entity"""
        self.follow_target = None
    
    def update(self, dt: float):
        """Update camera position (called each frame)"""
        if self.follow_target:
            self._update_following(dt)
    
    def _update_following(self, dt: float):
        """Update camera position when following an entity"""
        if not self.follow_target:
            return
        
        # Get target position
        transform = self.follow_target.get_component('Transform')
        if not transform:
            return
        
        target_x = transform.x + self.follow_offset[0]
        target_y = transform.y + self.follow_offset[1]
        
        # Calculate desired camera position (centered on target)
        desired_x = target_x - (self.screen_width / 2)
        desired_y = target_y - (self.screen_height / 2)
        
        # Smoothly move camera towards desired position
        current_x = self.x
        current_y = self.y
        
        # Calculate distance to move
        dx = desired_x - current_x
        dy = desired_y - current_y
        
        # Apply smooth movement
        if abs(dx) > 1.0:
            self.x += dx * self.follow_speed * dt
        if abs(dy) > 1.0:
            self.y += dy * self.follow_speed * dt
        
        # Clamp to world boundaries
        self.set_position(self.x, self.y)
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """Convert world coordinates to screen coordinates"""
        screen_x = world_x - self.x
        screen_y = world_y - self.y
        return screen_x, screen_y
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates"""
        world_x = screen_x + self.x
        world_y = screen_y + self.y
        return world_x, world_y
    
    def is_visible(self, world_x: float, world_y: float, width: float = 0, height: float = 0) -> bool:
        """Check if a world position is visible in the camera viewport"""
        screen_x, screen_y = self.world_to_screen(world_x, world_y)
        
        # Check if position is within viewport bounds
        if screen_x + width < 0 or screen_x > self.screen_width:
            return False
        if screen_y + height < 0 or screen_y > self.screen_height:
            return False
        
        return True
    
    def get_viewport_rect(self) -> pygame.Rect:
        """Get the current viewport rectangle in world coordinates"""
        return pygame.Rect(self.x, self.y, self.screen_width, self.screen_height)
    
    def zoom_in(self, factor: float = 1.2):
        """Zoom in by a factor"""
        self.zoom = min(self.max_zoom, self.zoom * factor)
    
    def zoom_out(self, factor: float = 1.2):
        """Zoom out by a factor"""
        self.zoom = max(self.min_zoom, self.zoom / factor)
    
    def set_zoom(self, zoom: float):
        """Set zoom level directly"""
        self.zoom = max(self.min_zoom, min(self.max_zoom, zoom))
    
    def get_zoom(self) -> float:
        """Get current zoom level"""
        return self.zoom
    
    def shake(self, intensity: float, duration: float):
        """Add camera shake effect (placeholder for future implementation)"""
        # TODO: Implement camera shake
        pass
    
    def get_debug_info(self) -> str:
        """Get debug information about the camera"""
        info = f"Camera: pos({self.x:.1f}, {self.y:.1f}), zoom({self.zoom:.2f})\n"
        info += f"Viewport: {self.screen_width}x{self.screen_height}\n"
        info += f"World: {self.world_width}x{self.world_height}\n"
        
        if self.follow_target:
            info += f"Following: {self.follow_target.name} (ID: {self.follow_target.entity_id})\n"
        else:
            info += "Not following any entity\n"
        
        return info
