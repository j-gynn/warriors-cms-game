from data.definitions.definition_loader import load_definitions


class ResourceRegistry:
    def __init__(self):
        self.definitions = load_definitions("resources")

    def get(self, resource_id: str):
        return self.definitions.get(resource_id)
