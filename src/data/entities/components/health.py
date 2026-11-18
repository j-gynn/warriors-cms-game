class HealthComponent:
    name = "health"

    def __init__(self, max_health=100):
        self.max_health = max_health
        self.health = max_health
