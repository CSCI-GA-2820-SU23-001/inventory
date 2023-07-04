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
from service.models import db
from service.common import status  # HTTP Status Codes
from service.models import Inventory
from service.models import Condition
from tests.factories import InventoryFactory
BASE_URL = "/inventory"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestYourResourceServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """

    def setUp(self):
        """ This runs before each test """
        self.client = app.test_client()

    def tearDown(self):
        """ This runs after each test """

    def _create_product_id(self, count):
            """Factory method to create pets in bulk"""
            product_id = []
            for _ in range(count):
                test_product_id = InventoryFactory()
                response = self.client.post(BASE_URL, json=test_product_id.serialize())
                self.assertEqual(
                    response.status_code, status.HTTP_201_CREATED, "Could not create test product_id"
                )
                new_product_id = response.get_json()
                test_product_id.id = new_product_id["id"]
                product_id.append(test_product_id)
            return product_id
    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_product(self):
        """Test deleting a product"""
        test_product = self._create_products(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_product['product_id']}/{test_product['condition']}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(f"{BASE_URL}/{test_product['product_id']}/{test_product['condition']}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)