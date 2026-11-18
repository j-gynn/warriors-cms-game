from typing import TYPE_CHECKING

from simulation.event_manager import FactionEvent

if TYPE_CHECKING:
    from simulation.factions.faction import Faction


class ResourceManager:
    def __init__(self, faction: "Faction"):
        self.faction: "Faction" = faction
        self._resources = {}

    def get_amount(self, resource_id):
        return self._resources.get(resource_id, 0)

    def add(self, resource_id, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")

        current_amount = self.get_amount(resource_id)

        self.faction.events.publish(
            FactionEvent(
                type="resource_changed",
                faction_id=self.faction.id,
                data={
                    "resource_id": resource_id,
                    "previous_amount": current_amount,
                    "new_amount": current_amount + amount,
                    "change": amount,
                },
            )
        )
        self._resources[resource_id] = self.get_amount(resource_id) + amount

    def remove(self, resource_id, amount) -> int:
        """
        Removes a specified amount of a resource from the manager.
        :param resource_id: resource to remove
        :param amount: amount to remove
        :return: amount actually removed
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")

        current_amount = self.get_amount(resource_id)

        amount_removed = current_amount if current_amount - amount < 0 else amount

        self._resources[resource_id] = max(0, current_amount - amount)

        self.faction.events.publish(
            FactionEvent(
                type="base.resource_changed",
                faction_id=self.faction.id,
                data={
                    "resource_id": resource_id,
                    "previous_amount": current_amount,
                    "new_amount": self.get_amount(resource_id),
                    "change": -amount_removed,
                },
            )
        )

        return amount_removed

    def has_enough(self, resource_id, amount):
        return self.get_amount(resource_id) >= amount

    def try_remove(self, resource_id, amount) -> bool:
        """
        Cancels the transaction if enough of the resource is not available.
        :param resource_id: resource to remove
        :param amount: amount to remove
        :return: True if the transaction was successful, False otherwise
        """

        if amount <= 0:
            raise ValueError("Amount must be positive")

        if not self.has_enough(resource_id, amount):
            return False

        self.remove(resource_id, amount)
        return True
