"""
TestInventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import logging
from service.models import Condition
from service.common import status
from tests.factories import InventoryFactory  # HTTP Status Codes
from tests.parent_models import TestResourceServer
from sqlalchemy.exc import IntegrityError

BASE_URL = "/api/inventory"


class TestYourResourceServerHealth(TestResourceServer):
    """Test Cases for Inventory Resource Server Health"""

    def test_health(self):
        """It should call the health endpoint"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class TestYourResourceServerIndex(TestResourceServer):
    """Test Cases for Inventory Resource Server Index"""

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class TestYourResourceServerDelete(TestResourceServer):
    """Test Cases for Inventory Resource Server Delete"""

    def _create_product_id(self):
        """Factory method to create products in bulk"""
        test_product_id = InventoryFactory()
        response = self.client.post(BASE_URL, json=test_product_id.serialize())
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Could not create test product_id",
        )
        new_product_id = response.get_json()
        return new_product_id

    def test_delete_product(self):
        """Test deleting a product"""
        test_product = self._create_product_id()
        response = self.client.delete(
            f"{BASE_URL}/{test_product['product_id']}/{test_product['condition']}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(
            f"{BASE_URL}/{test_product['product_id']}/{test_product['condition']}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product_with_invalid_details(self):
        """Test deleting a product"""
        response = self.client.delete(f"{BASE_URL}/0/OPEN_BOX")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TestYourResourceServerList(TestResourceServer):
    """Test Cases for Inventory Resource Server List"""

    def test_list_all_items(self):
        """It should list all of the items in the inventory"""
        # Test the list_all_items function in routes.py

        # Call list_all_items before adding anything; the list should be empty
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ret_list = response.get_json()
        self.assertEqual(len(ret_list), 0)

        # Add 50 inventory objects with random data into the DB
        for _ in range(50):
            test_inventory = InventoryFactory()
            response = self.client.post(BASE_URL, json=test_inventory.serialize())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # end for

        # All 50 entries have been added, make sure the size of the list is 50
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ret_list = response.get_json()
        self.assertEqual(len(ret_list), 50)

    # end func test_list_all_items

    def test_list_items_criteria_condition(self):
        """It should list items (based on input condition NEW, OPEN_BOX, USED) in the inventory"""

        # Call list_items_criteria before adding anything; the list should be empty
        # Pass in a proper string (NEW, USED, OPEN_BOX) to ensure we don't get an HTTP 400
        response = self.client.get(BASE_URL + "/NEW")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ret_list = response.get_json()
        self.assertEqual(len(ret_list), 0)

        # Pass in an unexpected value and make sure HTTP_400_BAD_REQUEST is returned
        response = self.client.get(BASE_URL + "/FOO")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Add some hard-coded inventory objects
        test_inventory = InventoryFactory(
            product_id=1, condition=Condition.NEW, quantity=10, restock_level=1
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=2, condition=Condition.NEW, quantity=5, restock_level=1
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=3, condition=Condition.NEW, quantity=15, restock_level=1
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=4, condition=Condition.OPEN_BOX, quantity=30, restock_level=12
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=5, condition=Condition.USED, quantity=30, restock_level=12
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=6, condition=Condition.USED, quantity=300, restock_level=12
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=7, condition=Condition.USED, quantity=100, restock_level=12
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=8, condition=Condition.USED, quantity=15, restock_level=5
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=9, condition=Condition.OPEN_BOX, quantity=15, restock_level=5
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=10, condition=Condition.USED, quantity=150, restock_level=5
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
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

    # end func test_list_items_criteria_condition

    def test_list_items_criteria_restock(self):
        """It should list items we're running low on (based on restock level) in the inventory"""

        # Add some hard-coded inventory objects
        test_inventory = InventoryFactory(
            product_id=1, condition=Condition.NEW, quantity=10, restock_level=11
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=2, condition=Condition.NEW, quantity=50, restock_level=60
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=3, condition=Condition.NEW, quantity=5, restock_level=1
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=4, condition=Condition.OPEN_BOX, quantity=30, restock_level=35
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=5, condition=Condition.USED, quantity=20, restock_level=20
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=6, condition=Condition.USED, quantity=500, restock_level=120
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=7, condition=Condition.USED, quantity=100, restock_level=120
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=8, condition=Condition.USED, quantity=15, restock_level=50
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=9, condition=Condition.OPEN_BOX, quantity=88, restock_level=95
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory = InventoryFactory(
            product_id=10, condition=Condition.USED, quantity=150, restock_level=150
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(BASE_URL + "/RESTOCK")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ret_list = response.get_json()

        # there are 6 entries from above where quantity < restock_level
        self.assertEqual(len(ret_list), 6)

    # end func test_list_items_criteria_restock


class TestYourResourceServerCreate(TestResourceServer):
    """Test Cases for Inventory Resource Server Create"""

    def test_create_inventory_success(self):
        """It should Create a new Inventory item"""
        test_inventory = InventoryFactory()
        logging.debug(
            "Test Inventory create successful: %s", test_inventory.serialize()
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_inventory_item = response.get_json()
        self.assertEqual(new_inventory_item["product_id"], test_inventory.product_id)
        self.assertEqual(
            getattr(Condition, new_inventory_item["condition"]),
            test_inventory.condition,
        )
        self.assertEqual(new_inventory_item["quantity"], test_inventory.quantity)
        self.assertEqual(
            new_inventory_item["restock_level"], test_inventory.restock_level
        )

    def test_create_inventory_conflict(self):
        """It should fail to Create a new Inventory item"""
        test_inventory = InventoryFactory()
        logging.debug("Test Inventory create conflict: %s", test_inventory.serialize())
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_inventory_item = response.get_json()
        self.assertEqual(new_inventory_item["product_id"], test_inventory.product_id)
        self.assertEqual(
            getattr(Condition, new_inventory_item["condition"]),
            test_inventory.condition,
        )
        self.assertEqual(new_inventory_item["quantity"], test_inventory.quantity)
        self.assertEqual(
            new_inventory_item["restock_level"], test_inventory.restock_level
        )

        # Retry the same POST to trigger key conflict
        try:
            response = self.client.post(BASE_URL, json=test_inventory.serialize())
            self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        except IntegrityError as error:
            logging.debug("Inventory item %s threw a conflict error as intended", test_inventory.serialize())

    def test_create_with_no_content_type(self):
        """Specifying some raw string with no type for the post request, it should report a 415 error"""
        response = self.client.post(BASE_URL, data="some raw string")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_with_invalid_content_type(self):
        """Specifying some other type for the post request, it should report a 415 error"""
        data = "key1=value1&key2=value2"
        response = self.client.post(
            BASE_URL, data=data, content_type="application/x-www-form-urlencoded"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class TestYourResourceServerUpdate(TestResourceServer):
    """Test Cases for Inventory Resource Server Update"""

    def test_update_normally(self):
        """Update normally"""
        test_inventory = InventoryFactory(product_id=1, condition=Condition.NEW)
        self.client.post(BASE_URL, json=test_inventory.serialize())
        update_url = BASE_URL + "/" + str(test_inventory.product_id) + "/NEW"
        update_quantity = test_inventory.quantity + 2
        update_restock_level = test_inventory.restock_level + 1
        response = self.client.put(
            update_url,
            json={"quantity": update_quantity, "restock_level": update_restock_level},
        )
        test_inventory_json = response.get_json()
        self.assertEqual(int(test_inventory_json["quantity"]), update_quantity)
        self.assertEqual(
            int(test_inventory_json["restock_level"]), update_restock_level
        )

    def test_update_non_existing_item(self):
        """Update a non-existing item, should report a 404 error"""
        update_url = BASE_URL + "/1/NEW"
        response = self.client.put(
            update_url, json={"quantity": 10, "restock_level": 5}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_negative_quantity(self):
        """Update a negative quantity, should report a 400 error"""
        test_inventory = InventoryFactory(product_id=1, condition=Condition.NEW)
        self.client.post(BASE_URL, json=test_inventory.serialize())
        update_url = BASE_URL + "/" + str(test_inventory.product_id) + "/NEW"
        update_quantity = -1
        update_restock_level = test_inventory.restock_level + 1
        response = self.client.put(
            update_url,
            json={"quantity": update_quantity, "restock_level": update_restock_level},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_negative_restock_level(self):
        """Update a negative restock level, should report a 400 error"""
        test_inventory = InventoryFactory(product_id=1, condition=Condition.NEW)
        self.client.post(BASE_URL, json=test_inventory.serialize())
        update_url = BASE_URL + "/" + str(test_inventory.product_id) + "/NEW"
        update_quantity = test_inventory.quantity + 2
        update_restock_level = -2
        response = self.client.put(
            update_url,
            json={"quantity": update_quantity, "restock_level": update_restock_level},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_using_non_condition_value(self):
        """Run test_update_using_non_condition_value method"""
        # Update an inventory by specifying a string which is not a part of Condition class
        # should be handled by check_condition_type function and report a 400 error"""
        test_inventory = InventoryFactory(product_id=1, condition=Condition.NEW)
        self.client.post(BASE_URL, json=test_inventory.serialize())
        update_url = BASE_URL + "/" + str(test_inventory.product_id) + "/EEEE"
        update_quantity = test_inventory.quantity + 2
        update_restock_level = test_inventory.restock_level + 1
        response = self.client.put(
            update_url,
            json={"quantity": update_quantity, "restock_level": update_restock_level},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestYourResourceServerGet(TestResourceServer):
    """Test Cases for Inventory Resource Server Get"""

    def test_get_inventory(self):
        """It should Get a single inventory"""
        # get the id of a inventory
        test_inventory = InventoryFactory(
            product_id=5, condition=Condition.NEW, quantity=30, restock_level=12
        )
        logging.debug(
            "Test Inventory create successful: %s", test_inventory.serialize()
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            f"{BASE_URL}/{test_inventory.product_id}/{test_inventory.condition.name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["product_id"], test_inventory.product_id)
        self.assertEqual(data["condition"], test_inventory.condition.name)
        self.assertEqual(data["quantity"], test_inventory.quantity)
        self.assertEqual(data["restock_level"], test_inventory.restock_level)

        # Now do OPEN_BOX
        test_inventory = InventoryFactory(
            product_id=5, condition=Condition.OPEN_BOX, quantity=30, restock_level=12
        )
        logging.debug(
            "Test Inventory create successful: %s", test_inventory.serialize()
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            f"{BASE_URL}/{test_inventory.product_id}/{test_inventory.condition.name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["product_id"], test_inventory.product_id)
        self.assertEqual(data["condition"], test_inventory.condition.name)
        self.assertEqual(data["quantity"], test_inventory.quantity)
        self.assertEqual(data["restock_level"], test_inventory.restock_level)

        # Now do USED
        test_inventory = InventoryFactory(
            product_id=5, condition=Condition.USED, quantity=30, restock_level=12
        )
        logging.debug(
            "Test Inventory create successful: %s", test_inventory.serialize()
        )
        response = self.client.post(BASE_URL, json=test_inventory.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(
            f"{BASE_URL}/{test_inventory.product_id}/{test_inventory.condition.name}"
        )
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

        response = self.client.get(f"{BASE_URL}/0/FINAL")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestYourResourceServerEnableDisableUpdate(TestResourceServer):
    """Test Cases for Inventory Resource Server Enable and Disable Update"""

    def test_enable_disable_update_action(self):
        """Test the functionality of the enable/disable update action"""

        # Add things to the DB
        test_inventory_first = InventoryFactory(
            product_id=1, condition=Condition.NEW, quantity=100, restock_level=10
        )
        response = self.client.post(BASE_URL, json=test_inventory_first.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory_second = InventoryFactory(
            product_id=2, condition=Condition.OPEN_BOX, quantity=100, restock_level=10
        )
        response = self.client.post(BASE_URL, json=test_inventory_second.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Now disable updates for product ID 1
        response = self.client.delete(
            BASE_URL + "/" + str(test_inventory_first.product_id) + "/NEW/active"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Try updating product ID 1
        update_quantity = test_inventory_first.quantity + 2
        update_restock_level = test_inventory_first.restock_level + 1
        response = self.client.put(
            BASE_URL + "/" + str(test_inventory_first.product_id) + "/NEW",
            json={"quantity": update_quantity, "restock_level": update_restock_level},
        )

        # Failure
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # But product ID 2 can freely be updated as it is still enabled
        update_quantity = test_inventory_second.quantity + 2
        update_restock_level = test_inventory_second.restock_level + 1
        response = self.client.put(
            BASE_URL + "/" + str(test_inventory_second.product_id) + "/OPEN_BOX",
            json={"quantity": update_quantity, "restock_level": update_restock_level},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Disabling product ID 1 should do nothing as it is still disabled
        response = self.client.delete(
            BASE_URL + "/" + str(test_inventory_first.product_id) + "/NEW/active"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Similarly, enabling product ID 2 should do nothing as it is still enabled
        response = self.client.put(
            BASE_URL + "/" + str(test_inventory_second.product_id) + "/OPEN_BOX/active"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Enable product ID 1 back
        response = self.client.put(
            BASE_URL + "/" + str(test_inventory_first.product_id) + "/NEW/active"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Product ID 1 can now be updated
        update_quantity = test_inventory_first.quantity + 2
        update_restock_level = test_inventory_first.restock_level + 1
        response = self.client.put(
            BASE_URL + "/" + str(test_inventory_first.product_id) + "/NEW",
            json={"quantity": update_quantity, "restock_level": update_restock_level},
        )

        # Success
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # end func test_update_inventory_after_disable

    def test_enable_disable_update_action_error_handler(self):
        """Test the error handler of the enable/disable update action"""

        # Add things to the DB
        test_inventory_first = InventoryFactory(
            product_id=1, condition=Condition.NEW, quantity=100, restock_level=10
        )
        response = self.client.post(BASE_URL, json=test_inventory_first.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        test_inventory_second = InventoryFactory(
            product_id=2, condition=Condition.NEW, quantity=100, restock_level=10
        )
        response = self.client.post(BASE_URL, json=test_inventory_second.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Try disabling updates to product ID 3 (doesn't exist)
        response = self.client.delete(BASE_URL + "/3/NEW/active")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try enabling updates to product ID 4 (doesn't exist)
        response = self.client.put(BASE_URL + "/4/USED/active")

        # Error
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # end func test_enable_disable_update_action_error_handler
