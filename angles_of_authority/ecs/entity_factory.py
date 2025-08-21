"""
Entity Factory for creating common entity types
Provides easy methods to create operators, suspects, civilians, etc.
"""

from .entity_manager import EntityManager
from .entity import Entity
from .component import Transform, Hitbox, Team, FOV, AIState, Inventory, Camera, Movement

class EntityFactory:
    """Factory for creating common entity types"""
    
    def __init__(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
    
    def create_operator(self, x: float, y: float, name: str = "Operator") -> Entity:
        """Create an operator entity"""
        entity = self.entity_manager.create_entity(name)
        
        # Add components
        entity.add_component(Transform(x, y, 0.0))
        entity.add_component(Hitbox(32.0, 32.0))  # 32x32 pixel hitbox
        entity.add_component(Team(Team.OPERATOR))
        entity.add_component(FOV(70.0, 220.0))  # 70° FOV, 220px range
        entity.add_component(Inventory())
        entity.add_component(Camera(is_recording=True))
        entity.add_component(Movement(speed=120.0, max_speed=180.0))  # Fast movement for operators
        
        # Add tags
        entity.add_tag("player_controlled")
        entity.add_tag("can_move")
        entity.add_tag("can_shoot")
        
        return entity
    
    def create_suspect(self, x: float, y: float, name: str = "Suspect") -> Entity:
        """Create a suspect entity"""
        entity = self.entity_manager.create_entity(name)
        
        # Add components
        entity.add_component(Transform(x, y, 0.0))
        entity.add_component(Hitbox(32.0, 32.0))
        entity.add_component(Team(Team.SUSPECT))
        entity.add_component(FOV(65.0, 200.0))  # 65° FOV, 200px range
        entity.add_component(AIState(AIState.IDLE))
        entity.add_component(Inventory())
        
        # Add tags
        entity.add_tag("ai_controlled")
        entity.add_tag("can_move")
        entity.add_tag("can_shoot")
        entity.add_tag("hostile")
        
        return entity
    
    def create_civilian(self, x: float, y: float, name: str = "Civilian") -> Entity:
        """Create a civilian entity"""
        entity = self.entity_manager.create_entity(name)
        
        # Add components
        entity.add_component(Transform(x, y, 0.0))
        entity.add_component(Hitbox(32.0, 32.0))
        entity.add_component(Team(Team.CIVILIAN))
        entity.add_component(FOV(80.0, 180.0))  # 80° FOV, 180px range
        entity.add_component(AIState(AIState.IDLE))
        
        # Add tags
        entity.add_tag("ai_controlled")
        entity.add_tag("can_move")
        entity.add_tag("innocent")
        
        return entity
    
    def create_press_observer(self, x: float, y: float, name: str = "Press") -> Entity:
        """Create a press observer entity"""
        entity = self.entity_manager.create_entity(name)
        
        # Add components
        entity.add_component(Transform(x, y, 0.0))
        entity.add_component(Hitbox(32.0, 32.0))
        entity.add_component(Team(Team.PRESS))
        entity.add_component(FOV(100.0, 240.0))  # 100° FOV, 240px range
        entity.add_component(AIState(AIState.IDLE))
        entity.add_component(Camera(is_recording=True))
        
        # Add tags
        entity.add_tag("ai_controlled")
        entity.add_tag("can_move")
        entity.add_tag("witness")
        entity.add_tag("high_priority_viewer")
        
        return entity
    
    def create_cover_object(self, x: float, y: float, width: float, height: float, name: str = "Cover") -> Entity:
        """Create a cover object entity"""
        entity = self.entity_manager.create_entity(name)
        
        # Add components
        entity.add_component(Transform(x, y, 0.0))
        entity.add_component(Hitbox(width, height))
        
        # Add tags
        entity.add_tag("static")
        entity.add_tag("cover")
        entity.add_tag("collision")
        
        return entity
    
    def create_door(self, x: float, y: float, width: float, height: float, name: str = "Door") -> Entity:
        """Create a door entity"""
        entity = self.entity_manager.create_entity(name)
        
        # Add components
        entity.add_component(Transform(x, y, 0.0))
        entity.add_component(Hitbox(width, height))
        
        # Add tags
        entity.add_tag("static")
        entity.add_tag("door")
        entity.add_tag("collision")
        entity.add_tag("interactive")
        
        return entity
    
    def create_evidence(self, x: float, y: float, evidence_type: str, name: str = "Evidence") -> Entity:
        """Create an evidence entity"""
        entity = self.entity_manager.create_entity(name)
        
        # Add components
        entity.add_component(Transform(x, y, 0.0))
        entity.add_component(Hitbox(16.0, 16.0))  # Smaller hitbox for evidence
        entity.add_component(Inventory())  # Evidence can be collected
        
        # Add tags
        entity.add_tag("static")
        entity.add_tag("evidence")
        entity.add_tag("collectible")
        entity.add_tag(f"evidence_type_{evidence_type}")
        
        return entity
    
    def create_wall(self, x: float, y: float, width: float, height: float, name: str = "Wall") -> Entity:
        """Create a wall entity"""
        entity = self.entity_manager.create_entity(name)
        
        # Add components
        entity.add_component(Transform(x, y, 0.0))
        entity.add_component(Hitbox(width, height))
        
        # Add tags
        entity.add_tag("static")
        entity.add_tag("wall")
        entity.add_tag("collision")
        entity.add_tag("opaque")
        
        return entity
