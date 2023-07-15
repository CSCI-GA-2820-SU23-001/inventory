"""
Utilities for Inventory API endpoints

"""

from flask import request, abort
from service.common import status  # HTTP Status Codes

# Import Flask application
from . import app

from service.models import Condition


######################################################################
# UTILITY FUNCTIONS
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


def check_condition_type(condition_str):
    """Checks if the given string is a product condition"""
    try:
        condition = Condition[condition_str]

        # This line was added to suppress a "make lint" error
        return condition
    except KeyError:
        app.logger.error("Invalid Condition Type.")
        abort(status.HTTP_400_BAD_REQUEST, "Invalid Condition Type.")
