class Bureaucracy:
    def __init__(self, state):
        self.state = state
        self.backlog = 0
        self.service_rate = 3.0  # cases per month
        self.arrival_rate = 3.0

    def update(self, dt):
        pass

    def monthly_tick(self):
        arrivals = self.arrival_rate
        completions = min(self.backlog, self.service_rate)
        self.backlog += arrivals - completions
        if self.backlog > 20:
            self.state.legitimacy = max(0.0, self.state.legitimacy - 1.0)
