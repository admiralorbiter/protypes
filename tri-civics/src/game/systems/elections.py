class Elections:
    def __init__(self, state):
        self.state = state
        self.cooldown = 12  # months to election check

    def update(self, dt):
        pass

    def monthly_tick(self):
        self.cooldown -= 1
        harm = (self.state.N.mean() + self.state.P.mean()) / 2.0
        if harm > 10:
            self.state.legitimacy = max(0, self.state.legitimacy - 0.5)
        if self.cooldown <= 0:
            self.cooldown = 12
            if self.state.legitimacy > 55:
                self.state.majority = "Reform"
            elif self.state.legitimacy < 45:
                self.state.majority = "Opposition"
            else:
                self.state.majority = "Neutral"
