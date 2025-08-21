"""
Entity class for the Entity Component System
Entities are containers for components and provide the interface for game logic
"""

from typing import Dict, Type, TypeVar, Optional, List
from .component import Component

T = TypeVar('T', bound=Component)

class Entity:
    """An entity in the game world, composed of multiple components"""
    
    def __init__(self, entity_id: int, name: str = ""):
        self.entity_id = entity_id
        self.name = name
        self.components: Dict[Type[Component], Component] = {}
        self.enabled = True
        self.tags: set[str] = set()
    
    def add_component(self, component: Component) -> 'Entity':
        """Add a component to this entity"""
        component_type = type(component)
        if component_type in self.components:
            raise ValueError(f"Component of type {component_type.__name__} already exists on entity {self.entity_id}")
        
        component.set_entity(self.entity_id)
        self.components[component_type] = component
        return self
    
    def remove_component(self, component_type: Type[T]) -> Optional[T]:
        """Remove a component from this entity"""
        if component_type in self.components:
            component = self.components.pop(component_type)
            component.entity_id = None
            return component
        return None
    
    def has_component(self, component_type: Type[T]) -> bool:
        """Check if entity has a specific component type"""
        return component_type in self.components
    
    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """Get a component of a specific type"""
        return self.components.get(component_type)
    
    def get_components(self) -> List[Component]:
        """Get all components on this entity"""
        return list(self.components.values())
    
    def get_enabled_components(self) -> List[Component]:
        """Get all enabled components on this entity"""
        return [comp for comp in self.components.values() if comp.enabled]
    
    def add_tag(self, tag: str):
        """Add a tag to this entity"""
        self.tags.add(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag from this entity"""
        self.tags.discard(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if entity has a specific tag"""
        return tag in self.tags
    
    def get_tags(self) -> set[str]:
        """Get all tags on this entity"""
        return self.tags.copy()
    
    def enable(self):
        """Enable this entity and all its components"""
        self.enabled = True
        for component in self.components.values():
            component.enable()
    
    def disable(self):
        """Disable this entity and all its components"""
        self.enabled = False
        for component in self.components.values():
            component.disable()
    
    def destroy(self):
        """Clean up entity and all components"""
        for component in self.components.values():
            component.entity_id = None
        self.components.clear()
        self.tags.clear()
    
    def __str__(self) -> str:
        component_names = [comp.__class__.__name__ for comp in self.components.values()]
        return f"Entity({self.entity_id}, '{self.name}', components: {component_names})"
    
    def __repr__(self) -> str:
        return self.__str__()
