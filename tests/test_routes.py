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

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_inventory(self):
        """It should Delete a Inventory"""
        test_inventory = Inventory(product_id=1, condition=Condition.NEW.name, quantity=10, restock_level=1)
        response = self.client.delete(f"{BASE_URL}/{test_inventory.product_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # Make sure it is deleted
        response = self.client.get(f"{BASE_URL}/{test_inventory.product_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)