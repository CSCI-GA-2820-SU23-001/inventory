"""
Utilities for Inventory API endpoints

"""

from flask import abort
from service.common import status  # HTTP Status Codes
from service.models import Condition

# Import Flask application
from . import app


######################################################################
# UTILITY FUNCTIONS
######################################################################
def check_condition_type(condition_str):
    """Checks if the given string is a product condition"""
    try:
        condition = Condition[condition_str]

        # This line was added to suppress a "make lint" error
        return condition
    except KeyError:
        app.logger.error("Invalid Condition Type.")
        abort(status.HTTP_400_BAD_REQUEST, "Invalid Condition Type.")
