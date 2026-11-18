from simulation.event_manager import EntityEvent


class PopulationManager:
    def __init__(self, faction):
        self.faction = faction
        self._population = {}
        self._food_demand = 0

    def get_food_demand(self):
        pass

    def on_role_change(self, event: EntityEvent):
        previous, current = event.data["previous_role"], event.data["new_role"]
