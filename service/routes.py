"""
Inventory Service

List, Create, Read, Update, and Delete products from the inventory database
"""
from service.models import Inventory, Condition
from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
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
    return ("<p>The inventory service keeps track of how many of each product we have in our warehouse</p>",
            status.HTTP_200_OK)
    

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
# DELETE A INVENTORY ITEM
######################################################################
@app.route("/inventory/<int:product_id>/<string:condition>", methods=["DELETE"])
def delete_inventory(product_id, condition):
    '''This endpoint will delete a product with the specified id and condition'''
    app.logger.info("Request to delete a product with product_id %s and condition %s", product_id, condition)
    product = Inventory.find(by_id=product_id, by_condition =condition)
    if product:
        product.delete()
        app.logger.info("Product with product_id %s and condition %s deleted.", product_id, condition)
    return ("", status.HTTP_204_NO_CONTENT)

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

######################################################################
# CREATE A LIST OF ITEMS
######################################################################
def build_inventory_list(_filter : bool, _condition : Condition):
    my_list = list()
    index_number = 0
    for entry in Inventory().all():

        # To avoid duplicating code, list_all_items and list_items_condition will both call this method
        # to build their lists. In list_all_items, we don't care about filtering on any condition;
        # _filter is False and _condition can be set to any value in the enum as it'll be ignored anyway
        #
        # In list_items_condition, we do care about filtering on a specified condition. _filter is True and
        # entry.condition must match _condition
        if ( (_filter and entry.condition == _condition) or _filter is False):
            my_list.append(
                            {
                                "product_id" : entry.product_id,
                                "condition" : entry.condition.name,
                                "quantity" : entry.quantity,
                                "restock_level" : entry.restock_level,

                                # twong, code crashes here if you do not convert entry.last_update_on to a string
                                # json cannot serialize DateTime objects
                                "last_updated_on" : str(entry.last_updated_on)
                            }
                        )

            # Write the current entry's info to the log
            app.logger.info("------------------------------------------------------------------")
            app.logger.info("Index : %d", index_number)
            app.logger.info("product_id : %d", entry.product_id)
            app.logger.info("condition : %s", entry.condition.name)
            app.logger.info("quantity : %d", entry.quantity)
            app.logger.info("restock_level : %d", entry.restock_level)
            app.logger.info("last_updated_on : %s", str(entry.last_updated_on))
            app.logger.info("------------------------------------------------------------------")
            index_number += 1
        # end if
    # end for

    return my_list
# end func build_inventory_list

######################################################################
# RETURN ALL ITEMS IN THE INVENTORY REGARDLESS OF CONDITION
######################################################################
@app.route("/inventory", methods=['GET'])
def list_all_items():
    app.logger.info("Request to list ALL items in the inventory...")

    # This function is expected to always return a status code of 200, unless the server is down
    # If there's nothing in the warehouse, the returned list will be empty. See build_inventory_list
    # for an explanation of the arguments being passed into it
    ret_list = build_inventory_list(False, Condition.FINAL)
    app.logger.info("There are %d items in the inventory", len(ret_list))
    return jsonify(ret_list), status.HTTP_200_OK
# end func list_all_items

######################################################################
# RETURN ALL ITEMS IN THE INVENTORY BASED ON CONDITION
######################################################################
@app.route("/inventory/<_condition>", methods=['GET'])
def list_items_condition(_condition : str):
    app.logger.info("Request to list inventory items under a specific condition: %s", _condition)
    my_cond = Condition.FINAL
    match _condition.upper():
        case "NEW":
            my_cond = Condition.NEW
        case "OPEN_BOX":
            my_cond = Condition.OPEN_BOX
        case "USED":
            my_cond = Condition.USED
        case _:
            # Default case, return HTTP 400 if the user passed in a string that isn't any of the ones above?
            return "Unknown argument " + _condition + " passed into URL", status.HTTP_400_BAD_REQUEST
    # end switch

    # See build_inventory_list for an explanation of the arguments being passed into it
    ret_list = build_inventory_list(True, my_cond)
    app.logger.info("There are %d items in the inventory with condition enum %d", len(ret_list), my_cond)
    return jsonify(ret_list), status.HTTP_200_OK
# end func list_items_condition

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
