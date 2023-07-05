"""
TestInventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import Condition, Inventory, db
from service.common import status
from tests.factories import InventoryFactory  # HTTP Status Codes


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@postgres:5432/testdb"
)
BASE_URL = "/inventory"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """
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
        self.client = app.test_client()
        db.session.query(Inventory).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()


    def _create_product_id(self, count):
            """Factory method to create products in bulk"""
            test_product_id = InventoryFactory()
            response = self.client.post(BASE_URL, json=test_product_id.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test product_id"
            )
            new_product_id = response.get_json()
            return new_product_id
    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_product(self):
        """Test deleting a product"""
        test_product = self._create_product_id(1)
        response = self.client.delete(f"{BASE_URL}/{test_product['product_id']}/{test_product['condition']}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f"{BASE_URL}/{test_product['product_id']}/{test_product['condition']}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_list_all_items(self):
        """ It should list all of the items in the inventory """
        # Test the list_all_items function in routes.py

        # Call list_all_items before adding anything; the list should be empty
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ret_list = response.get_json()
        self.assertEqual(len(ret_list), 0)

        # Add 50 inventory objects with random data into the DB
        for number in range(50):
            test_inventory = InventoryFactory()
            response = self.client.post(BASE_URL, json = test_inventory.serialize())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # end for

        # All 50 entries have been added, make sure the size of the list is 50
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ret_list = response.get_json()
        self.assertEqual(len(ret_list), 50)
    # end func test_list_all_items

    def test_list_items_condition(self):
        """ It should list items (based on input condition) in the inventory """
        # Test the list_items_condition function in routes.py

        # Call list_items_condition before adding anything; the list should be empty
        # Pass in a proper string (NEW, USED, OPEN_BOX) to ensure we don't get an HTTP 400
        response = self.client.get(BASE_URL + "/NEW")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ret_list = response.get_json()
        self.assertEqual(len(ret_list), 0)

        # Pass in an unexpected value and make sure HTTP_400_BAD_REQUEST is returned
        response = self.client.get(BASE_URL + "/FOO")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Add some hard-coded inventory objects
        test_inventory = Inventory(product_id = 1, condition = Condition.NEW, quantity = 10, restock_level = 1)
        response = self.client.post(BASE_URL, json = test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = Inventory(product_id = 2, condition = Condition.NEW, quantity = 5, restock_level = 1)
        response = self.client.post(BASE_URL, json = test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = Inventory(product_id = 3, condition = Condition.NEW, quantity = 15, restock_level = 1)
        response = self.client.post(BASE_URL, json = test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = Inventory(product_id = 4, condition = Condition.OPEN_BOX, quantity = 30, restock_level = 12)
        response = self.client.post(BASE_URL, json = test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = Inventory(product_id = 5, condition = Condition.USED, quantity = 30, restock_level = 12)
        response = self.client.post(BASE_URL, json = test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = Inventory(product_id = 6, condition = Condition.USED, quantity = 300, restock_level = 12)
        response = self.client.post(BASE_URL, json = test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = Inventory(product_id = 7, condition = Condition.USED, quantity = 100, restock_level = 12)
        response = self.client.post(BASE_URL, json = test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = Inventory(product_id = 8, condition = Condition.USED, quantity = 15, restock_level = 5)
        response = self.client.post(BASE_URL, json = test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = Inventory(product_id = 9, condition = Condition.OPEN_BOX, quantity = 15, restock_level = 5)
        response = self.client.post(BASE_URL, json = test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = Inventory(product_id = 10, condition = Condition.USED, quantity = 150, restock_level = 5)
        response = self.client.post(BASE_URL, json = test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # All entries have been added, make sure there are:
        # 3 new items
        # 5 used items
        # 2 opened items
        response = self.client.get(BASE_URL + "/NEW")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ret_list = response.get_json()
        self.assertEqual(len(ret_list), 3)

        response = self.client.get(BASE_URL + "/USED")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ret_list = response.get_json()
        self.assertEqual(len(ret_list), 5)

        response = self.client.get(BASE_URL + "/OPEN_BOX")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ret_list = response.get_json()
        self.assertEqual(len(ret_list), 2)
    # end func test_list_all_items

    def test_create_inventory_success(self):
        """It should Create a new Inventory item"""
        test_inventory = InventoryFactory()
        logging.debug("Test Inventory create successful: %s", test_inventory.serialize())
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_inventory_item = response.get_json()
        self.assertEqual(new_inventory_item["product_id"], test_inventory.product_id)
        self.assertEqual(getattr(Condition, new_inventory_item["condition"]), test_inventory.condition)
        self.assertEqual(new_inventory_item["quantity"], test_inventory.quantity)
        self.assertEqual(new_inventory_item["restock_level"], test_inventory.restock_level)


    def test_create_inventory_conflict(self):
        """It should fail to Create a new Inventory item"""
        test_inventory = InventoryFactory()
        logging.debug("Test Inventory create conflict: %s", test_inventory.serialize())
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_inventory_item = response.get_json()
        self.assertEqual(new_inventory_item["product_id"], test_inventory.product_id)
        self.assertEqual(getattr(Condition, new_inventory_item["condition"]), test_inventory.condition)
        self.assertEqual(new_inventory_item["quantity"], test_inventory.quantity)
        self.assertEqual(new_inventory_item["restock_level"], test_inventory.restock_level)

        # Retry the same POST to trigger key conflict
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_get_inventory(self):
        """It should Get a single inventory"""
        # get the id of a inventory
        test_inventory = InventoryFactory()
        logging.debug("Test Inventory create successful: %s", test_inventory.serialize())
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(f"{BASE_URL}/{test_inventory.product_id}/{test_inventory.condition.name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["product_id"], test_inventory.product_id)
        self.assertEqual(data["condition"], test_inventory.condition.name)
        self.assertEqual(data["quantity"], test_inventory.quantity)
        self.assertEqual(data["restock_level"], test_inventory.restock_level)

    def test_get_inventory_not_found(self):
        """It should not Get a inventory thats not found"""
        response = self.client.get(f"{BASE_URL}/0/NEW")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])
