"""
Test scene for development and debugging
Simple scene to verify basic infrastructure and ECS system
"""

import pygame
from core.scene import Scene
from ecs.entity import Entity
from ecs.component import Transform, FOV, Team, Movement, Hitbox
from ecs.entity_manager import EntityManager
from ecs.entity_factory import EntityFactory
from ecs.system import MovementSystem, RenderSystem, CollisionSystem, AISystem, VisionSystem
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
        self.movement_system = MovementSystem()
        self.entity_manager.add_system(self.movement_system)
        
        # Create vision system and add it
        self.vision_system = VisionSystem()
        self.entity_manager.add_system(self.vision_system)
        
        # Create render system with vision system reference
        self.render_system = RenderSystem(vision_system=self.vision_system)
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
        
        # Load map first
        self._load_map()
        
        # Create test entities after map is loaded
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
        
        # Update player controller
        self.player_controller.update(dt)
        
        # Update camera
        if self.camera:
            self.camera.update(dt)
    
    def render(self, screen: pygame.Surface):
        """Render test scene"""
        # Clear screen with dark blue
        screen.fill((20, 40, 80))
        
        if not self.map_renderer:
            return
            
        # UNIFIED RENDERING SYSTEM
        # All rendering uses the same coordinate system transformation
        
        # 1. Calculate camera offset (world position that appears at screen center)
        screen_width, screen_height = screen.get_size()
        
        # Camera target position (what we want to center on screen)
        camera_target_x = 160  # Center of 10x10 map (320/2)
        camera_target_y = 160  # Center of 10x10 map (320/2)
        
        # Calculate offset to center the target on screen
        camera_offset_x = camera_target_x - screen_width // 2
        camera_offset_y = camera_target_y - screen_height // 2
        
        # 2. Render map with this offset
        self.map_renderer.render(screen, (camera_offset_x, camera_offset_y))
        
        # 3. Render entities with the SAME offset
        for entity in self.entity_manager.get_all_entities():
            transform = entity.get_component(Transform)
            if transform:
                # Convert world coordinates to screen coordinates using the SAME offset
                screen_x = transform.x - camera_offset_x
                screen_y = transform.y - camera_offset_y
                
                # Only render if visible on screen
                if -50 <= screen_x <= screen_width + 50 and -50 <= screen_y <= screen_height + 50:
                    self._render_entity(screen, entity, screen_x, screen_y)
        
        # 4. Render FOV cones after all entities
        self._render_fov_cones(screen, camera_offset_x, camera_offset_y)
        
        # Render minimap
        minimap_rect = pygame.Rect(10, 10, 150, 100)
        self.map_renderer.render_minimap(screen, minimap_rect)
        
        if self.font:
            # Render UI panel on the right side
            self._render_ui_panel(screen)
    
    def handle_event(self, event):
        """Handle events in test scene"""
        if event.type == pygame.KEYDOWN:
            # Handle player controller input
            self.player_controller.handle_keydown(event.key)
            
            # Handle other game events
            if event.key == pygame.K_r:
                print("ROE toggle pressed!")
            elif event.key == pygame.K_v:
                print("Testing vision system...")
                self._test_vision_system()
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
            elif event.key == pygame.K_q:
                self._rotate_selected_operator(-45)  # Rotate left
            elif event.key == pygame.K_e:
                self._rotate_selected_operator(45)   # Rotate right
        
        elif event.type == pygame.KEYUP:
            # Handle key release for movement
            self.player_controller.handle_keyup(event.key)
    
    def _load_map(self):
        """Create and load the apartment map using MapBuilder"""
        print("Creating simple test map...")
        
        # Create a minimal test map with guaranteed open space
        self.tilemap = self._create_simple_test_map()
        
        # Set up renderer and camera
        self.map_renderer = MapRenderer(self.tilemap)
        # Create camera with proper world bounds (10x10 tiles = 320x320 pixels)
        # Set world size larger than map to allow proper positioning
        self.camera = Camera(1280, 720, 1280, 720)
        # Center camera on the map center (160, 160)
        self.camera.center_on(160, 160)
        
        # Set up movement system with tilemap and entity_manager for collision detection
        self.movement_system.set_tilemap(self.tilemap)
        self.movement_system.set_entity_manager(self.entity_manager)
        
        # Set up vision system with tilemap for line-of-sight calculations
        self.vision_system.set_tilemap(self.tilemap)
        
        # Set up camera to follow selected operator
        self._setup_camera_following()
        
        # Debug: Print camera and map information
        print(f"Camera position: ({self.camera.x:.1f}, {self.camera.y:.1f})")
        print(f"Map size: {self.tilemap.width}x{self.tilemap.height} tiles = {self.tilemap.width*32}x{self.tilemap.height*32} pixels")
        print(f"Map center should be at: ({self.tilemap.width*16:.1f}, {self.tilemap.height*16:.1f})")
        
        print("Map created successfully!")
        print(self.tilemap.debug_info())
        
        # Save the generated map for reference
        self.map_builder.save_map_to_csv(self.tilemap, "generated_apartment.csv")
    
    def _load_simple_apartment(self):
        """Load a simple apartment layout"""
        self.tilemap = self.map_builder.create_simple_apartment(20, 15)
        self.map_renderer = MapRenderer(self.tilemap)
        # Center camera on the map (20x15 tiles = 640x480 pixels)
        self.camera = Camera(1280, 720, 1280, 720)
        self.camera.center_on(320, 240)  # Center of 20x15 map
        self.movement_system.set_tilemap(self.tilemap)
        self.movement_system.set_entity_manager(self.entity_manager)
        
        # Set up vision system with tilemap for line-of-sight calculations
        self.vision_system.set_tilemap(self.tilemap)
        
        # Reposition all entities on the new map
        self._reposition_entities_on_map()
        
        self._setup_camera_following()
        print("Simple apartment loaded!")
        print(self.tilemap.debug_info())
    
    def _load_complex_apartment(self):
        """Load a complex apartment layout"""
        self.tilemap = self.map_builder.create_complex_apartment(25, 20)
        self.map_renderer = MapRenderer(self.tilemap)
        # Center camera on the map (25x20 tiles = 800x640 pixels)
        self.camera = Camera(1280, 720, 1280, 720)
        self.camera.center_on(400, 320)  # Center of 25x20 map
        self.movement_system.set_tilemap(self.tilemap)
        self.movement_system.set_entity_manager(self.entity_manager)
        
        # Set up vision system with tilemap for line-of-sight calculations
        self.vision_system.set_tilemap(self.tilemap)
        
        # Reposition all entities on the new map
        self._reposition_entities_on_map()
        
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
        # Create operators (player controlled) - position them on walkable floor tiles
        # Find guaranteed walkable positions using the tilemap
        if not self.tilemap:
            print("ERROR: No tilemap available for entity positioning!")
            return
            
        # Find ALL walkable floor tiles first, then spread entities strategically
        all_walkable_positions = []
        for y in range(self.tilemap.height):
            for x in range(self.tilemap.width):
                if self.tilemap.is_walkable(x, y):
                    world_x, world_y = self.tilemap.tile_to_world(x, y)
                    all_walkable_positions.append((world_x, world_y, x, y))  # Include tile coords for spacing
        
        # Select spread-out positions to avoid clustering
        walkable_positions = self._select_spread_positions(all_walkable_positions, 10)
        
        print(f"Found {len(walkable_positions)} walkable positions")
        print("First 5 walkable positions:")
        for i, (x, y) in enumerate(walkable_positions[:5]):
            print(f"  Position {i}: ({x:.1f}, {y:.1f})")
        
        # Create operators at walkable positions
        if len(walkable_positions) >= 2:
            operator1 = self.entity_factory.create_operator(walkable_positions[0][0], walkable_positions[0][1], "Operator 1")
            operator2 = self.entity_factory.create_operator(walkable_positions[1][0], walkable_positions[1][1], "Operator 2")
            print(f"Operators positioned at: ({walkable_positions[0][0]:.1f}, {walkable_positions[0][1]:.1f}) and ({walkable_positions[1][0]:.1f}, {walkable_positions[1][1]:.1f})")
            
            # Debug: Check what these positions look like in tile coordinates
            tile1_x, tile1_y = self.tilemap.world_to_tile(walkable_positions[0][0], walkable_positions[0][1])
            tile2_x, tile2_y = self.tilemap.world_to_tile(walkable_positions[1][0], walkable_positions[1][1])
            print(f"Operators at tile positions: ({tile1_x}, {tile1_y}) and ({tile2_x}, {tile2_y})")
        else:
            print("ERROR: Not enough walkable positions for operators!")
            return
        
        # Register operators with player controller
        self.player_controller.register_operator(operator1)
        self.player_controller.register_operator(operator2)
        
        # Create other entities at walkable positions
        if len(walkable_positions) >= 8:
            suspect = self.entity_factory.create_suspect(walkable_positions[2][0], walkable_positions[2][1], "Suspect 1")
            civilian = self.entity_factory.create_civilian(walkable_positions[3][0], walkable_positions[3][1], "Civilian 1")
            press = self.entity_factory.create_press_observer(walkable_positions[4][0], walkable_positions[4][1], "Press 1")
            
            # Create cover objects at walkable positions
            cover1 = self.entity_factory.create_cover_object(walkable_positions[5][0], walkable_positions[5][1], 64, 32, "Cover 1")
            cover2 = self.entity_factory.create_cover_object(walkable_positions[6][0], walkable_positions[6][1], 48, 48, "Cover 2")
            
            # Create door at walkable position
            door = self.entity_factory.create_door(walkable_positions[7][0], walkable_positions[7][1], 32, 64, "Door 1")
            
            # Create evidence and wall at walkable positions
            if len(walkable_positions) >= 10:
                evidence = self.entity_factory.create_evidence(walkable_positions[8][0], walkable_positions[8][1], "weapon", "Gun")
                wall = self.entity_factory.create_wall(walkable_positions[9][0], walkable_positions[9][1], 128, 32, "Wall 1")
            else:
                evidence = self.entity_factory.create_evidence(400, 272, "weapon", "Gun")
                wall = self.entity_factory.create_wall(464, 304, 128, 32, "Wall 1")
        else:
            # Fallback positions if not enough walkable tiles
            suspect = self.entity_factory.create_suspect(144, 144, "Suspect 1")
            civilian = self.entity_factory.create_civilian(176, 176, "Civilian 1")
            press = self.entity_factory.create_press_observer(208, 112, "Press 1")
            cover1 = self.entity_factory.create_cover_object(272, 208, 64, 32, "Cover 1")
            cover2 = self.entity_factory.create_cover_object(336, 176, 48, 48, "Cover 2")
            door = self.entity_factory.create_door(304, 112, 32, 64, "Door 1")
            evidence = self.entity_factory.create_evidence(400, 272, "weapon", "Gun")
            wall = self.entity_factory.create_wall(464, 304, 128, 32, "Wall 1")
        
        # Re-register all entities with systems after components are added
        for entity in self.entity_manager.get_all_entities():
            self.entity_manager.re_register_entity_with_systems(entity)
        
        print(f"Created {self.entity_manager.get_entity_count()} test entities")
        
        # Debug: Check what components each entity has
        fov_count = len([e for e in self.entity_manager.get_all_entities() if e.has_component(FOV)])
        print(f"Created {self.entity_manager.get_entity_count()} test entities ({fov_count} with FOV)")
        print("ECS System initialized successfully!")
    
    def _render_ui_panel(self, screen: pygame.Surface):
        """Render UI panel on the right side of the screen"""
        screen_width, screen_height = screen.get_size()
        
        # Calculate panel dimensions and position
        panel_width = 300
        panel_x = screen_width - panel_width - 20
        panel_y = 20
        panel_height = screen_height - 40
        
        # Draw semi-transparent background panel
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))  # Black with 180/255 alpha
        pygame.draw.rect(panel_surface, (100, 100, 100), (0, 0, panel_width, panel_height), 2)  # Border
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Render content
        content_x = panel_x + 15
        content_y = panel_y + 15
        line_height = 25
        
        # Title
        title_font = pygame.font.Font(None, 28)
        title_text = title_font.render("GAME CONTROLS", True, (255, 255, 255))
        screen.blit(title_text, (content_x, content_y))
        content_y += line_height + 10
        
        # Controls section
        controls_font = pygame.font.Font(None, 20)
        controls = [
            "WASD - Move Operator",
            "1/2 - Select Operator", 
            "Q/E - Rotate Operator",
            "V - Test Vision System",
            "2 - Simple Apartment",
            "3 - Complex Apartment",
            "4 - Player Info",
            "F - Flashbang",
            "K - Kick Door",
            "C - Cuff",
            "X - Secure Evidence",
            "R - Toggle ROE"
        ]
        
        for control in controls:
            control_text = controls_font.render(control, True, (200, 200, 200))
            screen.blit(control_text, (content_x, content_y))
            content_y += line_height
        
        content_y += 10
        
        # Game info section
        info_font = pygame.font.Font(None, 18)
        info_title = info_font.render("GAME STATUS", True, (255, 255, 255))
        screen.blit(info_title, (content_x, content_y))
        content_y += line_height + 5
        
        # ECS info
        ecs_info = [
            f"Counter: {self.counter:.1f}",
            f"Entities: {self.entity_manager.get_entity_count()}",
            f"Systems: {self.entity_manager.get_system_count()}",
            f"Map: {self.tilemap.width if self.tilemap else 'None'}x{self.tilemap.height if self.tilemap else 'None'}",
            f"Operators: {self.player_controller.get_operator_count()}"
        ]
        
        for info in ecs_info:
            info_text = info_font.render(info, True, (180, 180, 180))
            screen.blit(info_text, (content_x, content_y))
            content_y += line_height
        
        # Vision system info
        if self.vision_system:
            content_y += 5
            fov_entities = [e for e in self.entity_manager.get_all_entities() if e.has_component(FOV)]
            vision_text = info_font.render(f"FOV Entities: {len(fov_entities)}", True, (180, 180, 180))
            screen.blit(vision_text, (content_x, content_y))
            content_y += line_height
        
        # Selected operator info
        selected_op = self.player_controller.get_selected_operator()
        if selected_op:
            content_y += 5
            transform = selected_op.get_component(Transform)
            if transform:
                op_info = [
                    f"Selected: {selected_op.name}",
                    f"Position: ({transform.x:.0f}, {transform.y:.0f})",
                    f"Rotation: {transform.rotation:.0f}°"
                ]
                for info in op_info:
                    info_text = info_font.render(info, True, (150, 200, 255))
                    screen.blit(info_text, (content_x, content_y))
                    content_y += line_height
    
    def _render_entity(self, screen: pygame.Surface, entity: Entity, screen_x: float, screen_y: float):
        """Render a single entity at screen coordinates"""
        # Get entity color based on team/type
        color = self._get_entity_color(entity)
        
        # Draw entity as a circle
        radius = 20  # Larger radius for better visibility
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), radius)
        
        # Draw border
        border_color = (255, 255, 255) if self._is_selected(entity) else (0, 0, 0)
        border_width = 3 if self._is_selected(entity) else 1
        pygame.draw.circle(screen, border_color, (int(screen_x), int(screen_y)), radius, border_width)
        
        # Draw name above entity
        if hasattr(entity, 'name') and entity.name:
            font = pygame.font.Font(None, 18)
            text = font.render(entity.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(int(screen_x), int(screen_y - 30)))
            screen.blit(text, text_rect)
    
    def _get_entity_color(self, entity: Entity):
        """Get color for entity based on type"""
        if hasattr(entity, 'name'):
            if 'Operator' in entity.name:
                return (0, 100, 255)  # Blue for operators
            elif 'Suspect' in entity.name:
                return (255, 0, 0)    # Red for suspects
            elif 'Civilian' in entity.name:
                return (0, 255, 0)    # Green for civilians
            elif 'Press' in entity.name:
                return (255, 255, 0)  # Yellow for press
            elif 'Cover' in entity.name:
                return (139, 69, 19)  # Brown for cover
            elif 'Door' in entity.name:
                return (160, 82, 45)  # Saddle brown for doors
            elif 'Gun' in entity.name:
                return (255, 0, 255)  # Magenta for weapons
            elif 'Wall' in entity.name:
                return (128, 128, 128)  # Gray for walls
        return (255, 255, 255)  # White for unknown
    
    def _is_selected(self, entity: Entity) -> bool:
        """Check if entity is selected"""
        return (self.player_controller and 
                self.player_controller.selected_operator and 
                self.player_controller.selected_operator.entity_id == entity.entity_id)
    
    def _select_spread_positions(self, all_positions, max_count):
        """Select spread-out positions from all available walkable positions"""
        if len(all_positions) <= max_count:
            return [(x, y) for x, y, tx, ty in all_positions]
        
        # Use a simple spreading algorithm
        selected = []
        # Adjust minimum distance based on map size - smaller maps need smaller distances
        map_area = self.tilemap.width * self.tilemap.height if self.tilemap else 100
        if map_area <= 100:  # Small maps (10x10 or smaller)
            min_distance = 1
        elif map_area <= 300:  # Medium maps (20x15 or similar)
            min_distance = 2  
        else:  # Large maps
            min_distance = 3
        
        # Always start with the first position
        if all_positions:
            selected.append((all_positions[0][0], all_positions[0][1]))
            
        # Try to find positions with good spacing
        for world_x, world_y, tile_x, tile_y in all_positions[1:]:
            if len(selected) >= max_count:
                break
                
            # Check if this position is far enough from all selected positions
            too_close = False
            for sel_x, sel_y in selected:
                # Convert selected world coords back to tile coords for distance check
                sel_tile_x, sel_tile_y = self.tilemap.world_to_tile(sel_x, sel_y)
                distance = abs(tile_x - sel_tile_x) + abs(tile_y - sel_tile_y)  # Manhattan distance
                if distance < min_distance:
                    too_close = True
                    break
            
            if not too_close:
                selected.append((world_x, world_y))
        
        # If we don't have enough spread positions, fill with remaining positions
        if len(selected) < max_count:
            for world_x, world_y, tile_x, tile_y in all_positions:
                if len(selected) >= max_count:
                    break
                if (world_x, world_y) not in selected:
                    selected.append((world_x, world_y))
        
        print(f"Selected {len(selected)} spread-out positions from {len(all_positions)} total walkable positions")
        return selected
    
    def _reposition_entities_on_map(self):
        """Reposition all existing entities on the current map with good spacing"""
        if not self.tilemap:
            print("ERROR: No tilemap available for entity repositioning!")
            return
            
        # Get all existing entities
        all_entities = self.entity_manager.get_all_entities()
        if not all_entities:
            return
            
        # Find all walkable positions on the current map
        all_walkable_positions = []
        for y in range(self.tilemap.height):
            for x in range(self.tilemap.width):
                if self.tilemap.is_walkable(x, y):
                    world_x, world_y = self.tilemap.tile_to_world(x, y)
                    all_walkable_positions.append((world_x, world_y, x, y))
        
        # Select spread-out positions for all entities
        entity_count = len(all_entities)
        spread_positions = self._select_spread_positions(all_walkable_positions, entity_count)
        
        # Reposition each entity
        for i, entity in enumerate(all_entities):
            if i < len(spread_positions):
                transform = entity.get_component(Transform)
                if transform:
                    new_x, new_y = spread_positions[i]
                    transform.x = new_x
                    transform.y = new_y
                    print(f"Repositioned {getattr(entity, 'name', f'Entity {entity.entity_id}')} to ({new_x:.1f}, {new_y:.1f})")
        
        print(f"Repositioned {len(all_entities)} entities on the new map")
    
    def _test_vision_system(self):
        """Test the vision system by checking what entities can see"""
        if not self.vision_system:
            print("Vision system not available!")
            return
        
        all_entities = self.entity_manager.get_all_entities()
        fov_entities = [e for e in all_entities if e.has_component(FOV)]
        
        print(f"Vision Test: {len(fov_entities)} entities with FOV")
        
        for viewer in fov_entities:
            viewer_name = getattr(viewer, 'name', f'Entity {viewer.entity_id}')
            viewer_transform = viewer.get_component(Transform)
            
            if not viewer_transform:
                continue
            
            # Get visible entities
            visible = self.vision_system.get_visible_entities(viewer, all_entities)
            
            if visible:
                print(f"  {viewer_name}: Can see {len(visible)} entities")
            else:
                print(f"  {viewer_name}: Cannot see any entities")
    
    def _rotate_selected_operator(self, delta_degrees: float):
        """Rotate the selected operator to test FOV system"""
        selected_op = self.player_controller.get_selected_operator()
        if not selected_op:
            print("No operator selected!")
            return
        
        transform = selected_op.get_component(Transform)
        if not transform:
            print("Selected operator has no transform component!")
            return
        
        old_rotation = transform.rotation
        transform.rotate(delta_degrees)
        new_rotation = transform.rotation
        
        print(f"Rotated {getattr(selected_op, 'name', 'Operator')}: {old_rotation:.0f}° → {new_rotation:.0f}°")
        
        # Test vision immediately after rotation
        self._test_vision_system()
    
    def _render_fov_cones(self, screen: pygame.Surface, camera_offset_x: float, camera_offset_y: float):
        """Render FOV cones for all entities with FOV components"""
        if not self.vision_system:
            return
        
        fov_entities = [e for e in self.entity_manager.get_all_entities() if e.has_component(FOV)]
        
        for entity in fov_entities:
            transform = entity.get_component(Transform)
            if not transform:
                continue
            
            # Get FOV cone points
            fov = entity.get_component(FOV)
            cone_points = fov.get_fov_cone_points(transform)
            
            if len(cone_points) < 3:
                continue
            
            # Convert world coordinates to screen coordinates
            screen_cone_points = []
            for world_x, world_y in cone_points:
                screen_x = world_x - camera_offset_x
                screen_y = world_y - camera_offset_y
                screen_cone_points.append((int(screen_x), int(screen_y)))
            
            # Draw FOV cone (semi-transparent)
            # Create a polygon from the cone points
            cone_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            
            # Draw the cone with semi-transparent color
            cone_color = (255, 255, 0, 30)  # Yellow with 30/255 alpha
            pygame.draw.polygon(cone_surface, cone_color, screen_cone_points)
            
            # Draw cone outline
            outline_color = (255, 255, 0, 100)  # Yellow with 100/255 alpha
            pygame.draw.lines(cone_surface, outline_color, False, screen_cone_points, 2)
            
            # Blit the cone surface onto the screen
            screen.blit(cone_surface, (0, 0))
    
    def _create_simple_test_map(self):
        """Create a simple test map with guaranteed open space"""
        from maps.tilemap import Tilemap, TileType
        
        # Create a 10x10 map with mostly floor tiles
        width, height = 10, 10
        tilemap = Tilemap(width, height)
        
        # Fill with floor tiles
        for y in range(height):
            for x in range(width):
                tilemap.set_tile(x, y, TileType.FLOOR)
        
        # Add a few walls around the edges for testing
        for x in range(width):
            tilemap.set_tile(x, 0, TileType.WALL)  # Top edge
            tilemap.set_tile(x, height-1, TileType.WALL)  # Bottom edge
        
        for y in range(height):
            tilemap.set_tile(0, y, TileType.WALL)  # Left edge
            tilemap.set_tile(width-1, y, TileType.WALL)  # Right edge
        
        # Add a few internal walls for testing collision
        tilemap.set_tile(3, 3, TileType.WALL)
        tilemap.set_tile(6, 6, TileType.WALL)
        
        print(f"Created simple test map: {width}x{height} tiles")
        print("Map layout:")
        for y in range(height):
            row = ""
            for x in range(width):
                if tilemap.get_tile(x, y).tile_type == TileType.FLOOR:
                    row += "."
                else:
                    row += "#"
            print(f"  {row}")
        return tilemap
