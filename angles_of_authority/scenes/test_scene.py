"""
Test scene for development and debugging
Simple scene to verify basic infrastructure and ECS system
"""

import pygame
from core.scene import Scene
from ecs.entity_manager import EntityManager
from ecs.entity_factory import EntityFactory
from ecs.system import MovementSystem, RenderSystem, CollisionSystem, AISystem

class TestScene(Scene):
    """Simple test scene to verify basic functionality"""
    
    def __init__(self):
        super().__init__("Test")
        
        # Test data
        self.counter = 0
        self.font = None
        
        # ECS system
        self.entity_manager = EntityManager()
        self.entity_factory = EntityFactory(self.entity_manager)
        
        # Add systems
        self.entity_manager.add_system(MovementSystem())
        self.entity_manager.add_system(RenderSystem())
        self.entity_manager.add_system(CollisionSystem())
        self.entity_manager.add_system(AISystem())
        
        # Create test entities
        self._create_test_entities()
        
    def on_enter(self):
        """Initialize font when scene becomes active"""
        super().on_enter()
        self.font = pygame.font.Font(None, 36)
    
    def update(self, dt: float):
        """Update test scene logic"""
        self.counter += dt
        
        # Update ECS systems
        self.entity_manager.update_systems(dt)
    
    def render(self, screen: pygame.Surface):
        """Render test scene"""
        # Clear screen with dark blue
        screen.fill((20, 40, 80))
        
        if self.font:
            # Render test text
            text = self.font.render(f"Test Scene - Counter: {self.counter:.1f}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(text, text_rect)
            
            # Render instructions
            instructions = [
                "Controls:",
                "WASD - Move",
                "1/2 - Select Operator", 
                "V - Shout",
                "F - Flashbang",
                "K - Kick Door",
                "C - Cuff",
                "X - Secure Evidence",
                "R - Toggle ROE",
                "Space - Pause",
                "Escape - Quit"
            ]
            
            # Render ECS debug info
            ecs_info = [
                f"ECS: {self.entity_manager.get_entity_count()} entities, {self.entity_manager.get_system_count()} systems",
                "Entities created: Operator, Suspect, Civilian, Press, Cover, Door, Evidence, Wall"
            ]
            
            # Add ECS info to instructions
            instructions.extend([""] + ecs_info)
            
            y_offset = 100
            for instruction in instructions:
                inst_text = self.font.render(instruction, True, (200, 200, 200))
                inst_rect = inst_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + y_offset))
                screen.blit(inst_text, inst_rect)
                y_offset += 30
    
    def handle_event(self, event):
        """Handle events in test scene"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                print("ROE toggle pressed!")
            elif event.key == pygame.K_v:
                print("Shout action!")
            elif event.key == pygame.K_f:
                print("Flashbang action!")
            elif event.key == pygame.K_1:
                print("ECS Debug Info:")
                print(self.entity_manager.debug_info())
    
    def _create_test_entities(self):
        """Create test entities to verify ECS system"""
        # Create an operator
        operator = self.entity_factory.create_operator(100, 100, "Operator 1")
        
        # Create a suspect
        suspect = self.entity_factory.create_suspect(200, 150, "Suspect 1")
        
        # Create a civilian
        civilian = self.entity_factory.create_civilian(150, 200, "Civilian 1")
        
        # Create a press observer
        press = self.entity_factory.create_press_observer(250, 100, "Press 1")
        
        # Create some cover objects
        cover1 = self.entity_factory.create_cover_object(300, 200, 64, 32, "Cover 1")
        cover2 = self.entity_factory.create_cover_object(400, 150, 48, 48, "Cover 2")
        
        # Create a door
        door = self.entity_factory.create_door(350, 100, 32, 64, "Door 1")
        
        # Create evidence
        evidence = self.entity_factory.create_evidence(450, 250, "weapon", "Gun")
        
        # Create a wall
        wall = self.entity_factory.create_wall(500, 300, 128, 32, "Wall 1")
        
        print(f"Created {self.entity_manager.get_entity_count()} test entities")
        print("ECS System initialized successfully!")
