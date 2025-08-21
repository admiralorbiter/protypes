"""
Test scene for development and debugging
Simple scene to verify basic infrastructure and ECS system
"""

import pygame
from core.scene import Scene
from ecs.entity_manager import EntityManager
from ecs.entity_factory import EntityFactory
from ecs.system import MovementSystem, RenderSystem, CollisionSystem, AISystem
from ecs.player_controller import PlayerController
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
        self.render_system = RenderSystem()
        self.entity_manager.add_system(self.render_system)
        self.entity_manager.add_system(CollisionSystem())
        self.entity_manager.add_system(AISystem())
        
        # Player controller
        self.player_controller = PlayerController()
        
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
        
        # Update player controller
        self.player_controller.update(dt)
        
        # Update camera
        if self.camera:
            self.camera.update(dt)
    
    def render(self, screen: pygame.Surface):
        """Render test scene"""
        # Clear screen with dark blue
        screen.fill((20, 40, 80))
        
        # Render map
        if self.map_renderer and self.camera:
            camera_offset = (self.camera.x, self.camera.y)
            self.map_renderer.render(screen, camera_offset)
            
            # Set up render system with screen and camera
            self.render_system.set_screen_and_camera(screen, self.camera, self.player_controller)
            
            # Render entities AFTER the map
            for entity in self.entity_manager.get_all_entities():
                self.render_system._process_entity(entity, 0.0)
            
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
                "WASD - Move Operator",
                "1/2 - Select Operator",
                "2 - Simple Apartment",
                "3 - Complex Apartment", 
                "4 - Player Controller Info",
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
                f"Map: {self.tilemap.width if self.tilemap else 'None'}x{self.tilemap.height if self.tilemap else 'None'} tiles",
                f"Camera: ({self.camera.x:.0f}, {self.camera.y:.0f})" if self.camera else "Camera: None",
                f"Player Controller: {self.player_controller.get_operator_count()} operators"
            ]
            
            # Add selected operator position info
            selected_op = self.player_controller.get_selected_operator()
            if selected_op:
                transform = selected_op.get_component('Transform')
                if transform:
                    ecs_info.append(f"Selected Operator: {selected_op.name} at ({transform.x:.0f}, {transform.y:.0f})")
            
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
            # Handle player controller input
            self.player_controller.handle_keydown(event.key)
            
            # Handle other game events
            if event.key == pygame.K_r:
                print("ROE toggle pressed!")
            elif event.key == pygame.K_v:
                print("Shout action!")
            elif event.key == pygame.K_f:
                print("Flashbang action!")
            elif event.key == pygame.K_2:
                print("Generating simple apartment...")
                self._load_simple_apartment()
            elif event.key == pygame.K_3:
                print("Generating complex apartment...")
                self._load_complex_apartment()
            elif event.key == pygame.K_4:
                print("Player Controller Info:")
                print(self.player_controller.get_operator_info())
        
        elif event.type == pygame.KEYUP:
            # Handle key release for movement
            self.player_controller.handle_keyup(event.key)
    
    def _load_map(self):
        """Create and load the apartment map using MapBuilder"""
        print("Creating apartment map...")
        
        # Create a complex apartment
        self.tilemap = self.map_builder.create_complex_apartment(25, 20)
        
        # Set up renderer and camera
        self.map_renderer = MapRenderer(self.tilemap)
        self.camera = Camera(1280, 720, 25 * 32, 20 * 32)
        
        # Set up camera to follow selected operator
        self._setup_camera_following()
        
        print("Map created successfully!")
        print(self.tilemap.debug_info())
        
        # Save the generated map for reference
        self.map_builder.save_map_to_csv(self.tilemap, "generated_apartment.csv")
    
    def _load_simple_apartment(self):
        """Load a simple apartment layout"""
        self.tilemap = self.map_builder.create_simple_apartment(20, 15)
        self.map_renderer = MapRenderer(self.tilemap)
        self.camera = Camera(1280, 720, 20 * 32, 15 * 32)
        self._setup_camera_following()
        print("Simple apartment loaded!")
        print(self.tilemap.debug_info())
    
    def _load_complex_apartment(self):
        """Load a complex apartment layout"""
        self.tilemap = self.map_builder.create_complex_apartment(25, 20)
        self.map_renderer = MapRenderer(self.tilemap)
        self.camera = Camera(1280, 720, 25 * 32, 20 * 32)
        self._setup_camera_following()
        print("Complex apartment loaded!")
        print(self.tilemap.debug_info())
    
    def _setup_camera_following(self):
        """Set up camera to follow the selected operator"""
        if self.player_controller.selected_operator and self.camera:
            self.camera.follow_entity(self.player_controller.selected_operator)
            print(f"Camera following: {self.player_controller.selected_operator.name}")
    
    def _create_test_entities(self):
        """Create test entities to verify ECS system"""
        # Create operators (player controlled) - position them in the center of the map
        operator1 = self.entity_factory.create_operator(320, 240, "Operator 1")  # Center of 20x15 map
        operator2 = self.entity_factory.create_operator(380, 240, "Operator 2")  # Nearby
        
        # Register operators with player controller
        self.player_controller.register_operator(operator1)
        self.player_controller.register_operator(operator2)
        
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
        
        # Re-register all entities with systems after components are added
        for entity in self.entity_manager.get_all_entities():
            self.entity_manager.re_register_entity_with_systems(entity)
        
        print(f"Created {self.entity_manager.get_entity_count()} test entities")
        print("ECS System initialized successfully!")
