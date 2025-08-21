"""
Test scene for development and debugging
Simple scene to verify basic infrastructure and ECS system
"""

import pygame
from core.scene import Scene
from ecs.entity_manager import EntityManager
from ecs.entity_factory import EntityFactory
from ecs.system import MovementSystem, RenderSystem, CollisionSystem, AISystem
from maps.tilemap import Tilemap
from maps.map_renderer import MapRenderer
from maps.map_builder import MapBuilder
from core.camera import Camera

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
        
        # Map system
        self.map_builder = MapBuilder()
        self.tilemap = None
        self.map_renderer = None
        self.camera = None
        
        # Create test entities
        self._create_test_entities()
        
        # Load map
        self._load_map()
        
    def on_enter(self):
        """Initialize font when scene becomes active"""
        super().on_enter()
        self.font = pygame.font.Font(None, 36)
    
    def update(self, dt: float):
        """Update test scene logic"""
        self.counter += dt
        
        # Update ECS systems
        self.entity_manager.update_systems(dt)
        
        # Update camera
        self.camera.update(dt)
    
    def render(self, screen: pygame.Surface):
        """Render test scene"""
        # Clear screen with dark blue
        screen.fill((20, 40, 80))
        
        # Render map
        camera_offset = (self.camera.x, self.camera.y)
        self.map_renderer.render(screen, camera_offset)
        
        # Render minimap
        minimap_rect = pygame.Rect(10, 10, 150, 100)
        self.map_renderer.render_minimap(screen, minimap_rect)
        
        if self.font:
            # Render test text
            text = self.font.render(f"Test Scene - Counter: {self.counter:.1f}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(text, text_rect)
            
            # Render instructions
            instructions = [
                "Controls:",
                "WASD - Move",
                "1 - ECS Debug Info",
                "2 - Simple Apartment",
                "3 - Complex Apartment", 
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
                "Entities created: Operator, Suspect, Civilian, Press, Cover, Door, Evidence, Wall",
                f"Map: {self.tilemap.width}x{self.tilemap.height} tiles",
                f"Camera: ({self.camera.x:.0f}, {self.camera.y:.0f})"
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
            elif event.key == pygame.K_2:
                print("Generating simple apartment...")
                self._load_simple_apartment()
            elif event.key == pygame.K_3:
                print("Generating complex apartment...")
                self._load_complex_apartment()
    
    def _load_map(self):
        """Create and load the apartment map using MapBuilder"""
        print("Creating apartment map...")
        
        # Create a complex apartment
        self.tilemap = self.map_builder.create_complex_apartment(25, 20)
        
        # Set up renderer and camera
        self.map_renderer = MapRenderer(self.tilemap)
        self.camera = Camera(1280, 720, 25 * 32, 20 * 32)
        
        print("Map created successfully!")
        print(self.tilemap.debug_info())
        
        # Save the generated map for reference
        self.map_builder.save_map_to_csv(self.tilemap, "generated_apartment.csv")
    
    def _load_simple_apartment(self):
        """Load a simple apartment layout"""
        self.tilemap = self.map_builder.create_simple_apartment(20, 15)
        self.map_renderer = MapRenderer(self.tilemap)
        self.camera = Camera(1280, 720, 20 * 32, 15 * 32)
        print("Simple apartment loaded!")
        print(self.tilemap.debug_info())
    
    def _load_complex_apartment(self):
        """Load a complex apartment layout"""
        self.tilemap = self.map_builder.create_complex_apartment(25, 20)
        self.map_renderer = MapRenderer(self.tilemap)
        self.camera = Camera(1280, 720, 25 * 32, 20 * 32)
        print("Complex apartment loaded!")
        print(self.tilemap.debug_info())
    
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
