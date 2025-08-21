"""
System base classes for the Entity Component System
Systems process entities with specific component combinations
"""

from abc import ABC, abstractmethod
from typing import List, Type, TypeVar, Dict, Set
from .entity import Entity
from .component import Component, Transform, Hitbox, AIState

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
    
    def __init__(self):
        super().__init__([Transform, Hitbox])
    
    def _process_entity(self, entity: Entity, dt: float):
        """Process movement for a single entity"""
        # This will be implemented when we add movement components
        pass

class RenderSystem(ComponentSystem):
    """System for rendering entities"""
    
    def __init__(self):
        super().__init__([Transform])
    
    def _process_entity(self, entity: Entity, dt: float):
        """Process rendering for a single entity"""
        # This will be implemented when we add rendering
        pass

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
