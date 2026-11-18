from data.definitions.definition_loader import load_definitions
from simulation.event_manager import GameEvent


class LifeCycleSystem:
    lifecycle_definitions = load_definitions("lifecycles")

    def __init__(self, event_manager):
        self.events = event_manager

    def update(self, simulation):
        for entity in simulation.entities.get_all():
            lifecycle = entity.get_component("lifecycle")

            if lifecycle is None:
                continue

            current_stage_data = (
                self.lifecycle_definitions.get(lifecycle.lifecycle, {})
                .get("stages", {})
                .get(lifecycle.stage_id)
            )

            if not current_stage_data:
                raise ValueError(
                    "Entity '{0}' has an unrecognised life stage '{1}'".format(
                        entity.id, lifecycle.stage_id
                    )
                )

            lifecycle.time_in_stage += 1
            if current_stage_data["next_stage"] is None:
                # oldest and scrunkliest age possible

                # todo: implement death by old age
                continue

            min_age, max_age = current_stage_data["duration"]
            if min_age <= lifecycle.time_in_stage <= max_age:
                # todo: add variability in when they age up?
                self.events.publish(
                    GameEvent("next_lifecycle_stage", entity_id=entity.id)
                )
                lifecycle.stage_id = current_stage_data["next_stage"]
                lifecycle.time_in_stage = 0
