from atexit import register

from data.entities.entity_factory import EntityFactory
from data.entities.entity_registry import EntityRegistry
from data.entities.component_registry import COMPONENT_REGISTRY
from data.definitions.definition_loader import load_definitions
from data.social.family_graph import FamilyGraph
from data.social.relationship_graph import RelationshipGraph
from simulation.event_manager import EventManager
from simulation.moonskip.default_turn_phases import register_default_phases
from simulation.moonskip.turn_manager import TurnManager
from simulation.systems.ancestry_system import AncestrySystem
from simulation.systems.health_system import HealthSystem
from simulation.systems.hunger_system import HungerSystem
from simulation.systems.lifecycle_system import LifeCycleSystem
from simulation.systems.pregnancy_system import PregnancySystem
from simulation.systems.time_system import TimeSystem


class Simulation:
    def __init__(self, turn_number=0):
        self.turn_number = turn_number
        self.turn_manager = TurnManager(self)
        self.events = EventManager()
        self.ui_events = EventManager()  # for stories, patrols, etc.

        self.entity_definitions = load_definitions("entities")
        self.entities = EntityRegistry()

        self.relationships = RelationshipGraph()
        self._family_graph = FamilyGraph()

        self.hunger_system = HungerSystem(self.events)
        self.health_system = HealthSystem(self.events)
        self.lifecycle_system = LifeCycleSystem(self.events)
        self.ancestry_system = AncestrySystem(self.events, self._family_graph)
        self.pregnancy_system = PregnancySystem(self.events)

        register_default_phases(self)

        self.entity_factory = EntityFactory(
            definitions=self.entity_definitions,
            lifecycles=self.lifecycle_system.lifecycle_definitions,
            component_registry=COMPONENT_REGISTRY,
        )

    def spawn_entity(self, definition_id):
        entity = self.entity_factory.create(definition_id)

        index = self.entities.add(entity)

        return entity, index

    def advance_turn(self):
        self.turn_manager.advance_turn()
