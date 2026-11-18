from typing import Any


class TimeSystem:
    pass

    def __init__(self, event_manager, timestamp, season_data):
        self.events = event_manager
        self.timestamp = timestamp
        self.season_data = season_data
        self.calendar_idx = [
            key * value["duration"] for key, value in self.season_data.items()
        ]
        self.year_length = len(self.calendar_idx)

    def season(self, time, season_offset) -> str:
        return self.calendar_idx[(time + season_offset) % self.year_length]

    def season_modifiers(self, time, season_offset) -> dict[str, Any]:
        season = self.season(time, season_offset)
        return self.season_data[season]["modifiers"]
