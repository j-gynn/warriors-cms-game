class TurnPhase:
    def __init__(self, phase_id, name, system, priority):
        self.id = phase_id
        self.name = name
        self.system = system
        self.priority = priority

    def execute(self, simulation):
        self.system.update(simulation)
