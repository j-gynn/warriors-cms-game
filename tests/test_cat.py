from data.entities.entity_registry import EntityRegistry
from data.social.relationship_graph import RelationshipGraph
from simulation.simulation import Simulation

simulation = Simulation()

# Create some pawns
_, alice = simulation.spawn_entity("base.cat")
_, bob = simulation.spawn_entity("base.cat")
_, charlie = simulation.spawn_entity("base.cat")

print("Pawn IDs:")
print(alice, bob, charlie)

# Alice likes Bob
simulation.relationships.set_metric(alice, bob, RelationshipGraph.LIKE, 75)

# Bob trusts Alice
simulation.relationships.set_metric(bob, alice, RelationshipGraph.TRUST, 60)

# Charlie is romantically interested in Alice
simulation.relationships.set_metric(charlie, alice, RelationshipGraph.ROMANCE, 90)

# Retrieve directional relationships
print("\nAlice's feelings towards Bob:")
print(simulation.relationships.get_metrics(alice, bob))

print("\nBob's feelings towards Alice:")
print(simulation.relationships.get_metrics(bob, alice))

# Retrieve all relationships belonging to Alice
print("\nAlice's relationships:")

for other_pawn, metrics in simulation.relationships.iter_for_pawn(alice):
    print(other_pawn, metrics)

print("\nTotal relationships:")
print(simulation.relationships.relationship_count)
