from simulation.event_manager import EntityEvent


class HungerSystem:
    def __init__(self, event_manager):
        self.events = event_manager

    def update(self, simulation):
        for entity in simulation.entities.get_all():
            hunger = entity.get_component("hunger")

            if hunger is None:
                continue

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

    def get_modifiers(self, entity):
        """
        Returns the active modifier for the entity's hunger component
        """
        if not entity.has_component("hunger"):
            return 0

        modifier = 1.0

        for component in entity.components.values():
            modifier *= component.modifiers.get("hunger", {}).get("hunger_rate", 1.0)

        return modifier

    def get_requirement(self, entity):
        if not entity.has_component("hunger"):
            return 0
        return entity.get_component("hunger").hunger_rate * self.get_modifiers(entity)
