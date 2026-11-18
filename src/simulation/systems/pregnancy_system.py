from random import randint
import logging

from simulation.event_manager import GameEvent

logger = logging.getLogger(__name__)


class PregnancySystem:
    def __init__(self, event_manager):
        self.events = event_manager

        self.events.subscribe("pregnancy.birth", self.on_birth)

    def get_pregnant(self, simulation, mother_id, father_id, definition_id):
        self.events.schedule_event(
            GameEvent(
                "pregnancy.birth",
                None,
                {
                    "mother_id": mother_id,
                    "father_id": father_id,
                    "definition": definition_id,
                    "number_of_offspring": randint(1, 3),
                },
            ),
            due_turn=simulation.turn_number + 1,
        )
        logger.debug(
            "Pregnancy initiated; mother '{0}', father '{1}'".format(
                mother_id, father_id
            )
        )

    def on_birth(self, event, simulation):
        child_idx = [0] * event.data["number_of_offspring"]

        for i in range(event.data["number_of_offspring"]):
            child, child_idx[i] = simulation.spawn_entity(event.data["definition"])
            simulation.ancestry_system.add_biological_parent(
                event.data["mother_id"], child_idx
            )
            simulation.ancestry_system.add_biological_parent(
                event.data["father_id"], child_idx
            )

        self.events.publish(
            GameEvent(
                "entity.born",
                entity_id=None,
                data={
                    "mother_id": event.data["mother_id"],
                    "father_id": event.data["father_id"],
                    "children_ids": child_idx,
                },
            )
        )

        logger.debug(
            "Pregnancy complete, added {0} offspring; mother '{1}', father '{2}'".format(
                event.data["number_of_offspring"],
                event.data["mother_id"],
                event.data["father_id"],
            )
        )
