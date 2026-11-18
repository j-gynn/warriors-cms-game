# import pygame
#
# while 1:
#     for event in pygame.event.get():
#         pass

import logging

logging.basicConfig(level=logging.DEBUG)
from simulation.simulation import Simulation
from simulation.moonskip.turn_manager import TurnManager

sim = Simulation()

testcat, testcat_idx = sim.spawn_entity("base.cat")
print("welcome to clangen 2 lmao")
print(f"test cat id: {testcat.uuid}")

cat2, cat2_idx = sim.spawn_entity("base.cat")

sim.relationships.get_or_create_index(testcat.id, cat2.id)
sim.relationships.set_metric(testcat.id, cat2.id, 0, 100)
sim.relationships.set_metric(testcat.id, cat2.id, 1, 100)
print(sim.relationships.get_metrics(testcat.id, cat2.id))

while 1:
    i = input("Press Enter to advance turn...")

    match i:
        case "p":
            print("gregnancy queued")
            sim.pregnancy_system.get_pregnant(
                sim, testcat_idx, cat2.id, testcat.definition_id
            )
        case _:
            pass

    sim.advance_turn()
    print(f"\nturn: {sim.turn_number}")

    print(f"testcat's hunger is {testcat.get_component('hunger').hunger}")
    print(f"testcat's health is {testcat.get_component('health').health}")
    print(f"testcat's lifecycle state is {testcat.get_component('lifecycle').stage_id}")
    print(f"event queue is currently {len(sim.events.queue)} events long")

    if len(sim.entities.get_all()) == 0:
        print("no more entities, exiting")
        break
