import numpy as np


def get_derived_interaction_affinity(like, trust):
    """
    Provides a single value representing the overall likelihood of an interaction between two entities,
    based on their prior relationship
    :param like: instigator's like value
    :param trust: instigator's trust value
    :return: int from 0 to 100 representing the likelihood of interaction
    """
    like_weight = 1.0
    trust_weight = 0.5

    return ((np.abs(like) * like_weight) + (np.abs(trust) * trust_weight)) / (
        like_weight + trust_weight
    )
