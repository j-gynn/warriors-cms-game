from typing import TYPE_CHECKING

from simulation.moonskip.turn_phase import TurnPhase

if TYPE_CHECKING:
    from simulation.simulation import Simulation


def register_default_phases(simulation: "Simulation"):
    manager = simulation.turn_manager

    manager.register_phase(
        TurnPhase(
            phase_id="base.hunger",
            name="Consume food",
            system=simulation.hunger_system,
            priority=10,
        )
    )

    manager.register_phase(
        TurnPhase(
            phase_id="base.lifecycle",
            name="Handle age increase",
            system=simulation.lifecycle_system,
            priority=30,
        )
    )
