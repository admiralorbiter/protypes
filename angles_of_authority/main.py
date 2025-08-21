#!/usr/bin/env python3
"""
Angles of Authority - Main Entry Point
A tactical breach & clear game with moral/legitimacy systems
"""

import sys
import pygame
from core.game_loop import GameLoop
from core.scene_manager import SceneManager
from core.input_handler import InputHandler
from scenes.test_scene import TestScene

def main():
    """Main game entry point"""
    # Initialize Pygame
    pygame.init()
    
    # Set up display
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Angles of Authority")
    
    # Initialize core systems
    input_handler = InputHandler()
    scene_manager = SceneManager()
    
    # Add test scene
    test_scene = TestScene()
    scene_manager.add_scene("test", test_scene)
    scene_manager.switch_scene("test")
    
    game_loop = GameLoop(screen, input_handler, scene_manager)
    
    try:
        # Start the game loop
        game_loop.run()
    except KeyboardInterrupt:
        print("Game interrupted by user")
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
