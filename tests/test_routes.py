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


    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

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


    def test_update_normally(self):
        """Update normally"""
        test_inventory = InventoryFactory(condition=Condition.NEW)
        response_create = self.client.post(BASE_URL, json=test_inventory.serialize())
        update_url = BASE_URL + "/" + str(test_inventory.product_id) + "/NEW" 
        update_quantity = test_inventory.quantity + 2
        update_restock_level = test_inventory.restock_level + 1
        response = self.client.put(update_url, json={"quantity": update_quantity, "restock_level": update_restock_level})
        test_inventory_json = response.get_json()
        self.assertEqual(int(test_inventory_json["quantity"]), update_quantity)
        self.assertEqual(int(test_inventory_json["restock_level"]), update_restock_level)


    def test_update_non_existing_item(self):
        """Update a non-existing item, should report a 404 error"""
        update_url = BASE_URL + "/1/NEW"
        response = self.client.put(update_url, json={"quantity": 10, "restock_level": 5})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_update_negative_quantity(self):
        """Update a negative quantity, should report a 400 error"""
        test_inventory = InventoryFactory(condition=Condition.NEW)
        response_create = self.client.post(BASE_URL, json=test_inventory.serialize())
        update_url = BASE_URL + "/" + str(test_inventory.product_id) + "/NEW" 
        update_quantity = -1
        update_restock_level = test_inventory.restock_level + 1
        response = self.client.put(update_url, json={"quantity": update_quantity, "restock_level": update_restock_level})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_update_negative_restock_level(self):
        """Update a negative restock level, should report a 400 error"""
        test_inventory = InventoryFactory(condition=Condition.NEW)
        response_create = self.client.post(BASE_URL, json=test_inventory.serialize())
        update_url = BASE_URL + "/" + str(test_inventory.product_id) + "/NEW" 
        update_quantity = test_inventory.quantity + 2
        update_restock_level = -2
        response = self.client.put(update_url, json={"quantity": update_quantity, "restock_level": update_restock_level})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_update_using_non_condition_value(self):
        """Update an inventory by specifying a string which is not a part of Condition class, should be handled by check_condition_type function and report a 400 error"""
        test_inventory = InventoryFactory(condition=Condition.NEW)
        response_create = self.client.post(BASE_URL, json=test_inventory.serialize())
        update_url = BASE_URL + "/" + str(test_inventory.product_id) + "/EEEE" 
        update_quantity = test_inventory.quantity + 2
        update_restock_level = test_inventory.restock_level + 1
        response = self.client.put(update_url, json={"quantity": update_quantity, "restock_level": update_restock_level})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)