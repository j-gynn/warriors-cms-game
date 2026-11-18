from simulation.event_manager import EntityEvent


class HealthSystem:
    def __init__(self, event_manager):
        self.events = event_manager

        self.events.subscribe("health.starvation", self.on_starvation_event)
        self.events.subscribe("death", self.on_death_event)

    def update(self, simulation):
        pass

    @staticmethod
    def will_die_this_turn(health):
        return health.health <= 0

    def on_starvation_event(self, event, simulation):
        entity = simulation.entities.get(event.entity_id)
        health = entity.get_component("health")
        health.health -= event.data["health_reduce"]
        if self.will_die_this_turn(health):
            self.events.publish(
                EntityEvent(
                    "base.entity.death",
                    entity_id=entity.id,
                    data={"cause": "starvation"},
                )
            )

    def on_death_event(self, event, simulation):
        print("entity deceased lmfao")
        simulation.entities.remove(event.entity_id)
