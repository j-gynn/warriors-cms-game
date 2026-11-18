from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass
class GameEvent:
    type: str
    data: dict


@dataclass
class EntityEvent(GameEvent):
    entity_id: int


@dataclass
class FactionEvent(GameEvent):
    faction_id: int


class EventManager:
    def __init__(self):
        self.queue: deque[GameEvent] = deque()
        self._handlers = defaultdict(list)

        self._scheduled_events = {}

    def subscribe(self, event_type, handler):
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type, handler):
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    def publish(self, data: GameEvent):
        self.queue.append(data)

    def process_events(self, simulation):
        processed = 0
        max_events = 100000

        while self.queue:
            if processed >= max_events:
                raise RuntimeError("Maximum event processing limit exceeded")

            event = self.queue.popleft()

            for handler in self._handlers[event.type]:
                handler(event, simulation)

            processed += 1

    def schedule_event(self, event: GameEvent, due_turn: int):
        self._scheduled_events.setdefault(due_turn, []).append(event)

    def release_scheduled_events(self, turn: int):
        self.queue.extend(self._scheduled_events.pop(turn, []))
