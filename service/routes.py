######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
# spell: ignore Rofrano jsonify restx dbname
"""
Inventory Store Service with Swagger
Paths:
------
GET / - Displays a UI for Selenium testing
GET /inventory - Returns a list all of the Inventories
GET /inventory/{product_id}/{condition} - Returns the Inventory with a given id number
POST /inventory - Creates a new Inventory record in the database
PUT /inventory/{product_id}/{condition} - Updates an Inventory object record in the database
PUT /inventory/{product_id}/{condition}/active - Change an item's update status to enabled
DELETE /inventory/{product_id}/{condition/active - Change an item's update status to disabled
DELETE /inventory/{product_id}/{condition} - Deletes an Inventory object record in the database
"""

import sqlite3

from flask import jsonify
from flask_restx import Resource, fields
from sqlalchemy import exc
from service.models import Inventory, Condition, UpdateStatusType
from service.common import status  # HTTP Status Codes
from service.utilities import check_condition_type
from . import app, api


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """Index page"""
    return app.send_static_file("index.html")


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Inventory",
    {
        "product_id": fields.Integer(
            required=True, description="The product ID of the Inventory"
        ),
        "condition": fields.String(
            required=True,
            enum=Condition._member_names_,
            description="The condition of the item (i.e., NEW, OPEN_BOX, USED)",
        ),
        "quantity": fields.Integer(
            description="The number of copies we have of this item"
        ),
        "restock_level": fields.Integer(description="The restock level of this item"),
        "last_updated_on": fields.Date(description="The day the item was created"),
        "can_update": fields.String(
            enum=UpdateStatusType._member_names_,
            description="The update status (ENABLED, DISABLED) of the item",
        ),
    },
)
inventory_model = api.inherit(
    "InventoryModel",
    create_model,
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

update_model = api.model(
    "UpdateModel",
    {
        "quantity": fields.Integer(
            description="The number of copies we have of this item"
        ),
        "restock_level": fields.Integer(description="The restock level of this item"),
    },
)


######################################################################
#  PATH: /inventory/{product_id}/{condition}/active
######################################################################
@api.route("/inventory/<product_id>/<condition>/active")
@api.param("product_id", "The product ID")
@api.param("condition", "The condition")
class InventoryUpdateStatus(Resource):
    """
    InventoryUpdateStatus class
    Allows the manipulation of a single item's update status
    PUT /inventory/{product_id}/{condition}/active - Enable the item's update status; you can now update the item
    DELETE /inventory/{product_id}/{condition}/active - Disable the item's update status; you can no longer update the item
    """

    # ------------------------------------------------------------------
    # ENABLE ITEM UPDATES
    # ------------------------------------------------------------------
    @api.doc("enable_item_update")
    @api.response(404, "Inventory not found")
    @api.response(400, "The posted Inventory data was not valid")
    @api.marshal_with(inventory_model)
    def put(self, product_id, condition):
        """Enable updates of a product ID"""
        app.logger.info(
            "Request to enable updates of product ID %s, condition %s",
            product_id,
            condition,
        )
        check_condition_type(condition)
        inventory = Inventory.find(product_id, condition)
        if inventory is None:
            app.logger.error(
                "Tuple (%s, %s) does not exist in database", product_id, condition
            )
            abort(status.HTTP_404_NOT_FOUND, "Invalid argument specified")
        # check_condition_type already verified that condition is a valid enum value
        else:
            inventory.can_update = UpdateStatusType.ENABLED
            inventory.update()
            app.logger.info(
                "Successfully enabled updates of product ID %s, condition %s",
                product_id,
                condition,
            )
            return (
                jsonify(
                    "Successfully enabled updates of product ID "
                    + product_id
                    + " with condition "
                    + condition
                ),
                status.HTTP_200_OK,
            )

    # ------------------------------------------------------------------
    # DISABLE ITEM UPDATES
    # ------------------------------------------------------------------
    @api.doc("disable_item_update")
    @api.response(404, "Inventory not found")
    @api.response(400, "The posted Inventory data was not valid")
    @api.marshal_with(inventory_model)
    def delete(self, product_id, condition):
        """Disable updates of a product ID"""
        app.logger.info(
            "Request to disable updates of product ID %s, condition %s",
            product_id,
            condition,
        )
        check_condition_type(condition)
        inventory = Inventory.find(product_id, condition)
        if inventory is None:
            app.logger.error(
                "Tuple (%s, %s) does not exist in database", product_id, condition
            )
            abort(status.HTTP_404_NOT_FOUND, "Invalid argument specified")
        # check_condition_type already verified that condition is a valid enum value
        else:
            inventory.can_update = UpdateStatusType.DISABLED
            inventory.update()
            app.logger.info(
                "Successfully disabled updates of product ID %s, condition %s",
                product_id,
                condition,
            )
            return (
                jsonify(
                    "Successfully disabled updates of product ID "
                    + product_id
                    + " with condition "
                    + condition
                ),
                status.HTTP_204_NO_CONTENT,
            )


######################################################################
#  PATH: /inventory/{product_id}/{condition}
######################################################################
@api.route("/inventory/<product_id>/<condition>")
@api.param("product_id", "The product ID")
@api.param("condition", "The condition")
class InventoryResource(Resource):
    """
    InventoryResource class
    Allows the manipulation of a single Inventory
    GET /inventory/{product_id}/{condition} - Returns an Inventory object with the id and condition
    PUT /inventory/{product_id}/{condition} - Update an Inventory object with the id and condition
    DELETE /inventory/{product_id}/{condition} -  Deletes an Inventory object with the id and condition
    """

    # ------------------------------------------------------------------
    # RETRIEVE AN INVENTORY OBJECT
    # ------------------------------------------------------------------
    @api.doc("get_inventory")
    @api.response(404, "Inventory not found")
    @api.marshal_with(inventory_model)
    def get(self, product_id, condition):
        """
        Retrieve a single Inventory
        This endpoint will return an Inventory object based on its product ID
        """
        app.logger.info(
            "Request to Retrieve an inventory object with id [%s] and condition [%s]",
            product_id,
            condition,
        )
        check_condition_type(condition)
        inventory = Inventory.find(product_id, condition)
        if not inventory:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Inventory with id '{product_id}' and condition '{condition}' was not found.",
            )
        return inventory.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING INVENTORY
    # ------------------------------------------------------------------
    @api.doc("update_inventory")
    @api.response(404, "Inventory not found")
    @api.response(400, "The posted Inventory data was not valid")
    @api.expect(update_model)
    @api.marshal_with(inventory_model)
    def put(self, product_id, condition):
        """
        Update an Inventory object
        This endpoint will update an Inventory object based on the body that is posted
        """
        app.logger.info(
            "Request to Update an inventory object with id [%s] and condition [%s]",
            product_id,
            condition,
        )

        check_condition_type(condition)
        inventory = Inventory.find(product_id, condition)

        # end try/catch
        if not inventory:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Inventory with id '{product_id}' was not found.",
            )
        # end if
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        if data["quantity"] > 0 and data["restock_level"] > 0:
            if inventory.can_update == UpdateStatusType.ENABLED:
                inventory.quantity = data["quantity"]
                inventory.restock_level = data["restock_level"]
                inventory.update()
                return inventory.serialize(), status.HTTP_200_OK
            # end if

            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Product ID {product_id} is currently disabled and cannot be updated",
            )
        else:
            app.logger.error(
                "routes.py, InventoryResource::put, neg quantity and restock_levels args"
            )
            app.logger.error(
                "quantity: %d, restock_level: %d",
                data["quantity"],
                data["restock_level"],
            )
            return "", status.HTTP_400_BAD_REQUEST

    # ------------------------------------------------------------------
    # DELETE AN INVENTORY OBJECT
    # ------------------------------------------------------------------
    @api.doc("delete_inventory")
    @api.response(204, "Inventory deleted")
    def delete(self, product_id, condition):
        """
        Delete an Inventory object
        This endpoint will delete an Inventory object based the id specified in the path
        """
        app.logger.info(
            "Request to Delete an inventory object with id [%s] and condition [%s]",
            product_id,
            condition,
        )
        check_condition_type(condition)
        inventory = Inventory.find(product_id, condition)
        if inventory:
            inventory.delete()
            app.logger.info("Inventory with id [%s] was deleted", product_id)
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /inventory/<listFilter>
######################################################################
@api.route("/inventory/<list_filter>")
@api.param(
    "list_filter", "The filter for the type of list (NEW, OPEN_BOX, USED, RESTOCK)"
)
class InventoryListFilter(Resource):
    """Builds a filtered list"""

    # ------------------------------------------------------------------
    # LIST INVENTORIES BASED ON CONDITION OR RESTOCK
    # ------------------------------------------------------------------
    @api.doc("list_inventory_filter")
    @api.marshal_list_with(inventory_model)
    def get(self, list_filter):
        """Returns a filtered list"""
        app.logger.info("Request to list items using list_filter: %s", list_filter)
        inventory = []
        if list_filter.upper() == "NEW":
            inventory = Inventory.find_by_condition(Condition.NEW)
        elif list_filter.upper() == "OPEN_BOX":
            inventory = Inventory.find_by_condition(Condition.OPEN_BOX)
        elif list_filter.upper() == "USED":
            inventory = Inventory.find_by_condition(Condition.USED)
        elif list_filter.upper() == "RESTOCK":
            inventory = Inventory.find_by_restock()
        else:
            app.logger.info(
                "routes.py, InventoryListFilter::get error, unknown list_filter type: %s",
                list_filter,
            )
            return "", status.HTTP_400_BAD_REQUEST
        # end switch case
        app.logger.info("[%s] Inventories returned", inventory.count())
        results = [inventory.serialize() for inventory in inventory]
        return results, status.HTTP_200_OK


