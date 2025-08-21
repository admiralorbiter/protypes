"""
Entity Manager for the Entity Component System
Coordinates all entities and systems in the game world
"""

from typing import Dict, List, Optional, Type, TypeVar
from .entity import Entity
from .system import System
from .component import Component

T = TypeVar('T', bound=Component)

class EntityManager:
    """Manages all entities and systems in the game world"""
    
    def __init__(self):
        self.entities: Dict[int, Entity] = {}
        self.systems: List[System] = []
        self.next_entity_id = 1
        self.entity_tags: Dict[str, set[int]] = {}  # tag -> set of entity IDs
    
    def create_entity(self, name: str = "") -> Entity:
        """Create a new entity with a unique ID"""
        entity = Entity(self.next_entity_id, name)
        self.entities[self.next_entity_id] = entity
        self.next_entity_id += 1
        
        # Register with all systems
        for system in self.systems:
            system.register_entity(entity)
        
        return entity
    
    def destroy_entity(self, entity_id: int):
        """Destroy an entity and remove it from all systems"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            
            # Remove from all systems
            for system in self.systems:
                system.unregister_entity(entity)
            
            # Remove from tag collections
            for tag in entity.get_tags():
                if tag in self.entity_tags:
                    self.entity_tags[tag].discard(entity_id)
            
            # Clean up entity
            entity.destroy()
            del self.entities[entity_id]
    
    def get_entity(self, entity_id: int) -> Optional[Entity]:
        """Get an entity by ID"""
        return self.entities.get(entity_id)
    
    def get_all_entities(self) -> List[Entity]:
        """Get all entities"""
        return list(self.entities.values())
    
    def get_entities_with_component(self, component_type: Type[T]) -> List[Entity]:
        """Get all entities that have a specific component type"""
        return [entity for entity in self.entities.values() 
                if entity.has_component(component_type)]
    
    def get_entities_with_tag(self, tag: str) -> List[Entity]:
        """Get all entities with a specific tag"""
        if tag in self.entity_tags:
            return [self.entities[entity_id] for entity_id in self.entity_tags[tag] 
                    if entity_id in self.entities]
        return []
    
    def add_system(self, system: System):
        """Add a system to the entity manager"""
        self.systems.append(system)
        
        # Register all existing entities with the new system
        for entity in self.entities.values():
            system.register_entity(entity)
    
    def remove_system(self, system: System):
        """Remove a system from the entity manager"""
        if system in self.systems:
            self.systems.remove(system)
    
    def update_systems(self, dt: float):
        """Update all systems"""
        for system in self.systems:
            system.update(self.entities, dt)
    
    def add_entity_tag(self, entity_id: int, tag: str):
        """Add a tag to an entity"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.add_tag(tag)
            
            # Update tag collections
            if tag not in self.entity_tags:
                self.entity_tags[tag] = set()
            self.entity_tags[tag].add(entity_id)
    
    def remove_entity_tag(self, entity_id: int, tag: str):
        """Remove a tag from an entity"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            entity.remove_tag(tag)
            
            # Update tag collections
            if tag in self.entity_tags:
                self.entity_tags[tag].discard(entity_id)
    
    def clear(self):
        """Clear all entities and systems"""
        # Clear all entities
        for entity in self.entities.values():
            entity.destroy()
        self.entities.clear()
        
        # Clear all systems
        for system in self.systems:
            system.entities.clear()
        
        # Clear tag collections
        self.entity_tags.clear()
        
        # Reset entity ID counter
        self.next_entity_id = 1
    
    def get_entity_count(self) -> int:
        """Get the total number of entities"""
        return len(self.entities)
    
    def get_system_count(self) -> int:
        """Get the total number of systems"""
        return len(self.systems)
    
    def debug_info(self) -> str:
        """Get debug information about the entity manager"""
        info = f"EntityManager: {self.get_entity_count()} entities, {self.get_system_count()} systems\n"
        
        # Entity info
        for entity_id, entity in self.entities.items():
            component_names = [comp.__class__.__name__ for comp in entity.get_components()]
            tags = list(entity.get_tags())
            info += f"  Entity {entity_id} ({entity.name}): {component_names}, tags: {tags}\n"
        
        # System info
        for system in self.systems:
            info += f"  System {system.__class__.__name__}: {len(system.entities)} entities\n"
        
        return info
