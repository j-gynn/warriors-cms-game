from data.social.family_graph import FamilyGraph
from simulation.entity_systems.ancestry_system import AncestrySystem

family = FamilyGraph()
ancestrysystem = AncestrySystem(None, family)

maternal_grandparent = 5
mother = 0
father = 1
adoptive_parent = 2
child = 3
second_child = 4

family.add_biological_parent(maternal_grandparent, mother)
family.add_biological_parent(mother, child)
family.add_biological_parent(father, child)
family.adopt(adoptive_parent, child)

family.add_biological_parent(mother, second_child)

print("Mother's parents:")
print(list(family.get_parents(mother)))

print("Child's parents:")
print(list(family.get_parents(child)))

print("\nMother's children:")
print(list(family.get_children(mother)))

print("\nParent count:", family.get_parent_count(child))
print("Child count:", family.get_child_count(mother))

print("\nRemove adoption:")
print(family.remove_parent(adoptive_parent, child))

print("\nTry removing biological parent:")
print(family.remove_parent(mother, child))

print("\nRemaining parents:")
print(list(family.get_parents(child)))

print("\nTotal connections:", family.connection_count)
