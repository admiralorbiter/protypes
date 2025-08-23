import pygame
from game.app import GameApp

def main():
    pygame.init()
    pygame.display.set_caption('Tri-Civics (Starter)')
    app = GameApp((1180, 760))
    app.run()
    pygame.quit()

if __name__ == '__main__':
    main()
