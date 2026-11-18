from enum import Enum
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from data.social.family_graph import FamilyGraph


class RelationType(Enum):
    biological = 0
    adoptive = 1


class AncestrySystem:
    def __init__(self, event_manager, family_graph):
        self.events = event_manager
        self.family_graph: "FamilyGraph" = family_graph

    def update(self, simulation):
        pass

    def add_biological_parent(self, parent_id, child_id):
        self.family_graph.add_parent(parent_id, child_id, self.family_graph.BIOLOGICAL)

    def adopt(self, parent_id, child_id):
        self.family_graph.add_parent(parent_id, child_id, self.family_graph.ADOPTIVE)

    def get_biological_ancestors(self, pawn_id, max_depth=3):
        visited = {pawn_id}
        frontier = [(pawn_id, 0)]

        while frontier:
            current_id, depth = frontier.pop()

            if depth >= max_depth:
                continue

            for parent_id, status in self.family_graph.get_parents(current_id):
                if status != self.family_graph.BIOLOGICAL:
                    continue

                if parent_id in visited:
                    continue

                visited.add(parent_id)

                yield parent_id, depth + 1
                frontier.append((parent_id, depth + 1))

    def can_breed(self, pawn_a, pawn_b, max_depth=3):
        if pawn_a == pawn_b:
            return False

        ancestors_a = {
            ancestor_id
            for ancestor_id, _ in self.get_biological_ancestors(pawn_a, max_depth)
        }

        if pawn_b in ancestors_a:
            return False

        for ancestor_id, _ in self.get_biological_ancestors(pawn_b, max_depth):
            if ancestor_id in ancestors_a:
                return False

        return True

    # def get_siblings(self, pawn_id):
    #     seen = set()
    #
    #     for parent_id, blood_status in self.family_graph.get_parents(pawn_id):
    #         for sibling_id, _ in self.family_graph.get_children(parent_id):
    #             if sibling_id != pawn_id:
    #                 seen.add(sibling_id)
    #
    #     yield from seen
    #
    # def get_grandparents(self, pawn_id):
    #     seen = set()
    #
    #     for parent_id, _ in self.family_graph.get_parents(pawn_id):
    #         for grandparent_id, _ in self.family_graph.get_parents(parent_id):
    #             seen.add(grandparent_id)
    #
    #     yield from seen
    #
    # def get_grandchildren(self, pawn_id):
    #     seen = set()
    #
    #     for child_id, _ in self.family_graph.get_children(pawn_id):
    #         for grandchild_id, _ in self.family_graph.get_children(child_id):
    #             seen.add(grandchild_id)
    #
    #     yield from seen
    #
    # def get_niblings(self, pawn_id):
    #     seen = set()
    #
    #     for sibling_id in self.get_siblings(pawn_id):
    #         for nibling_id in self.family_graph.get_children(sibling_id):
    #             seen.add(nibling_id)
