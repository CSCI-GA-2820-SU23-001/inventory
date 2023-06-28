"""
Test cases for Inventory Model

"""
import os
import logging
import unittest
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
        inventory = Inventory(quantity=1, restock_level=3)
        self.assertEqual(str(inventory), "<Inventory id=[None] condition=[None]>")
        self.assertTrue(inventory is not None)
        self.assertEqual(inventory.id, None)
        self.assertEqual(inventory.condition, None)
        self.assertEqual(inventory.quantity, 1)
        self.assertEqual(inventory.restock_level, 3)

        inventory = Inventory(condition=Condition.OPEN_BOX, restock_level=5)
        self.assertEqual(inventory.quantity, None)
        self.assertEqual(inventory.condition, Condition.OPEN_BOX)

    def test_add_a_inventory(self):
        """It should Create a inventory and add it to the database"""
        inventories = Inventory.all()
        self.assertEqual(inventories, [])
        inventory = Inventory(quantity=10, restock_level=4)
        self.assertTrue(inventory is not None)
        self.assertEqual(inventory.id, None)
        inventory.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(inventory.id)
        inventories = Inventory.all()
        self.assertEqual(len(inventories), 1)

    def test_read_a_inventory(self):
        """It should Read a Inventory"""
        inventory = Inventory(quantity=1, restock_level=3)
        logging.debug(inventory)
        inventory.id = None
        inventory.create()
        self.assertIsNotNone(inventory.id)
        # Fetch it back
        found_inventory = Inventory.find(inventory.id)
        self.assertEqual(found_inventory.id, inventory.id)
        self.assertEqual(found_inventory.name, inventory.name)
        self.assertEqual(found_inventory.category, inventory.category)