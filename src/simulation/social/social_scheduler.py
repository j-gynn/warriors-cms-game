"""

Handles choosing which entities interact per turn.
Initiators are selected randomly. Targets are selected with a bias towards the initiator's strong relationships (pos or neg).
Matching is reciprocal: once selected, an entity cannot initiate their own interaction.
Matching can fail if nothing is suitable.

"""

from collections.abc import Callable, Sequence
import numpy as np

from simulation.event_manager import GameEvent


class SocialScheduler:
    def __init__(
        self,
        relationship_lookup: Callable,
        interaction_chance: float = 0.15,
        relationship_bias: float = 2.0,
        max_relationship: float = 100.0,
        rng: np.random.Generator | None = None,
    ):
        if not 0.0 <= interaction_chance <= 1.0:
            raise ValueError("interaction_chance must be between 0 and 1")

        if relationship_bias < 0:
            raise ValueError("relationship_bias cannot be negative")

        if max_relationship <= 0:
            raise ValueError("max_relationship must be positive")

        self.relationship_lookup = relationship_lookup
        self.interaction_chance = interaction_chance
        self.relationship_bias = relationship_bias
        self.max_relationship = max_relationship
        self.rng = rng if rng is not None else np.random.default_rng()

    def schedule(self, living_ids: list[int], event_queue):
        """
        try and create social interactions between the given pawns
        :param living_ids: all living, eligible pawns in the group
        :param event_queue: the event queue to publish events to
        :return: the number of social interactions queued
        """
        living_ids = np.asarray(living_ids)

        if living_ids.ndim != 1:
            raise ValueError("living_ids must be one-dimensional")

        if len(np.unique(living_ids)) != len(living_ids):
            raise ValueError("living_ids must contain unique IDs")

        if len(living_ids) < 2:
            return 0

        # Randomly select initiators.
        initiator_mask = self.rng.random(len(living_ids)) < self.interaction_chance

        initiators = np.flatnonzero(initiator_mask)

        # Randomize processing order.
        self.rng.shuffle(initiators)

        # All pawns begin available.
        available = np.ones(len(living_ids), dtype=bool)

        interaction_count = 0

        for initiator_idx in initiators:
            # Another pawn may already have selected this pawn.
            if not available[initiator_idx]:
                continue

            # Identify all currently available partners.
            candidate_mask = available.copy()
            candidate_mask[initiator_idx] = False

            candidate_indices = np.flatnonzero(candidate_mask)

            if len(candidate_indices) == 0:
                continue

            candidate_ids = living_ids[candidate_indices]
            initiator_id = living_ids[initiator_idx]

            # Retrieve initiator's perception of each candidate.
            scores = np.asarray(
                self.relationship_lookup(initiator_id, candidate_ids),
                dtype=np.float64,
            )

            if scores.shape != candidate_ids.shape:
                raise ValueError("Relationship lookup returned an invalid shape")

            if not np.all(np.isfinite(scores)):
                raise ValueError("Relationship scores must be finite")

            # Positive and negative relationships both increase likelihood
            weights = (
                1.0
                + self.relationship_bias
                * np.minimum(np.abs(scores), self.max_relationship)
                / self.max_relationship
            )

            probabilities = weights / weights.sum()

            selected_idx = self.rng.choice(len(candidate_ids), p=probabilities)

            partner_idx = candidate_indices[selected_idx]
            partner_id = living_ids[partner_idx]

            # Reserve both this turn
            available[initiator_idx] = False
            available[partner_idx] = False

            # Emit the interaction event
            event_queue.append(
                GameEvent(
                    type="social_interaction",
                    entity_id=int(initiator_id),
                    data={"target_id": partner_id},
                )
            )

            interaction_count += 1

        return interaction_count
