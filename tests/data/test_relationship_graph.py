import unittest

import numpy as np
from numpy.testing import assert_array_equal

from data.social.relationship_graph import RelationshipGraph


class TestRelationshipGraph(unittest.TestCase):
    def setUp(self):
        self.graph = RelationshipGraph()

    def test_pair_key(self):
        # given
        entity = 1
        entity2 = 2

        big_number = 2**32

        # raises
        self.assertRaises(ValueError, self.graph.pair_key, a=entity, b=entity)
        self.assertRaises(OverflowError, self.graph.pair_key, a=big_number, b=entity)
        self.assertRaises(OverflowError, self.graph.pair_key, a=entity, b=big_number)

        # gives a value
        key = self.graph.pair_key(entity, entity2)
        reverse_key = self.graph.pair_key(entity2, entity)

        # confirm the keys are the same
        self.assertEqual(key, reverse_key)

    def test_get_or_create_index(self):
        # starting with an empty dictionary
        self.assertDictEqual(self.graph.lookup, {})
        idx = self.graph.get_or_create_index(1, 0)

        # should only create once
        self.assertEqual(self.graph.get_or_create_index(1, 0), idx)
        self.assertEqual(self.graph.relationship_count, 1)

        # canonizes to smallest first
        assert_array_equal(self.graph.endpoints[idx], (0, 1))

    def test_grow(self):
        self.graph = RelationshipGraph(initial_capacity=2)
        self.assertEqual(self.graph.capacity, 2)
        self.graph.get_or_create_index(0, 1)
        self.graph.get_or_create_index(1, 2)
        self.assertEqual(self.graph.capacity, 2)
        self.graph.get_or_create_index(2, 3)
        self.assertEqual(self.graph.capacity, 4)

    def test_get_metrics(self):
        # trying to get an invalid relationship returns None
        self.assertIsNone(self.graph.get_metrics(0, 1))

        # create some relationships
        self.graph.get_or_create_index(0, 1)
        self.assertEqual(self.graph.relationship_count, 1)

        assert_array_equal(self.graph.get_metrics(0, 1), (0, 0, 0))

    def test_set_metrics(self):
        # create a relationship
        self.graph.get_or_create_index(0, 1)
        self.assertEqual(self.graph.relationship_count, 1)

        # throw out invalid metrics
        self.assertRaises(
            ValueError, self.graph.set_metric, observer=0, target=1, metric=-1, value=20
        )

        # throw out invalid values
        self.assertRaises(
            ValueError,
            self.graph.set_metric,
            observer=0,
            target=1,
            metric=0,
            value=-101,
        )
        self.assertRaises(
            ValueError,
            self.graph.set_metric,
            observer=0,
            target=1,
            metric=0,
            value=101,
        )

        # confirm that a change happens, and that it happens only to observer's side
        self.graph.set_metric(observer=0, target=1, metric=0, value=20)

        assert_array_equal(self.graph.get_metrics(0, 1), (20, 0, 0))
        assert_array_equal(self.graph.get_metrics(1, 0), (0, 0, 0))

        # confirm that a change happens to the correct metric
        self.graph.set_metric(observer=1, target=2, metric=1, value=20)
        assert_array_equal(self.graph.get_metrics(1, 2), (0, 20, 0))
        assert_array_equal(self.graph.get_metrics(2, 1), (0, 0, 0))

    def test_get_metrics_for_multiple(self):
        self.graph.set_metric(0, 1, 0, 10)
        self.graph.set_metric(0, 2, 0, 10)
        self.graph.set_metric(0, 3, 0, 10)
        self.graph.get_or_create_index(1, 2)
        self.assertEqual(self.graph.relationship_count, 4)

        output = self.graph.get_metrics_for_multiple(0, [1, 2, 3])
        assert_array_equal(output, [(10, 0, 0), (10, 0, 0), (10, 0, 0)])

        self.assertRaises(ValueError, self.graph.get_metrics_for_multiple, 0, [0])

        # missing values should be treated as (0, 0, 0)
        output = self.graph.get_metrics_for_multiple(0, [1, 100, 3])
        assert_array_equal(output, [(10, 0, 0), (0, 0, 0), (10, 0, 0)])

    def test_adjust_metric_add(self):
        # given
        self.graph.set_metric(0, 1, 0, 10)
        assert_array_equal(self.graph.get_metrics(0, 1), (10, 0, 0))

        # add 10, should now be 20
        self.graph.adjust_metric(0, 1, 0, 10)
        assert_array_equal(self.graph.get_metrics(0, 1), (20, 0, 0))

        # add 200, should now be 100
        self.graph.adjust_metric(0, 1, 0, 200)
        assert_array_equal(self.graph.get_metrics(0, 1), (100, 0, 0))

    def test_adjust_metric_subtract(self):
        # given
        self.graph.set_metric(0, 1, 0, 20)
        assert_array_equal(self.graph.get_metrics(0, 1), (20, 0, 0))

        # subtract 10, should now be 10
        self.graph.adjust_metric(0, 1, 0, -10)
        assert_array_equal(self.graph.get_metrics(0, 1), (10, 0, 0))

        # subtract 200, should now be -100
        self.graph.adjust_metric(0, 1, 0, -200)
        assert_array_equal(self.graph.get_metrics(0, 1), (-100, 0, 0))

    def test_adjust_metric_subtract_romance(self):
        # given
        self.graph.set_metric(0, 1, 2, 20)
        assert_array_equal(self.graph.get_metrics(0, 1), (0, 0, 20))

        # subtract 200, should now be 0
        self.graph.adjust_metric(0, 1, 2, -200)
        assert_array_equal(self.graph.get_metrics(0, 1), (0, 0, 0))

    def test_mark_inactive(self):
        # create some relationships
        self.graph.set_metric(0, 1, 0, 10)
        self.graph.set_metric(0, 2, 0, 10)

        self.graph.mark_inactive(0, 1)


if __name__ == "__main__":
    unittest.main()
