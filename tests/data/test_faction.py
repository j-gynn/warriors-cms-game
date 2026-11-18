import unittest

from simulation.event_manager import EventManager
from simulation.factions.faction import Faction


class TestFactionResources(unittest.TestCase):
    def setUp(self):
        self.events = EventManager()
        self.faction = Faction("test", self.events)

    def test_add(self):
        # given
        self.assertEqual(self.faction.resources.get_amount("base.food"), 0)

        # when
        self.faction.resources.add("base.food", 10)

        # then
        self.assertEqual(self.faction.resources.get_amount("base.food"), 10)
        # check an event was emitted
        self.assertEqual(len(self.events.queue), 1)

        self.assertRaises(ValueError, self.faction.resources.add, "base.food", -1)

    def test_remove(self):
        # given
        self.faction.resources.add("base.food", 100)
        self.assertEqual(self.faction.resources.get_amount("base.food"), 100)
        self.events.queue.clear()

        # when
        self.faction.resources.remove("base.food", 10)

        # then
        self.assertEqual(self.faction.resources.get_amount("base.food"), 90)
        # check an event was emitted
        self.assertEqual(len(self.events.queue), 1)

        self.assertRaises(ValueError, self.faction.resources.remove, "base.food", -1)

    def test_remove_partial(self):
        # given
        self.faction.resources.add("base.food", 100)
        self.assertEqual(self.faction.resources.get_amount("base.food"), 100)
        self.events.queue.clear()

        to_take = 110
        consumed = self.faction.resources.remove("base.food", to_take)
        self.assertNotEqual(consumed, to_take)
        self.assertEqual(consumed, 100)
        self.assertEqual(self.faction.resources.get_amount("base.food"), 0)
        self.assertEqual(len(self.events.queue), 1)

    def test_try_remove(self):
        # given
        self.faction.resources.add("base.food", 100)
        self.assertEqual(self.faction.resources.get_amount("base.food"), 100)

        self.assertTrue(self.faction.resources.try_remove("base.food", 100))
        self.assertFalse(self.faction.resources.try_remove("base.food", 100))
