import pygame, time
from .state import GameState
from .systems.city_externalities import CityExternalities
from .systems.districting import Districting
from .systems.bureaucracy import Bureaucracy
from .systems.elections import Elections

FIXED_DT = 1/60  # seconds

class GameApp:
    def __init__(self, size=(1180, 760)):
        self.screen = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.state = GameState()
        # Systems
        self.city = CityExternalities(self.state)
        self.dist = Districting(self.state)
        self.bureau = Bureaucracy(self.state)
        self.elex = Elections(self.state)
        # UI mode
        self.paused = False
        self.font = pygame.font.SysFont('arial', 16)

    def run(self):
        accumulator = 0.0
        last = time.time()
        running = True
        while running:
            now = time.time()
            accumulator += now - last
            last = now
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    self.dist.handle_key(event.key)
                    self.city.handle_key(event.key)
            # Fixed-step update
            while accumulator >= FIXED_DT:
                if not self.paused:
                    self.update(FIXED_DT)
                accumulator -= FIXED_DT
            self.draw()
            self.clock.tick(60)

    def update(self, dt):
        # Update order mirrors GDD
        self.city.update(dt)
        self.bureau.update(dt)
        # Elections depend on city harms (very rough placeholder)
        self.elex.update(dt)
        self.state.month_time += dt
        if self.state.month_time >= self.state.seconds_per_month:
            self.state.month_time = 0.0
            self.state.month += 1
            if self.state.month % 12 == 0:
                self.state.year += 1
            self.city.monthly_tick()
            self.bureau.monthly_tick()
            self.elex.monthly_tick()

    def draw(self):
        self.screen.fill((20, 24, 28))
        # Map and overlays
        self.city.draw(self.screen, topleft=(12, 12))
        self.dist.draw_overlay(self.screen, topleft=(12, 12))
        self.draw_hud()
        pygame.display.flip()

    def draw_hud(self):
        hud = f"Budget: ${self.state.budget:,.0f}  Legitimacy: {self.state.legitimacy:.0f}  Majority: {self.state.majority}  Month: {self.state.month} Year: {self.state.year}"
        txt = self.font.render(hud, True, (230,230,230))
        self.screen.blit(txt, (12, 720))
