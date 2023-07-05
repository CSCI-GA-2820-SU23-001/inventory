"""
Inventory Service

List, Create, Read, Update, and Delete products from the inventory database
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Inventory, Condition
from sqlalchemy.exc import IntegrityError

# Import utilities
from service.utilities import check_content_type

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
# RETRIEVE AN INVENTORY
######################################################################
@app.route("/inventory/<int:product_id>/<condition>", methods=["GET"])
def get_inventories(product_id, condition):
    """
    Retrieve a single inventory

    This endpoint will return an Inventory based on the product id and condition
    """
    app.logger.info("Request for inventory with id: %s and condition %s", product_id, condition)
    my_cond = Condition.FINAL
    match condition.upper():
        case "NEW":
            my_cond = Condition.NEW
        case "OPEN_BOX":
            my_cond = Condition.OPEN_BOX
        case "USED":
            my_cond = Condition.USED
        case _:
            # Default case, return HTTP 400 if the user passed in a string that isn't any of the ones above?
            return "Unknown argument " + condition + " passed into URL", status.HTTP_400_BAD_REQUEST
    # end switch
    inventory = Inventory.find(product_id, my_cond)
    if not inventory:
        abort(status.HTTP_404_NOT_FOUND, f"Inventory with id '{product_id}' and condition '{condition}' was not found.")

    app.logger.info("Returning inventory: %s, %s", inventory.product_id, inventory.condition)
    return jsonify(inventory.serialize()), status.HTTP_200_OK