######################################################################
#  PATH: /inventory
######################################################################
@api.route("/inventory", strict_slashes=False)
class InventoryCollection(Resource):
    """Handles all interactions with collections of Inventories"""

    # ------------------------------------------------------------------
    # LIST ALL INVENTORIES
    # ------------------------------------------------------------------
    @api.doc("list_inventory")
    @api.marshal_list_with(inventory_model)
    def get(self):
        """Returns all of the Inventories"""
        app.logger.info("Request to list ALL Inventories...")
        inventory = Inventory.all()
        app.logger.info("[%s] Inventories returned", len(inventory))
        results = [inventory.serialize() for inventory in inventory]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW INVENTORY
    # ------------------------------------------------------------------
    @api.doc("create_inventory")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(inventory_model, code=201)
    def post(self):
        """
        Creates an Inventory object
        This endpoint will create an Inventory object based the data in the body that is posted
        """
        app.logger.info("Request to Create an Inventory object")
        inventory = Inventory()
        app.logger.debug("Payload = %s", api.payload)
        inventory.deserialize(api.payload)
        try:
            inventory.create()
        except (exc.IntegrityError, sqlite3.IntegrityError) as error:
            # It was most likely a 409 conflict, which is what we will return. But log the error message
            # anyway for more info
            app.logger.error(
                "routes.py, InventoryCollection::post, an error occurred: %s",
                error.orig.diag.message_detail,
            )
            return "", status.HTTP_409_CONFLICT
        # end try/catch block
        app.logger.info("Inventory with new id [%s] created!", inventory.product_id)
        location_url = api.url_for(
            InventoryResource,
            product_id=inventory.product_id,
            condition=inventory.condition,
            _external=True,
        )
        return (
            inventory.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)


def init_db(dbname="inventory"):
    """Initialize the model"""
    Inventory.init_db(dbname)
