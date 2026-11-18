import uuid


class Entity:
    def __init__(self, entity_id, definition_id):
        self.id: int | None = None  # will be given by the entity registry
        self.uuid = entity_id
        self.definition_id = definition_id
        self.components = {}

    def add_component(self, component):
        self.components[component.name] = component

    def get_component(self, name):
        return self.components.get(name)

    def has_component(self, name):
        return name in self.components
