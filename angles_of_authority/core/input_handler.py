"""
Input handling system for Angles of Authority
Manages keyboard and mouse input with configurable bindings
"""

import pygame
from typing import Dict, Callable, Any

class InputHandler:
    """Handles all input processing and binding"""
    
    def __init__(self):
        # Input state
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
        
        # Mouse state
        self.mouse_pos = (0, 0)
        self.mouse_buttons = [False, False, False]  # Left, Middle, Right
        self.mouse_buttons_just_pressed = [False, False, False]
        self.mouse_buttons_just_released = [False, False, False]
        
        # Action bindings
        self.action_bindings: Dict[str, Callable] = {}
        self.key_bindings: Dict[int, str] = {}
        
        # Setup default bindings
        self._setup_default_bindings()
    
    def _setup_default_bindings(self):
        """Setup default key bindings"""
        # Movement
        self.bind_key(pygame.K_w, "move_up")
        self.bind_key(pygame.K_s, "move_down")
        self.bind_key(pygame.K_a, "move_left")
        self.bind_key(pygame.K_d, "move_right")
        
        # Operator selection
        self.bind_key(pygame.K_1, "select_operator_1")
        self.bind_key(pygame.K_2, "select_operator_2")
        
        # Actions
        self.bind_key(pygame.K_v, "shout")
        self.bind_key(pygame.K_f, "flashbang")
        self.bind_key(pygame.K_k, "kick_door")
        self.bind_key(pygame.K_c, "cuff")
        self.bind_key(pygame.K_x, "secure_evidence")
        self.bind_key(pygame.K_r, "toggle_roe")
        
        # Game control
        self.bind_key(pygame.K_SPACE, "pause")
        self.bind_key(pygame.K_ESCAPE, "quit")
    
    def bind_key(self, key: int, action: str):
        """Bind a key to an action"""
        self.key_bindings[key] = action
    
    def bind_action(self, action: str, callback: Callable):
        """Bind an action to a callback function"""
        self.action_bindings[action] = callback
    
    def handle_event(self, event):
        """Process a single pygame event"""
        if event.type == pygame.KEYDOWN:
            key = event.key
            self.keys_pressed.add(key)
            self.keys_just_pressed.add(key)
            
            # Check for action binding
            if key in self.key_bindings:
                action = self.key_bindings[key]
                if action in self.action_bindings:
                    self.action_bindings[action]()
        
        elif event.type == pygame.KEYUP:
            key = event.key
            self.keys_pressed.discard(key)
            self.keys_just_released.add(key)
        
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            button = event.button - 1  # Convert to 0-based index
            if 0 <= button < 3:
                self.mouse_buttons[button] = True
                self.mouse_buttons_just_pressed[button] = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            button = event.button - 1
            if 0 <= button < 3:
                self.mouse_buttons[button] = False
                self.mouse_buttons_just_released[button] = True
    
    def update(self, dt: float):
        """Update input state (called each frame)"""
        # Clear just-pressed and just-released states
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        
        for i in range(3):
            self.mouse_buttons_just_pressed[i] = False
            self.mouse_buttons_just_released[i] = False
    
    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed"""
        return key in self.keys_pressed
    
    def is_key_just_pressed(self, key: int) -> bool:
        """Check if a key was just pressed this frame"""
        return key in self.keys_just_pressed
    
    def is_key_just_released(self, key: int) -> bool:
        """Check if a key was just released this frame"""
        return key in self.keys_just_released
    
    def get_mouse_pos(self) -> tuple:
        """Get current mouse position"""
        return self.mouse_pos
    
    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is pressed"""
        if 0 <= button < 3:
            return self.mouse_buttons[button]
        return False
    
    def is_mouse_button_just_pressed(self, button: int) -> bool:
        """Check if a mouse button was just pressed"""
        if 0 <= button < 3:
            return self.mouse_buttons_just_pressed[button]
        return False
