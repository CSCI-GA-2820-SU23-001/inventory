"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from service.models import Inventory, Condition


class InventoryFactory(factory.Factory):
    """Creates fake inventories for testing purposes"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Inventory

    id = factory.Sequence(lambda n: n)
    quantity = factory.Sequence(lambda n: n)
    restock_level = factory.Sequence(lambda n: n)
    condition = FuzzyChoice(choices=[Condition.NEW, Condition.OPEN_BOX, Condition.USED])
