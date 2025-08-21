"""
Main game loop for Angles of Authority
Handles timing, frame rate, and scene management
"""

import pygame
from .scene_manager import SceneManager
from .input_handler import InputHandler

class GameLoop:
    """Main game loop with delta time and pause support"""
    
    def __init__(self, screen, input_handler: InputHandler, scene_manager: SceneManager):
        self.screen = screen
        self.input_handler = input_handler
        self.scene_manager = scene_manager
        
        # Timing
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        self.dt = 0.0  # Delta time in seconds
        
        # Game state
        self.running = True
        self.paused = False
        
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            self._handle_events()
            
            # Update game state
            if not self.paused:
                self._update()
            
            # Render
            self._render()
            
            # Cap frame rate
            self.dt = self.clock.tick(self.target_fps) / 1000.0
    
    def _handle_events(self):
        """Process all pending events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
            
            # Pass events to input handler and current scene
            self.input_handler.handle_event(event)
            current_scene = self.scene_manager.get_current_scene()
            if current_scene:
                current_scene.handle_event(event)
    
    def _update(self):
        """Update game logic"""
        # Update input handler
        self.input_handler.update(self.dt)
        
        # Update current scene
        current_scene = self.scene_manager.get_current_scene()
        if current_scene:
            current_scene.update(self.dt)
    
    def _render(self):
        """Render the current scene"""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render current scene
        current_scene = self.scene_manager.get_current_scene()
        if current_scene:
            current_scene.render(self.screen)
        
        # Update display
        pygame.display.flip()
