"""
Base scene class for Angles of Authority
All game scenes (Game, AAR, Menu) inherit from this
"""

import pygame
from abc import ABC, abstractmethod

class Scene(ABC):
    """Abstract base class for all game scenes"""
    
    def __init__(self, name: str):
        self.name = name
        self.active = False
    
    def on_enter(self):
        """Called when this scene becomes active"""
        self.active = True
    
    def on_exit(self):
        """Called when this scene becomes inactive"""
        self.active = False
    
    @abstractmethod
    def update(self, dt: float):
        """Update scene logic (called each frame)"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """Render the scene (called each frame)"""
        pass
    
    def handle_event(self, event):
        """Handle pygame events (can be overridden)"""
        pass
