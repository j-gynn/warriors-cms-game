import numpy as np


class RelationshipGraph:
    # Metric positions
    LIKE = 0
    TRUST = 1
    ROMANCE = 2

    METRIC_COUNT = 6

    def __init__(self, initial_capacity=1024):
        self.capacity = initial_capacity
        self.count = 0

        # Relationship endpoints
        self.endpoints = np.zeros((self.capacity, 2), dtype=np.int64)

        # Directional relationship metrics
        self.metrics = np.zeros((self.capacity, self.METRIC_COUNT), dtype=np.int8)

        # Record validity
        self.active = np.zeros(self.capacity, dtype=np.bool_)

        # Pair key -> relationship record index
        self.lookup = {}

        # Pawn index -> relationship record indices
        self.adjacency = {}

    @staticmethod
    def pair_key(a, b):
        if a == b:
            raise ValueError("An entity cannot have a relationship with itself")

        if a > b:
            a, b = b, a

        if a >= 2**32 or b >= 2**32:
            raise OverflowError("Entity index exceeds 32-bit pair-key limit")

        return (a << 32) | b

    def _grow(self):
        new_capacity = self.capacity * 2

        endpoints = np.zeros((new_capacity, 2), dtype=np.int64)

        metrics = np.zeros((new_capacity, self.METRIC_COUNT), dtype=np.int8)

        active = np.zeros(new_capacity, dtype=np.bool_)

        endpoints[: self.count] = self.endpoints[: self.count]
        metrics[: self.count] = self.metrics[: self.count]
        active[: self.count] = self.active[: self.count]

        self.endpoints = endpoints
        self.metrics = metrics
        self.active = active

        self.capacity = new_capacity

    def get_or_create_index(self, a, b):
        """
        Get or create the relationship index between two entities.
        :param a:
        :param b:
        :return:
        """
        key = self.pair_key(a, b)

        existing = self.lookup.get(key)

        if existing is not None:
            return existing

        if self.count >= self.capacity:
            self._grow()

        index = self.count
        self.count += 1

        # Canonical ordering: lower index first
        if a > b:
            a, b = b, a

        self.endpoints[index] = (a, b)

        self.metrics[index] = 0
        self.active[index] = True

        self.lookup[key] = index

        self.adjacency.setdefault(a, []).append(index)
        self.adjacency.setdefault(b, []).append(index)

        return index

    def get_metrics(self, observer, target):
        key = self.pair_key(observer, target)
        index = self.lookup.get(key)

        if index is None:
            return None

        a, b = self.endpoints[index]

        if observer == a:
            offset = 0
        else:
            offset = 3

        return self.metrics[index, offset : offset + 3]

    def get_metrics_for_multiple(self, observer, targets):
        targets = np.asarray(targets, dtype=np.int64)
        count = len(targets)

        # Construct pair keys and retrieve storage indices.
        indices = np.fromiter(
            (
                self.lookup.get(self.pair_key(observer, int(target)), -1)
                for target in targets
            ),
            dtype=np.int64,
            count=count,
        )

        # Allocate neutral results for missing relationships.
        result = np.zeros((count, 3), dtype=self.metrics.dtype)

        valid = indices >= 0

        if not np.any(valid):
            return result

        valid_indices = indices[valid]

        # Determine which direction's metrics to retrieve.
        endpoints = self.endpoints[valid_indices]

        offsets = np.where(endpoints[:, 0] == observer, 0, 3)

        # Retrieve all relevant metric rows.
        rows = self.metrics[valid_indices]

        # Extract the correct directional metrics.
        result[valid] = rows[
            np.arange(len(valid_indices))[:, None], offsets[:, None] + np.arange(3)
        ]

        return result

    def set_metric(self, observer, target, metric, value):
        if metric not in (self.LIKE, self.TRUST, self.ROMANCE):
            raise ValueError("Invalid relationship metric")

        value = int(value)

        if not -100 <= value <= 100:
            raise ValueError("Metric must be between -100 and 100")

        index = self.get_or_create_index(observer, target)

        a, b = self.endpoints[index]

        offset = 0 if observer == a else 3

        self.metrics[index, offset + metric] = value

    def adjust_metric(self, observer, target, metric, amount):
        current = self.get_metrics(observer, target)

        if current is None:
            value = 0
        else:
            value = int(current[metric])

        new_value = max(-100 if metric != self.ROMANCE else 0, min(100, value + amount))

        self.set_metric(observer, target, metric, new_value)

    def mark_inactive(self, a, b):
        key = self.pair_key(a, b)

        index = self.lookup.pop(key, None)

        if index is None:
            return False

        self.active[index] = False

        return True

    def iter_for_pawn(self, pawn):
        for index in self.adjacency.get(pawn, ()):
            if not self.active[index]:
                continue

            a, b = self.endpoints[index]

            if pawn == a:
                other = int(b)
                offset = 0
            else:
                other = int(a)
                offset = 3

            yield other, self.metrics[index, offset : offset + 3]

    @property
    def relationship_count(self):
        return len(self.lookup)
