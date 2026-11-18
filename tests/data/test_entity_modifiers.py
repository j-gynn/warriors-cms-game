import unittest

from data.entities.components.hunger import HungerComponent
from simulation.simulation import Simulation


class TestEntityModifiers(unittest.TestCase):
    def test_modifiers(self):
        simulation = Simulation()
        entity, idx = simulation.spawn_entity("base.cat")

        self.assertNotEqual(simulation.hunger_system.get_modifiers(entity), 1.0)
        entity.get_component("lifecycle")


if __name__ == "__main__":
    unittest.main()
