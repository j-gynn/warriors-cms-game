import json
from pathlib import Path


def load_definitions(directory):
    definitions = {}

    directory = Path(__file__).resolve().parent / Path(directory)

    for file_path in directory.glob("*.json"):
        with file_path.open("r", encoding="utf-8") as file:
            definition = json.load(file)

        definition_id = definition["id"]

        if definition_id in definitions:
            raise ValueError(f"Duplicate definition: {definition_id}")

        definitions[definition_id] = definition

    return definitions
