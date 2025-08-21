"""
System base classes for the Entity Component System
Systems process entities with specific component combinations
"""

import pygame
from abc import ABC, abstractmethod
from typing import List, Type, TypeVar, Dict, Set
from .entity import Entity
from .component import Component, Transform, Hitbox, AIState, Movement, Team

T = TypeVar('T', bound=Component)

class System(ABC):
    """Base class for all systems"""
    
    def __init__(self):
        self.entities: Set[int] = set()  # Set of entity IDs this system processes
        self.enabled = True
    
    def register_entity(self, entity: Entity):
        """Register an entity with this system if it has required components"""
        if self._entity_matches_requirements(entity):
            self.entities.add(entity.entity_id)
    
    def unregister_entity(self, entity: Entity):
        """Unregister an entity from this system"""
        self.entities.discard(entity.entity_id)
    
    def enable(self):
        """Enable this system"""
        self.enabled = True
    
    def disable(self):
        """Disable this system"""
        self.enabled = False
    
    @abstractmethod
    def _entity_matches_requirements(self, entity: Entity) -> bool:
        """Check if an entity has the required components for this system"""
        pass
    
    @abstractmethod
    def update(self, entities: Dict[int, Entity], dt: float):
        """Update all registered entities"""
        pass

class ComponentSystem(System):
    """System that processes entities with specific component types"""
    
    def __init__(self, required_components: List[Type[Component]]):
        super().__init__()
        self.required_components = required_components
    
    def _entity_matches_requirements(self, entity: Entity) -> bool:
        """Check if entity has all required components"""
        return all(entity.has_component(comp_type) for comp_type in self.required_components)
    
    def get_entities_with_components(self, entities: Dict[int, Entity]) -> List[Entity]:
        """Get all entities that have the required components"""
        return [entities[entity_id] for entity_id in self.entities if entity_id in entities]
    
    def update(self, entities: Dict[int, Entity], dt: float):
        """Update all registered entities"""
        if not self.enabled:
            return
        
        matching_entities = self.get_entities_with_components(entities)
        for entity in matching_entities:
            if entity.enabled:
                self._process_entity(entity, dt)
    
    @abstractmethod
    def _process_entity(self, entity: Entity, dt: float):
        """Process a single entity (override this method)"""
        pass

class MovementSystem(ComponentSystem):
    """System for handling entity movement"""
    
    def __init__(self, tilemap=None, entity_manager=None):
        super().__init__([Transform, Movement])
        self.tilemap = tilemap
        self.entity_manager = entity_manager
    
    def set_tilemap(self, tilemap):
        """Set the tilemap for collision detection"""
        self.tilemap = tilemap
    
    def set_entity_manager(self, entity_manager):
        """Set the entity manager for entity-to-entity collision detection"""
        self.entity_manager = entity_manager
    
    def _process_entity(self, entity: Entity, dt: float):
        """Process movement for a single entity"""
        transform = entity.get_component(Transform)
        movement = entity.get_component(Movement)
        hitbox = entity.get_component(Hitbox)
        
        if not transform or not movement:
            return
        

        
        # Calculate new position
        new_x = transform.x + movement.velocity_x * dt
        new_y = transform.y + movement.velocity_y * dt
        
        # Check collision with tilemap if available
        if self.tilemap and hitbox:
            # Check X movement
            can_move_x = self._can_move_to(new_x, transform.y, hitbox)
            if can_move_x:
                transform.x = new_x
            else:
                movement.velocity_x = 0  # Stop X movement on collision
            
            # Check Y movement  
            can_move_y = self._can_move_to(transform.x, new_y, hitbox)
            if can_move_y:
                transform.y = new_y
            else:
                movement.velocity_y = 0  # Stop Y movement on collision
        else:
            # No collision detection - apply movement directly
            transform.x = new_x
            transform.y = new_y
        
        # Apply friction
        movement.apply_friction(dt)
    
    def _can_move_to(self, x: float, y: float, hitbox: Hitbox) -> bool:
        """Check if an entity can move to the given position"""
        # Check tilemap collision first
        if self.tilemap:
            # Get hitbox bounds
            half_width = hitbox.width / 2
            half_height = hitbox.height / 2
            
            # Check all four corners of the hitbox
            corners = [
                (x - half_width, y - half_height),  # Top-left
                (x + half_width, y - half_height),  # Top-right
                (x - half_width, y + half_height),  # Bottom-left
                (x + half_width, y + half_height),  # Bottom-right
            ]
            
            for corner_x, corner_y in corners:
                # Convert world coordinates to tile coordinates using the tilemap's method
                tile_x, tile_y = self.tilemap.world_to_tile(corner_x, corner_y)
                
                # Check if the tile at this position is walkable
                if not self.tilemap.is_walkable(tile_x, tile_y):
                    return False
        
        # Check entity-to-entity collision
        if self.entity_manager:
            # Get hitbox bounds for the moving entity
            half_width = hitbox.width / 2
            half_height = hitbox.height / 2
            
            # Check collision with all other entities
            for other_entity in self.entity_manager.get_all_entities():
                if other_entity.entity_id == hitbox.entity_id:  # Skip self
                    continue
                
                # Skip collision with static objects (walls, doors) - they use tilemap collision
                if other_entity.has_tag("static"):
                    continue
                    
                other_transform = other_entity.get_component(Transform)
                other_hitbox = other_entity.get_component(Hitbox)
                
                if not other_transform or not other_hitbox:
                    continue
                
                # Check if hitboxes overlap
                other_half_width = other_hitbox.width / 2
                other_half_height = other_hitbox.height / 2
                
                if self._hitboxes_overlap(
                    x, y, half_width, half_height,
                    other_transform.x, other_transform.y, 
                    other_half_width, other_half_height
                ):
                    # Debug output
                    distance_x = abs(x - other_transform.x)
                    distance_y = abs(y - other_transform.y)
                    threshold_x = (half_width + other_half_width) - 2.0
                    threshold_y = (half_height + other_half_height) - 2.0
                    print(f"COLLISION: Moving to ({x:.1f}, {y:.1f}) blocked by entity at ({other_transform.x:.1f}, {other_transform.y:.1f})")
                    print(f"  Distance: X={distance_x:.1f}, Y={distance_y:.1f}")
                    print(f"  Threshold: X={threshold_x:.1f}, Y={threshold_y:.1f}")
                    print(f"  Hitbox sizes: Moving={half_width*2:.1f}x{half_height*2:.1f}, Other={other_half_width*2:.1f}x{other_half_height*2:.1f}")
                    return False
        
        return True
    
    def _hitboxes_overlap(self, x1: float, y1: float, w1: float, h1: float,
                          x2: float, y2: float, w2: float, h2: float) -> bool:
        """Check if two hitboxes overlap"""
        # w1, h1, w2, h2 are half-widths and half-heights (radii)
        # Two circles overlap if distance between centers < sum of radii
        distance_x = abs(x1 - x2)
        distance_y = abs(y1 - y2)
        
        # Use a slightly smaller collision radius to allow entities to get closer
        collision_buffer = 2.0  # Allow entities to get within 2 pixels
        overlap_threshold_x = (w1 + w2) - collision_buffer
        overlap_threshold_y = (h1 + h2) - collision_buffer
        
        return (distance_x < overlap_threshold_x and 
                distance_y < overlap_threshold_y)

