"""
My Service

Describe what your service does here
"""
from service.models import Inventory, Condition
from flask import Flask, jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes


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

@app.route("/Inventory/<int:product_id>/<string:condition>", methods=["DELETE"])
def delete_recommendation(product_id, condition):
    '''This endpoint will delete a product with the specified id and condition'''
    app.logger.info("Request to delete a product with product_id %s and condition %s", product_id, condition)
    product = Inventory.query.filter_by(product_id=product_id, condition=condition).first()
    if product:
        product.delete()
        # db.session.commit()
    app.logger.info("Product with product_id %s and condition %s deleted.", product_id, condition)
    return "", status.HTTP_204_NO_CONTENT