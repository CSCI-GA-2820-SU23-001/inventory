"""
My Service

Describe what your service does here
"""

from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Inventory

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

# Place your REST API code here ...

######################################################################
# DELETE A RECOMMENDATION
######################################################################

@app.route("/inventory/<int:id>", methods=["DELETE"])
def delete_inventory(id):
    app.logger.info("Request to delete inventory with ID %s", id)
    product_id = Inventory.find(id)
    if product_id:
        condition = product_id.condition
        if condition == Condition.NEW:
            product_id.delete(id)
            app.logger.info("Inventory with ID %s and condition %s deleted successfully.", id, condition)
            return "", status.HTTP_204_NO_CONTENT
        else:
            app.logger.info("Cannot delete inventory with ID %s and condition %s.", id, condition)
            return "Cannot delete inventory with the specified condition.", status.HTTP_403_FORBIDDEN
    else:
        app.logger.info("Inventory with ID %s not found.", id)
        return "", status.HTTP_404_NOT_FOUND
