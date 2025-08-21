"""
Scene management system for Angles of Authority
Handles switching between different game states (Game, AAR, Menu)
"""

class SceneManager:
    """Manages different game scenes and their transitions"""
    
    def __init__(self):
        self.scenes = {}
        self.current_scene_name = None
        self.scene_stack = []
    
    def add_scene(self, name: str, scene):
        """Add a scene to the manager"""
        self.scenes[name] = scene
    
    def switch_scene(self, name: str):
        """Switch to a different scene"""
        if name in self.scenes:
            self.current_scene_name = name
            self.scenes[name].on_enter()
    
    def push_scene(self, name: str):
        """Push a scene onto the stack (for overlays)"""
        if name in self.scenes:
            if self.current_scene_name:
                self.scene_stack.append(self.current_scene_name)
            self.current_scene_name = name
            self.scenes[name].on_enter()
    
    def pop_scene(self):
        """Pop the top scene from the stack"""
        if self.scene_stack:
            self.current_scene_name = self.scene_stack.pop()
            self.scenes[self.current_scene_name].on_enter()
    
    def get_current_scene(self):
        """Get the currently active scene"""
        if self.current_scene_name and self.current_scene_name in self.scenes:
            return self.scenes[self.current_scene_name]
        return None
    
    def get_current_scene_name(self):
        """Get the name of the currently active scene"""
        return self.current_scene_name
