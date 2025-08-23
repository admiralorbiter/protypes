import pygame, numpy as np

# Colors are placeholders
COLORS = {
    0: (40, 44, 52),   # empty
    1: (90, 120, 180), # housing
    2: (120, 100, 100) # factory
}

class CityExternalities:
    def __init__(self, state):
        self.state = state
        self.D = 0.08
        self.decay = 0.01
        self.tile = 16
        self.surface = pygame.Surface((state.btype.shape[1]*self.tile, state.btype.shape[0]*self.tile))

    def handle_key(self, key):
        if key == pygame.K_1: self.state.show_field = 1
        if key == pygame.K_2: self.state.show_field = 2
        if key == pygame.K_3: self.state.show_field = 3

    def update(self, dt):
        # Simple daily substep approximation
        steps = 4
        for _ in range(steps):
            self.diffuse_once(self.state.N, self.sources_N())
            self.diffuse_once(self.state.P, self.sources_P())

    def diffuse_once(self, F, S):
        # naive Laplacian
        H, W = F.shape
        L = np.zeros_like(F)
        L[1:-1,1:-1] = (F[:-2,1:-1] + F[2:,1:-1] + F[1:-1,:-2] + F[1:-1,2:] - 4*F[1:-1,1:-1])
        F += self.D * L - self.decay * F + S
        np.clip(F, 0, 255, out=F)

    def sources_N(self):
        return (self.state.btype == 2).astype('float32') * 0.5

    def sources_P(self):
        return (self.state.btype == 2).astype('float32') * 0.4

    def draw(self, screen, topleft=(0,0)):
        # Draw base tiles
        self.surface.fill((30,30,30))
        for y in range(self.state.btype.shape[0]):
            for x in range(self.state.btype.shape[1]):
                bt = int(self.state.btype[y, x])
                pygame.draw.rect(self.surface, COLORS.get(bt, (50,50,50)),
                                 (x*self.tile, y*self.tile, self.tile-1, self.tile-1))
        # Overlay field heatmap (red alpha)
        F = self.state.N if self.state.show_field == 1 else (self.state.P if self.state.show_field == 2 else self.state.T)
        for y in range(self.state.btype.shape[0]):
            for x in range(self.state.btype.shape[1]):
                v = int(min(255, F[y, x]))
                if v > 0:
                    s = pygame.Surface((self.tile-1, self.tile-1), pygame.SRCALPHA)
                    s.fill((255, 0, 0, min(180, v)))
                    self.surface.blit(s, (x*self.tile, y*self.tile))
        screen.blit(self.surface, topleft)

    def monthly_tick(self):
        pass
