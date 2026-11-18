class PopulationManager:
    def __init__(self, faction):
        self.faction = faction
        self._population = {}

    def consume_food(self, required):
        supplied = self.faction.resources.remove("base.food", required)

        shortage = required - supplied

        if shortage > 0:
            self.handle_food_shortage()

    def handle_food_shortage(self):
        print("yo pawns gonna be dead ayo")
