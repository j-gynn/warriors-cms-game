import numpy as np


class FamilyGraph:
    BIOLOGICAL = 0
    ADOPTIVE = 1

    def __init__(self, initial_capacity=1024):
        self.capacity = initial_capacity
        self.count = 0

        # Connection storage:
        # Column 0: Parent index (uint32)
        # Column 1: Child index (uint32)
        # Column 2: Relationship type (uint8)
        # Column 3: Active (bool)
        #
        # Separate arrays are used because NumPy arrays
        # cannot efficiently mix these data types.

        self.parents = np.zeros(self.capacity, dtype=np.uint32)

        self.children = np.zeros(self.capacity, dtype=np.uint32)

        self.types = np.zeros(self.capacity, dtype=np.uint8)

        self.active = np.zeros(self.capacity, dtype=np.bool_)

        # Parent-child pair -> connection index
        self.lookup = {}

        # Child -> connection indices
        self.parents_by_child = {}

        # Parent -> connection indices
        self.children_by_parent = {}

        self.active_count = 0

    @staticmethod
    def pair_key(parent, child):
        if parent == child:
            raise ValueError("A pawn cannot be their own parent")

        if min(parent, child) < 0:
            raise ValueError("Pawn indexes cannot be negative")

        if max(parent, child) >= 2**32:
            raise OverflowError("Pawn index exceeds uint32 limit")

        return (parent << 32) | child

    def _grow(self):
        new_capacity = self.capacity * 2

        parents = np.zeros(new_capacity, dtype=np.uint32)
        children = np.zeros(new_capacity, dtype=np.uint32)
        types = np.zeros(new_capacity, dtype=np.uint8)
        active = np.zeros(new_capacity, dtype=np.bool_)

        parents[: self.count] = self.parents[: self.count]
        children[: self.count] = self.children[: self.count]
        types[: self.count] = self.types[: self.count]
        active[: self.count] = self.active[: self.count]

        self.parents = parents
        self.children = children
        self.types = types
        self.active = active

        self.capacity = new_capacity

    def add_parent(self, parent, child, relationship_type=BIOLOGICAL):
        """
        Add a parent-child relationship to the family graph.
        :param parent: parent index
        :param child: child index
        :param relationship_type: biological or adoptive
        :return: True if record was added, False if it already existed
        """

        key = self.pair_key(parent, child)

        if relationship_type not in (self.BIOLOGICAL, self.ADOPTIVE):
            raise ValueError("Invalid relationship type")

        existing = self.lookup.get(key)

        if existing is not None:
            existing_type = int(self.types[existing])

            # Biological connections take priority.
            if existing_type == self.ADOPTIVE and relationship_type == self.BIOLOGICAL:
                self.types[existing] = self.BIOLOGICAL
                return True

            return False

        if self.count >= self.capacity:
            self._grow()

        index = self.count
        self.count += 1

        self.parents[index] = parent
        self.children[index] = child
        self.types[index] = relationship_type
        self.active[index] = True

        self.lookup[key] = index

        self.parents_by_child.setdefault(child, []).append(index)
        self.children_by_parent.setdefault(parent, []).append(index)

        self.active_count += 1

        return True

    def add_biological_parent(self, parent, child):
        return self.add_parent(parent, child, self.BIOLOGICAL)

    def adopt(self, parent, child):
        return self.add_parent(parent, child, self.ADOPTIVE)

    def get_parents(self, child):
        """
        Get all parents of the child
        :param child: child index
        :return: parent index, relationship type
        """
        for index in self.parents_by_child.get(child, ()):
            if self.active[index]:
                yield int(self.parents[index]), int(self.types[index])

    def get_children(self, parent):
        """
        Get all children of the parent
        :param parent: parent index
        :return: child index, relationship type
        """
        for index in self.children_by_parent.get(parent, ()):
            if self.active[index]:
                yield int(self.children[index]), int(self.types[index])

    def is_parent_of(self, parent, child):
        return self.pair_key(parent, child) in self.lookup

    def remove_parent(self, parent, child):
        key = self.pair_key(parent, child)

        index = self.lookup.get(key)

        if index is None:
            return False

        # Biological parenthood cannot be rescinded.
        if self.types[index] == self.BIOLOGICAL:
            return False

        del self.lookup[key]

        self.active[index] = False
        self.active_count -= 1

        return True

    def get_parent_count(self, child):
        return sum(1 for _ in self.get_parents(child))

    def get_child_count(self, parent):
        return sum(1 for _ in self.get_children(parent))

    @property
    def connection_count(self):
        return self.active_count
