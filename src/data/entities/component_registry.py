from src.data.entities.components.life_cycle import LifeCycleComponent
from src.data.entities.components.health import HealthComponent
from src.data.entities.components.hunger import HungerComponent

COMPONENT_REGISTRY = {
    "health": HealthComponent,
    "hunger": HungerComponent,
    "lifecycle": LifeCycleComponent,
}
