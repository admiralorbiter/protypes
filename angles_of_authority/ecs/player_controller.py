"""
Player controller system for handling operator input and movement
Manages WASD movement, operator selection, and action commands
"""

import pygame
from typing import Dict, List, Optional
from .entity import Entity
from .component import Movement, Transform, Team

class PlayerController:
    """Handles player input and controls operator movement"""
    
    def __init__(self):
        self.selected_operator: Optional[Entity] = None
        self.operators: List[Entity] = []
        self.movement_keys = {
            pygame.K_w: (0, -1),    # Up
            pygame.K_s: (0, 1),     # Down
            pygame.K_a: (-1, 0),    # Left
            pygame.K_d: (1, 0),     # Right
        }
        self.movement_input = {key: False for key in self.movement_keys}
    
    def register_operator(self, operator: Entity):
        """Register an operator entity for control"""
        if operator.has_component(Team) and operator.get_component(Team).is_operator():
            self.operators.append(operator)
            if not self.selected_operator:
                self.selected_operator = operator
            print(f"Registered operator: {operator.name}")
    
    def select_operator(self, index: int):
        """Select operator by index (1-based)"""
        if 0 < index <= len(self.operators):
            self.selected_operator = self.operators[index - 1]
            print(f"Selected operator: {self.selected_operator.name}")
        else:
            print(f"No operator at index {index}")
    
    def handle_keydown(self, key: int):
        """Handle key press events"""
        if key in self.movement_keys:
            self.movement_input[key] = True
        elif key == pygame.K_1:
            self.select_operator(1)
        elif key == pygame.K_2:
            self.select_operator(2)
    
    def handle_keyup(self, key: int):
        """Handle key release events"""
        if key in self.movement_keys:
            self.movement_input[key] = False
    
    def update(self, dt: float):
        """Update player controller (called each frame)"""
        if not self.selected_operator:
            print("No selected operator")
            return
        
        # Get movement component
        movement = self.selected_operator.get_component(Movement)
        if not movement:
            print("Selected operator has no Movement component")
            return
        
        # Calculate movement direction
        dx, dy = 0, 0
        for key, (key_dx, key_dy) in self.movement_keys.items():
            if self.movement_input[key]:
                dx += key_dx
                dy += key_dy
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/√2
            dy *= 0.707
        
        # Apply movement
        if dx != 0 or dy != 0:
            # Calculate velocity based on speed
            velocity_x = dx * movement.speed
            velocity_y = dy * movement.speed
            movement.set_velocity(velocity_x, velocity_y)
        else:
            # No input, let friction slow down
            movement.set_velocity(0, 0)
    
    def get_selected_operator(self) -> Optional[Entity]:
        """Get currently selected operator"""
        return self.selected_operator
    
    def get_operator_count(self) -> int:
        """Get number of registered operators"""
        return len(self.operators)
    
    def get_operator_info(self) -> str:
        """Get debug info about operators"""
        info = f"Player Controller: {len(self.operators)} operators\n"
        for i, operator in enumerate(self.operators, 1):
            selected = " (SELECTED)" if operator == self.selected_operator else ""
            info += f"  {i}: {operator.name}{selected}\n"
        return info
