"""
Component base classes for the Entity Component System
Components define the data and behavior of entities
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class Component(ABC):
    """Base class for all components"""
    
    def __init__(self):
        self.entity_id: Optional[int] = None
        self.enabled: bool = True
    
    def set_entity(self, entity_id: int):
        """Set the entity this component belongs to"""
        self.entity_id = entity_id
    
    def enable(self):
        """Enable this component"""
        self.enabled = True
    
    def disable(self):
        """Disable this component"""
        self.enabled = False

class Transform(Component):
    """Position and orientation of an entity in the world"""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, rotation: float = 0.0):
        super().__init__()
        self.x = x
        self.y = y
        self.rotation = rotation  # Rotation in degrees
    
    def get_position(self) -> tuple[float, float]:
        """Get current position as (x, y) tuple"""
        return (self.x, self.y)
    
    def set_position(self, x: float, y: float):
        """Set position"""
        self.x = x
        self.y = y
    
    def move(self, dx: float, dy: float):
        """Move by delta amounts"""
        self.x += dx
        self.y += dy
    
    def get_rotation(self) -> float:
        """Get current rotation in degrees"""
        return self.rotation
    
    def set_rotation(self, rotation: float):
        """Set rotation in degrees"""
        self.rotation = rotation % 360.0
    
    def rotate(self, delta: float):
        """Rotate by delta degrees"""
        self.rotation = (self.rotation + delta) % 360.0

class Hitbox(Component):
    """Collision detection for entities"""
    
    def __init__(self, width: float = 32.0, height: float = 32.0, offset_x: float = 0.0, offset_y: float = 0.0):
        super().__init__()
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
    
    def get_rect(self, transform: Transform) -> tuple[float, float, float, float]:
        """Get collision rectangle as (x, y, width, height)"""
        x = transform.x + self.offset_x - self.width / 2
        y = transform.y + self.offset_y - self.height / 2
        return (x, y, self.width, self.height)
    
    def collides_with(self, other_hitbox: 'Hitbox', other_transform: Transform) -> bool:
        """Check if this hitbox collides with another"""
        rect1 = self.get_rect(Transform(self.entity_id, 0, 0))  # Dummy transform for calculation
        rect2 = other_hitbox.get_rect(other_transform)
        
        # Simple AABB collision detection
        return not (rect1[0] + rect1[2] < rect2[0] or 
                   rect2[0] + rect2[2] < rect1[0] or
                   rect1[1] + rect1[3] < rect2[1] or
                   rect2[1] + rect2[3] < rect1[1])

class Team(Component):
    """Team affiliation for entities"""
    
    OPERATOR = "operator"
    SUSPECT = "suspect"
    CIVILIAN = "civilian"
    PRESS = "press"
    
    def __init__(self, team: str):
        super().__init__()
        if team not in [self.OPERATOR, self.SUSPECT, self.CIVILIAN, self.PRESS]:
            raise ValueError(f"Invalid team: {team}")
        self.team = team
    
    def is_operator(self) -> bool:
        return self.team == self.OPERATOR
    
    def is_suspect(self) -> bool:
        return self.team == self.SUSPECT
    
    def is_civilian(self) -> bool:
        return self.team == self.CIVILIAN
    
    def is_press(self) -> bool:
        return self.team == self.PRESS
    
    def is_hostile_to(self, other_team: 'Team') -> bool:
        """Check if this team is hostile to another team"""
        if self.team == self.OPERATOR:
            return other_team.team == self.SUSPECT
        elif self.team == self.SUSPECT:
            return other_team.team == self.OPERATOR
        return False

class FOV(Component):
    """Field of view and vision capabilities"""
    
    def __init__(self, fov_degrees: float = 70.0, range_pixels: float = 120.0):
        super().__init__()
        self.fov_degrees = fov_degrees
        self.range_pixels = range_pixels
    
    def can_see_point(self, transform: Transform, target_x: float, target_y: float) -> bool:
        """Check if this entity can see a specific point"""
        import math
        
        # Calculate distance
        dx = target_x - transform.x
        dy = target_y - transform.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > self.range_pixels:
            return False
        
        # Calculate angle to target (in degrees)
        # atan2 returns angle in radians, convert to degrees
        target_angle = math.degrees(math.atan2(dy, dx))
        
        # Normalize to 0-360 range
        target_angle = (target_angle + 360) % 360
        
        # Calculate angle difference
        angle_diff = abs(target_angle - transform.rotation)
        
        # Handle wrapping around 360 degrees
        if angle_diff > 180.0:
            angle_diff = 360.0 - angle_diff
        
        return angle_diff <= self.fov_degrees / 2.0
    
    def get_fov_cone_points(self, transform: Transform, num_points: int = 12) -> list:
        """Get points defining the FOV cone for visualization"""
        import math
        
        points = []
        half_fov = self.fov_degrees / 2.0
        
        # Add the entity's position as the first point (cone origin)
        points.append((transform.x, transform.y))
        
        # Start angle (left edge of FOV cone)
        start_angle = transform.rotation - half_fov
        
        for i in range(num_points + 1):
            # Calculate angle for this point
            angle = start_angle + (self.fov_degrees / num_points) * i
            
            # Convert to radians
            angle_rad = math.radians(angle)
            
            # Calculate point on cone edge
            x = transform.x + math.cos(angle_rad) * self.range_pixels
            y = transform.y + math.sin(angle_rad) * self.range_pixels
            
            points.append((x, y))
        
        return points

class AIState(Component):
    """AI behavior state for non-player entities"""
    
    IDLE = "idle"
    INVESTIGATE = "investigate"
    ALERT = "alert"
    COMBAT = "combat"
    FLEE = "flee"
    SURPRISED = "surprised"
    
    def __init__(self, initial_state: str = IDLE):
        super().__init__()
        self.current_state = initial_state
        self.state_timer = 0.0
        self.target_entity_id: Optional[int] = None
        self.last_known_target_pos: Optional[tuple[float, float]] = None
    
    def change_state(self, new_state: str):
        """Change to a new AI state"""
        if new_state != self.current_state:
            self.current_state = new_state
            self.state_timer = 0.0
    
    def update_timer(self, dt: float):
        """Update the state timer"""
        self.state_timer += dt
    
    def set_target(self, entity_id: int, position: tuple[float, float]):
        """Set a target entity and its last known position"""
        self.target_entity_id = entity_id
        self.last_known_target_pos = position
    
    def clear_target(self):
        """Clear the current target"""
        self.target_entity_id = None
        self.last_known_target_pos = None

class Inventory(Component):
    """Items and equipment carried by entities"""
    
    def __init__(self):
        super().__init__()
        self.items: Dict[str, Any] = {}
        self.max_items = 10
    
    def add_item(self, item_name: str, item_data: Any) -> bool:
        """Add an item to inventory"""
        if len(self.items) >= self.max_items:
            return False
        self.items[item_name] = item_data
        return True
    
    def remove_item(self, item_name: str) -> Any:
        """Remove and return an item from inventory"""
        return self.items.pop(item_name, None)
    
    def has_item(self, item_name: str) -> bool:
        """Check if entity has a specific item"""
        return item_name in self.items
    
    def get_item(self, item_name: str) -> Any:
        """Get an item without removing it"""
        return self.items.get(item_name)
    
    def get_item_count(self) -> int:
        """Get total number of items"""
        return len(self.items)

class Camera(Component):
    """Bodycam system for operators and other recording entities"""
    
    def __init__(self, is_recording: bool = True):
        super().__init__()
        self.is_recording = is_recording
        self.recording_start_time = 0.0
        self.recorded_events = []
    
    def start_recording(self, start_time: float):
        """Start recording events"""
        self.is_recording = True
        self.recording_start_time = start_time
        self.recorded_events.clear()
    
    def stop_recording(self):
        """Stop recording events"""
        self.is_recording = False
    
    def record_event(self, event_data: dict):
        """Record an event if recording is active"""
        if self.is_recording:
            self.recorded_events.append(event_data)
    
    def get_recorded_events(self) -> list:
        """Get all recorded events"""
        return self.recorded_events.copy()

class Movement(Component):
    """Movement capabilities for entities"""
    
    def __init__(self, speed: float = 100.0, max_speed: float = 150.0):
        super().__init__()
        self.speed = speed  # Pixels per second
        self.max_speed = max_speed
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.acceleration = 400.0  # Pixels per second squared
        self.friction = 0.8  # Velocity multiplier per frame
    
    def set_velocity(self, x: float, y: float):
        """Set velocity directly"""
        self.velocity_x = max(-self.max_speed, min(self.max_speed, x))
        self.velocity_y = max(-self.max_speed, min(self.max_speed, y))
    
    def add_velocity(self, dx: float, dy: float):
        """Add to current velocity"""
        self.velocity_x = max(-self.max_speed, min(self.max_speed, self.velocity_x + dx))
        self.velocity_y = max(-self.max_speed, min(self.max_speed, self.velocity_y + dy))
    
    def apply_friction(self, dt: float):
        """Apply friction to slow down movement"""
        self.velocity_x *= self.friction ** dt
        self.velocity_y *= self.friction ** dt
        
        # Stop very small velocities
        if abs(self.velocity_x) < 1.0:
            self.velocity_x = 0.0
        if abs(self.velocity_y) < 1.0:
            self.velocity_y = 0.0
    
    def get_velocity(self) -> tuple[float, float]:
        """Get current velocity as (x, y) tuple"""
        return (self.velocity_x, self.velocity_y)
    
    def is_moving(self) -> bool:
        """Check if entity is currently moving"""
        return abs(self.velocity_x) > 1.0 or abs(self.velocity_y) > 1.0
