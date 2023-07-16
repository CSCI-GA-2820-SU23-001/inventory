"""
Test cases for Inventory Model

"""
import os
import logging
import unittest
import datetime
from werkzeug.exceptions import NotFound
from tests.factories import InventoryFactory
from service.models import Inventory, Condition, DataValidationError, db
from service import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Inventory   M O D E L   T E S T   C A S E S
######################################################################
class TestInventory(unittest.TestCase):
    """Test Cases for Inventory Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Inventory.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_inventory(self):
        """It should Create a Inventory and assert that it exists"""
        inventory = Inventory(
            product_id=1, condition=Condition.NEW, quantity=1, restock_level=3
        )
        self.assertEqual(
            str(inventory), "<Inventory product_id=[1] condition=[Condition.NEW]>"
        )
        self.assertTrue(inventory is not None)
        self.assertTrue(inventory.product_id is not None)
        self.assertEqual(inventory.condition, Condition.NEW)
        self.assertEqual(inventory.quantity, 1)
        self.assertEqual(inventory.restock_level, 3)

        inventory = Inventory(
            product_id=2, condition=Condition.OPEN_BOX, restock_level=5
        )
        self.assertEqual(inventory.quantity, None)
        self.assertEqual(inventory.condition, Condition.OPEN_BOX)

    def test_add_a_inventory(self):
        """It should Create a inventory and add it to the database"""
        inventories = Inventory.all()
        self.assertEqual(inventories, [])
        inventory = Inventory(
            product_id=1, condition=Condition.NEW, quantity=10, restock_level=4
        )
        self.assertTrue(inventory is not None)
        self.assertTrue(inventory.product_id is not None)
        inventory.create()
        self.assertIsNotNone(inventory.product_id)
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 1)

    def test_add_a_inventory_default_quantity(self):
        """It should Create a inventory with default quantity and restock_level and add it to the database"""
        inventory = Inventory(product_id=2, condition=Condition.OPEN_BOX)
        self.assertTrue(inventory is not None)
        self.assertTrue(inventory.product_id is not None)
        self.assertEqual(inventory.quantity, None)
        self.assertEqual(inventory.restock_level, None)
        inventory.create()
        self.assertIsNotNone(inventory.product_id)
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 1)
        self.assertEqual(inventories[0].product_id, inventory.product_id)
        self.assertEqual(inventories[0].quantity, 1)
        self.assertEqual(inventories[0].restock_level, 1)

    def test_read_a_inventory(self):
        """It should Read a Inventory"""
        inventory = InventoryFactory()
        logging.debug(inventory)
        inventory.create()
        self.assertIsNotNone(inventory.product_id)
        # Fetch it back
        found_inventory = Inventory.find(inventory.product_id, inventory.condition)
        self.assertEqual(found_inventory.product_id, inventory.product_id)
        self.assertEqual(found_inventory.condition, inventory.condition)

    def test_update_a_inventory(self):
        """It should Update a Inventory"""
        inventory = InventoryFactory()
        logging.debug(inventory)
        inventory.create()
        logging.debug(inventory)
        self.assertIsNotNone(inventory.product_id)
        # Change it an save it
        inventory.quantity = 13
        original_id = inventory.product_id
        inventory.update()
        self.assertEqual(inventory.product_id, original_id)
        self.assertEqual(inventory.quantity, 13)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 1)
        self.assertEqual(inventories[0].product_id, original_id)
        self.assertEqual(inventories[0].quantity, 13)

    def test_update_no_id(self):
        """It should not Update an inventory with no product_id"""
        inventory = InventoryFactory()
        logging.debug(inventory)
        inventory.product_id = None
        self.assertRaises(DataValidationError, inventory.update)

    def test_update_no_condition(self):
        """It should not Update an inventory with no condition"""
        inventory = InventoryFactory()
        logging.debug(inventory)
        inventory.condition = None
        self.assertRaises(DataValidationError, inventory.update)

    def test_delete_an_inventory(self):
        """It should Delete a inventory"""
        inventory = InventoryFactory()
        inventory.create()
        self.assertEqual(len(Inventory.all()), 1)
        # delete the inventory and make sure it isn't in the database
        inventory.delete()
        self.assertEqual(len(Inventory.all()), 0)

    def test_list_all_inventories(self):
        """It should List all inventories in the database"""
        inventories = Inventory.all()
        self.assertEqual(inventories, [])
        # Create 5 inventories
        for _ in range(5):
            inventory = InventoryFactory()
            inventory.create()
        # See if we get back 5 inventories
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 5)

    def test_serialize_an_inventory(self):
        """It should serialize an Inventory"""
        inventory = InventoryFactory()
        self.assertEqual(inventory.last_updated_on, None)
        inventory.create()
        self.assertIsNotNone(inventory.product_id)
        self.assertNotEqual(inventory.last_updated_on, None)
        data = inventory.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("product_id", data)
        self.assertEqual(data["product_id"], inventory.product_id)
        self.assertIn("condition", data)
        self.assertEqual(data["condition"], inventory.condition.name)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], inventory.quantity)
        self.assertIn("restock_level", data)
        self.assertEqual(data["restock_level"], inventory.restock_level)
        self.assertIn("last_updated_on", data)
        self.assertAlmostEqual(
            data["last_updated_on"],
            inventory.last_updated_on,
            delta=datetime.timedelta(seconds=0),
        )

    def test_deserialize_an_inventory(self):
        """It should de-serialize a inventory"""
        data = InventoryFactory().serialize()
        inventory = Inventory()
        inventory.deserialize(data)
        self.assertNotEqual(inventory, None)
        self.assertNotEqual(inventory.product_id, None)
        self.assertEqual(inventory.condition.name, data["condition"])
        self.assertEqual(inventory.quantity, data["quantity"])
        self.assertEqual(inventory.restock_level, data["restock_level"])
        self.assertEqual(inventory.last_updated_on, data["last_updated_on"])

    def test_deserialize_missing_data(self):
        """It should not deserialize an Inventory with missing data"""
        data = {"product_id": 1, "quantity": "2"}
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_deserialize_bad_quantity(self):
        """It should not deserialize a bad quantity attribute"""
        test_inventory = InventoryFactory()
        data = test_inventory.serialize()
        data["quantity"] = "true"
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_deserialize_bad_restock_level(self):
        """It should not deserialize a bad restock_level attribute"""
        test_inventory = InventoryFactory()
        data = test_inventory.serialize()
        data["restock_level"] = "true"
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_deserialize_bad_condition(self):
        """It should not deserialize a bad condition attribute"""
        test_inventory = InventoryFactory()
        data = test_inventory.serialize()
        data["condition"] = "unknown"  # wrong case
        inventory = Inventory()
        self.assertRaises(DataValidationError, inventory.deserialize, data)

    def test_find_inventory(self):
        """It should Find a inventory by ID"""
        inventories = InventoryFactory.create_batch(5)
        for inventory in inventories:
            inventory.create()
        logging.debug(inventories)
        # make sure they got saved
        self.assertEqual(len(Inventory.all()), 5)
        # find the 2nd inventory record in the list
        inventory = Inventory.find(inventories[1].product_id, inventories[1].condition)
        self.assertIsNot(inventory, None)
        self.assertEqual(inventory.product_id, inventories[1].product_id)
        self.assertEqual(inventory.condition, inventories[1].condition)
        self.assertEqual(inventory.quantity, inventories[1].quantity)
        self.assertEqual(inventory.restock_level, inventories[1].restock_level)

    def test_find_by_condition(self):
        """It should Find Inventories by condition"""
        inventories = InventoryFactory.create_batch(10)
        for inventory in inventories:
            inventory.create()
        condition = inventories[0].condition
        count = len(
            [inventory for inventory in inventories if inventory.condition == condition]
        )
        found = Inventory.find_by_condition(condition)
        self.assertEqual(found.count(), count)
        for inventory in found:
            self.assertEqual(inventory.condition, condition)

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        inventories = InventoryFactory.create_batch(3)
        for inventory in inventories:
            inventory.create()

        inventory = Inventory.find_or_404(
            inventories[1].product_id, inventories[1].condition
        )
        self.assertIsNot(inventory, None)
        self.assertEqual(inventory.product_id, inventories[1].product_id)
        self.assertEqual(inventory.condition, inventories[1].condition)
        self.assertEqual(inventory.quantity, inventories[1].quantity)
        self.assertEqual(inventory.restock_level, inventories[1].restock_level)

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Inventory.find_or_404, 0, Condition.NEW)
