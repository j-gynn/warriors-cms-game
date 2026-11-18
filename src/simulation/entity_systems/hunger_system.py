from simulation.event_manager import EntityEvent


class HungerSystem:
    def __init__(self, event_manager):
        self.events = event_manager

    def update(self, simulation):
        for entity in simulation.entities.get_all():
            hunger = entity.get_component("hunger")

            if hunger is None:
                continue

            # todo implement stockpiles
            hunger.hunger += hunger.hunger_rate

            if hunger.hunger >= 80:
                self.events.publish(
                    EntityEvent(
                        "base.entity.health.starvation",
                        entity_id=entity.id,
                        data={"health_reduce": 20},
                    )
                )
            elif hunger.hunger >= 50:
                self.events.publish(
                    EntityEvent(
                        "base.entity.health.starvation",
                        entity_id=entity.id,
                        data={"health_reduce": 10},
                    )
                )
