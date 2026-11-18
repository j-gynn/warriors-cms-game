from typing import TYPE_CHECKING

from simulation.factions.population import PopulationManager
from simulation.factions.resources import ResourceManager

if TYPE_CHECKING:
    from simulation.event_manager import EventManager


class Faction:
    def __init__(self, faction_id, event_manager):
        self.id = faction_id
        self.events: "EventManager" = event_manager
        self.resources = ResourceManager(self)
        self.population = PopulationManager(self)