class RenderSystem(ComponentSystem):
    """System for rendering entities"""
    
    def __init__(self, screen=None, camera=None, player_controller=None):
        super().__init__([Transform])
        self.screen = screen
        self.camera = camera
        self.player_controller = player_controller
    
    def set_screen_and_camera(self, screen, camera, player_controller=None):
        """Set the screen and camera for rendering"""
        self.screen = screen
        self.camera = camera
        if player_controller:
            self.player_controller = player_controller
    
    def _process_entity(self, entity: Entity, dt: float):
        """Process rendering for a single entity"""
        if not self.screen or not self.camera:
            return
            
        transform = entity.get_component(Transform)
        
        if not transform:
            return
        
        # Convert world coordinates to screen coordinates
        screen_x, screen_y = self.camera.world_to_screen(transform.x, transform.y)
        
        # Only render if visible on screen
        if not self.camera.is_visible(transform.x, transform.y, 32, 32):
            return
        
        # Get entity color based on team/type
        color = self._get_entity_color(entity)
        
        # Draw entity as a circle (32px diameter)
        radius = 20  # Larger radius for better visibility
        pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), radius)
        
        # Draw border
        border_color = (255, 255, 255) if self._is_selected(entity) else (0, 0, 0)
        border_width = 3 if self._is_selected(entity) else 1
        pygame.draw.circle(self.screen, border_color, (int(screen_x), int(screen_y)), radius, border_width)
        
        # Draw name above entity
        if hasattr(entity, 'name') and entity.name:
            font = pygame.font.Font(None, 18)
            text = font.render(entity.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_x, screen_y - 30))
            self.screen.blit(text, text_rect)
    
    def _get_entity_color(self, entity):
        """Get color based on entity type"""
        team = entity.get_component(Team)
        
        if team:
            if team.team == Team.OPERATOR:
                return (0, 100, 255)  # Blue
            elif team.team == Team.SUSPECT:
                return (255, 50, 50)  # Red
            elif team.team == Team.CIVILIAN:
                return (100, 255, 100)  # Green
            elif team.team == Team.PRESS:
                return (255, 255, 100)  # Yellow
        
        # Default colors based on tags
        if entity.has_tag("cover"):
            return (139, 69, 19)  # Brown
        elif entity.has_tag("door"):
            return (160, 82, 45)  # Saddle brown
        elif entity.has_tag("evidence"):
            return (255, 0, 255)  # Magenta
        else:
            return (128, 128, 128)  # Gray
    
    def _is_selected(self, entity):
        """Check if entity is currently selected"""
        if self.player_controller:
            return entity == self.player_controller.get_selected_operator()
        return False

class CollisionSystem(ComponentSystem):
    """System for handling collisions between entities"""
    
    def __init__(self):
        super().__init__([Transform, Hitbox])
    
    def _process_entity(self, entity: Entity, dt: float):
        """Process collisions for a single entity"""
        # This will be implemented when we add collision detection
        pass

class AISystem(ComponentSystem):
    """System for AI behavior"""
    
    def __init__(self):
        super().__init__([AIState, Transform])
    
    def _process_entity(self, entity: Entity, dt: float):
        """Process AI for a single entity"""
        ai_state = entity.get_component(AIState)
        if ai_state:
            ai_state.update_timer(dt)
            # AI logic will be implemented later
