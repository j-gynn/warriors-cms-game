class EntityRegistry:
    def __init__(self):
        self.entities = {}
        self.uuid_to_index = {}
        self.index_to_uuid = []

    def add(self, entity):
        index = len(self.index_to_uuid)

        self.uuid_to_index[entity.id] = index
        self.index_to_uuid.append(entity.id)

        if index in self.entities:
            raise ValueError(f"Entity with id {0} already exists.".format(index))
        self.entities[index] = entity
        entity.id = index
        return index

    def get(self, entity_id):
        return self.entities.get(entity_id)

    def remove(self, entity_id):
        self.entities.pop(entity_id, None)

    def get_all(self):
        return list(self.entities.values())

    def get_by_component(self, component_name):
        return [
            entity
            for entity in self.entities.values()
            if entity.has_component(component_name)
        ]
