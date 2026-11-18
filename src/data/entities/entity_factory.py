import uuid

from src.data.entities.entity import Entity


class EntityFactory:
    def __init__(self, definitions, lifecycles, component_registry):
        self.definitions = definitions
        self.lifecycles = lifecycles
        self.component_registry = component_registry

    def create(self, definition_id, entity_id=None):
        definition = self.definitions.get(definition_id)

        if definition is None:
            raise ValueError("Unknown entity definition id {}".format(definition_id))
        entity = Entity(
            entity_id=entity_id or uuid.uuid4().hex, definition_id=definition_id
        )

        lifecycle = definition.get("lifecycle")

        if lifecycle:
            lifecycle_config = {
                "lifecycle": lifecycle["definition"],
                "stage_id": lifecycle["starting_stage"],
                "time_in_stage": 0,
            }

            definition_components = dict(definition.get("components", {}))

            definition_components["lifecycle"] = lifecycle_config

        else:
            definition_components = definition.get("components", {})

        for component_id, config in definition_components.items():
            component_cls = self.component_registry.get(component_id)

            if component_cls is None:
                raise ValueError(
                    "Unrecognised component '{0}' in entity definition '{1}'".format(
                        component_id, definition_id
                    )
                )

            if not isinstance(config, dict):
                raise ValueError("Invalid component config '{0}'".format(config))

            try:
                component = component_cls(**config)
            except TypeError as e:
                raise ValueError(
                    "Invalid component config '{0}' in '{1}': {2}".format(
                        component_id, definition_id, e
                    )
                ) from e

            entity.add_component(component)
        return entity
