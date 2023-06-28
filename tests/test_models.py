"""
Test cases for Inventory Model

"""
import os
import logging
import unittest
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
    """ Test Cases for Inventory Model """

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

    def test_example_replace_this(self):
        """ It should always be true """
        self.assertTrue(True)

    def test_create_a_inventory(self):
        """It should Create a Inventory and assert that it exists"""
        inventory = Inventory(id=1, condition= Condition.NEW, quantity=1, restock_level=3)
        self.assertEqual(str(inventory), "<Inventory id=[1] condition=[Condition.NEW]>")
        self.assertTrue(inventory is not None)
        self.assertTrue(inventory.id is not None)
        self.assertEqual(inventory.condition, Condition.NEW)
        self.assertEqual(inventory.quantity, 1)
        self.assertEqual(inventory.restock_level, 3)

        inventory = Inventory(id=2, condition=Condition.OPEN_BOX, restock_level=5)
        self.assertEqual(inventory.quantity, None)
        self.assertEqual(inventory.condition, Condition.OPEN_BOX)

    def test_add_a_inventory(self):
        """It should Create a inventory and add it to the database"""
        inventories = Inventory.all()
        self.assertEqual(inventories, [])
        inventory = Inventory(id=1, condition=Condition.NEW, quantity=10, restock_level=4)
        self.assertTrue(inventory is not None)
        self.assertTrue(inventory.id is not None)
        inventory.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(inventory.id)
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 1)

    def test_read_a_inventory(self):
        """It should Read a Inventory"""
        inventory = InventoryFactory()
        logging.debug(inventory)
        inventory.create()
        self.assertIsNotNone(inventory.id)
        # Fetch it back
        found_inventory = Inventory.find(inventory.id, inventory.condition)
        self.assertEqual(found_inventory.id, inventory.id)
        self.assertEqual(found_inventory.condition, inventory.condition)

    def test_update_a_inventory(self):
        """It should Update a Inventory"""
        #inventory = Inventory(id=2, condition= Condition.NEW, quantity=1, restock_level=3)
        inventory = InventoryFactory()
        logging.debug(inventory)
        inventory.create()
        logging.debug(inventory)
        self.assertIsNotNone(inventory.id)
        
        # Change it an save it
        inventory.quantity = 13
        original_id = inventory.id
        inventory.update()
        self.assertEqual(inventory.id, original_id)
        self.assertEqual(inventory.quantity, 13)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 1)
        self.assertEqual(inventories[0].id, original_id)
        self.assertEqual(inventories[0].quantity, 13)
    
    def test_update_no_id(self):
        """It should not Update an inventory with no id"""
        inventory = InventoryFactory()
        logging.debug(inventory)
        inventory.id = None
        self.assertRaises(DataValidationError, inventory.update)

    def test_delete_an_inventory(self):
        """It should Delete a inventory"""
        inventory = InventoryFactory()
        inventory.create()
        self.assertEqual(len(Inventory.all()), 1)
        # delete the pet and make sure it isn't in the database
        inventory.delete()
        self.assertEqual(len(Inventory.all()), 0)

    def test_list_all_inventories(self):
        """It should List all inventories in the database"""
        inventories = Inventory.all()
        self.assertEqual(inventories, [])
        # Create 5 Pets
        for _ in range(5):
            inventory = InventoryFactory()
            inventory.create()
        # See if we get back 5 pets
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 5)

    def test_serialize_an_inventory(self):
        """It should serialize an Inventory"""
        inventory = InventoryFactory()
        data = inventory.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], inventory.id)
        self.assertIn("condition", data)
        self.assertEqual(data["condition"], inventory.condition.name)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], inventory.quantity)
        self.assertIn("restock_level", data)
        self.assertEqual(data["restock_level"], inventory.restock_level)
    
    def test_deserialize_an_inventory(self):
        """It should de-serialize a inventory"""
        data = InventoryFactory().serialize()
        inventory = Inventory()
        inventory.deserialize(data)
        self.assertNotEqual(inventory, None)
        self.assertNotEqual(inventory.id, None)
        self.assertEqual(inventory.condition.name, data["condition"])
        self.assertEqual(inventory.quantity, data["quantity"])
        self.assertEqual(inventory.restock_level, data["restock_level"])
        
    def test_deserialize_missing_data(self):
        """It should not deserialize an Inventory with missing data"""
        data = {"id": 1, "quantity": "2"}
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
        # find the 2nd pet in the list
        inventory = Inventory.find(inventories[1].id, inventories[1].condition)
        self.assertIsNot(inventory, None)
        self.assertEqual(inventory.id, inventories[1].id)
        self.assertEqual(inventory.condition, inventories[1].condition)
        self.assertEqual(inventory.quantity, inventories[1].quantity)
        self.assertEqual(inventory.restock_level, inventories[1].restock_level)
