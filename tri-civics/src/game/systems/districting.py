import pygame, numpy as np
from ..utils.metrics import compute_eg

class Districting:
    def __init__(self, state):
        self.state = state
        self.brush_id = 1
        self.font = pygame.font.SysFont('arial', 14)

    def handle_key(self, key):
        if key == pygame.K_d:
            self.brush_id = (self.brush_id % 5) + 1

    def draw_overlay(self, screen, topleft=(0,0)):
        tile = 16
        surf = pygame.Surface((self.state.district.shape[1]*tile, self.state.district.shape[0]*tile), pygame.SRCALPHA)
        # Draw borders by scanning edges
        H, W = self.state.district.shape
        for y in range(H):
            for x in range(W):
                did = int(self.state.district[y,x])
                if x+1<W and self.state.district[y,x+1] != did:
                    pygame.draw.line(surf, (255,255,255,120), (x*tile+tile-1, y*tile), (x*tile+tile-1, y*tile+tile-1))
                if y+1<H and self.state.district[y+1,x] != did:
                    pygame.draw.line(surf, (255,255,255,120), (x*tile, y*tile+tile-1), (x*tile+tile-1, y*tile+tile-1))
        # EG quick calc (toy model)
        eg = compute_eg(self.state)
        txt = self.font.render(f"EG: {eg:+.3f}", True, (240,240,240))
        surf.blit(txt, (8, 8))
        screen.blit(surf, topleft)
