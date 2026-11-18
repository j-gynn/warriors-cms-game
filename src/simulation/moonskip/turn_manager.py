class TurnManager:
    def __init__(self, simulation):
        self.simulation = simulation
        self.phases = {}

    def register_phase(self, phase):
        if phase.id in self.phases:
            raise ValueError(f"Phase already registered: {phase.id}")

        self.phases[phase.id] = phase

    def unregister_phase(self, phase_id):
        self.phases.pop(phase_id, None)

    def advance_turn(self):
        self.simulation.events.release_scheduled_events(self.simulation.turn_number)
        ordered_phases = sorted(self.phases.values(), key=lambda p: (p.priority, p.id))

        for phase in ordered_phases:
            phase.execute(self.simulation)
            self.simulation.events.process_events(self.simulation)

        self.simulation.turn_number += 1
