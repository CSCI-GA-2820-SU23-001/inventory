"""
Inventory Service

List, Create, Read, Update, and Delete products from the inventory database
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Inventory
from sqlalchemy.exc import IntegrityError

# Import utilities
from service.utilities import check_content_type, check_condition_type

# Import Flask application
from . import app



######################################################################
# GET INDEX
######################################################################
@app.route("/", methods=['GET'])
def index():
    """ Root URL response """
    return (
        "<p>Reminder: return some useful information in json format about the service here</p>",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
# ADD A NEW INVENTORY ITEM
######################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """
    Creates an inventory listing for the product
    This endpoint will create an Inventory listing based on the data in the body that is posted
    """
    app.logger.info("Request to create an inventory item")
    check_content_type("application/json")
    inventory = Inventory()
    inventory.deserialize(request.get_json())
    message = ""
    status_code = status.HTTP_400_BAD_REQUEST
    try:
        inventory.create()
        message = inventory.serialize()
        status_code = status.HTTP_201_CREATED
        app.logger.info("Inventory for product with ID [%s] and condition [%s] created.", inventory.product_id, inventory.condition)
    except IntegrityError:
        message = "Primary key conflict: <%s, %s> key pair already exists in database" % (inventory.product_id, inventory.condition)
        status_code = status.HTTP_409_CONFLICT
        app.logger.info("Inventory for product with ID [%s] and condition [%s] already exists.")

    return jsonify(message), status_code



######################################################################
# UPDATE AN INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:product_id>/<string:condition>", methods=["PUT"])
def update_inventory(product_id, condition):
    """
    Updates an inventory listing for the specified product and condition
    This endpoint will update the inventory listing for the specified product and condition
    based on the data in the body that is sent in the request
    """
    app.logger.info("Request to update inventory for product with ID [%s] and condition [%s]", product_id, condition)
    check_content_type("application/json")
    check_condition_type(condition)
    inventory = Inventory.find(product_id, condition)
    if inventory is None:
        abort(status.HTTP_404_NOT_FOUND, f"Inventory not found for product with ID {product_id} and condition {condition}")

    update_json = request.get_json()
    quantity = update_json["quantity"]
    restock_level = update_json["restock_level"]

    if quantity < 0:
        abort(status.HTTP_400_BAD_REQUEST, "Quantity to be updated must be higher or equal to 0.")
    if restock_level < 0:
        abort(status.HTTP_400_BAD_REQUEST, "Restock level to be updated must be higher or equal to 0.")
    
    message = ""
    inventory.quantity = quantity
    inventory.restock_level = restock_level
    inventory.update()
    message = inventory.serialize()
    status_code = status.HTTP_200_OK
    app.logger.info("Inventory for product with ID [%s] and condition [%s] updated.", inventory.product_id, inventory.condition)

    return jsonify(message), status_code