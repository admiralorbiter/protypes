class Node:
    def __init__(self, name, servers=1, mu=1.0, sigma=0.2, rule=False, tp=0.0, fp=0.0, delay=0.0):
        self.name = name
        self.servers = servers
        self.mu = mu
        self.sigma = sigma
        self.rule = rule
        self.tp = tp
        self.fp = fp
        self.delay = delay
