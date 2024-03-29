"""
Models for Inventory
All of the models are stored in this module
"""
import logging
from enum import Enum
from datetime import datetime
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from requests import HTTPError  # pylint: disable=redefined-builtin
from retry import retry

logger = logging.getLogger("flask.app")
# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()
# global variables for retry (must be int)
RETRY_COUNT = int(os.environ.get("RETRY_COUNT", 10))
RETRY_DELAY = int(os.environ.get("RETRY_DELAY", 1))
RETRY_BACKOFF = int(os.environ.get("RETRY_BACKOFF", 2))


# Function to initialize the database
def init_db(app):
    """Initializes the SQLAlchemy app"""
    Inventory.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Condition(Enum):
    """Enumeration of valid condition of products"""

    NEW = 1
    OPEN_BOX = 2
    USED = 3
    # This is the last value in the enum and is meant to be a default value. Nothing should come after this
    FINAL = 4


# end enum Condition
class UpdateStatusType(Enum):
    """Enumeration of update status types"""

    DISABLED = (0,)
    ENABLED = (1,)
    # This is the last value in the enum and is meant to be a default value. Nothing should come after this
    UNKNOWN = 2


# end enum UpdateStatusType
class Inventory(db.Model):
    """
    Class that represents a Inventory
    """

    app = None
    # Table Schema
    product_id = db.Column(db.Integer, primary_key=True)
    condition = db.Column(
        db.Enum(Condition), server_default=(Condition.NEW.name), primary_key=True
    )
    quantity = db.Column(db.Integer, default=1)
    restock_level = db.Column(db.Integer, default=1)
    last_updated_on = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )
    can_update = db.Column(
        db.Enum(UpdateStatusType), default=UpdateStatusType.ENABLED.name
    )

    def __repr__(self):
        return (
            f"<Inventory product_id=[{self.product_id}] condition=[{self.condition}]>"
        )

    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def create(self):
        """
        Creates a Inventory to the database
        """
        logger.info("Creating new inventory...")
        try:
            db.session.add(self)
            return db.session.commit()
        except exc.IntegrityError as error:
            db.session.rollback()
            logger.error(
                "Inventory model create, an error occurred: %s",
                error,
            )
            # error, there already is a user using this bank address or other
            # constraint failed
            raise

    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def update(self):
        """
        Updates a Inventory to the database
        """
        logger.info(
            "Updating inventory product_id=%s,condition=%s",
            self.product_id,
            self.condition,
        )
        if not self.product_id:
            raise DataValidationError("Update called with empty ID field")
        if not self.condition:
            raise DataValidationError("Update called with empty Condition field")
        # Commit the changes
        db.session.commit()

    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def delete(self):
        """Removes a Inventory from the data store"""
        logger.info(
            "Deleting inventory product_id=%s,condition=%s",
            self.product_id,
            self.condition,
        )
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """Serializes a Inventory into a dictionary"""
        return {
            "product_id": self.product_id,
            "condition": self.condition.name,
            "quantity": self.quantity,
            "restock_level": self.restock_level,
            "last_updated_on": self.last_updated_on,
            "can_update": self.can_update.name,
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Inventory from a dictionary
        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_id"]
            if self.product_id <= 0:
                raise DataValidationError("data[product_id] is <= 0")
            self.condition = getattr(Condition, data["condition"])
            try:
                # We already have a function in utilities.py that checks the condition enum type
                # Check the can_update enum; if it's invalid, throw an error
                self.can_update = getattr(UpdateStatusType, data["can_update"])
            except AttributeError:
                raise DataValidationError(
                    "Invalid can_update attribute type: %s", data["can_update"]
                )
            if isinstance(data["quantity"], int) and data["quantity"] >= 1:
                self.quantity = data["quantity"]
            else:
                raise DataValidationError(
                    "Invalid type or value for integer [quantity]: "
                    + str(type(data["quantity"]))
                )
            if isinstance(data["restock_level"], int) and data["restock_level"] >= 1:
                self.restock_level = data["restock_level"]
            else:
                raise DataValidationError(
                    "Invalid type or value for integer [restock_level]: "
                    + str(type(data["restock_level"]))
                )
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Inventory: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Inventory: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def all(cls):
        """Returns all of the Inventories in the database"""
        logger.info("Processing all Inventories")
        return cls.query.all()

    @classmethod
    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def find(cls, by_id, by_condition):
        """Finds a Inventory by it's ID and condition"""
        logger.info(
            "Processing lookup for product_id %s and condition %s ...",
            by_id,
            by_condition,
        )
        return cls.query.filter(
            cls.product_id == by_id, cls.condition == by_condition
        ).first()

    @classmethod
    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def find_or_404(cls, product_id: int, condition: Condition):
        """Find an Inventory by it's product product_id and condition
        :param product_id: the id of the Product to find
        :type condition: Condition
        :return: an instance with the Inventory, or 404_NOT_FOUND if not found
        :rtype: Inventory
        """
        logger.info(
            "Processing lookup or 404 for product_id %s, condition %s",
            product_id,
            condition,
        )
        return cls.query.get_or_404((product_id, condition))

    @classmethod
    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def find_by_condition(cls, condition: Condition) -> list:
        """Returns all inventories by their condition
        :param condition: values are ['NEW', 'OPEN_BOX', 'USED']
        :type available: enum
        :return: a collection of inventories that are available
        :rtype: list
        """
        logger.info("Processing condition query for %s ...", condition.name)
        return cls.query.filter(cls.condition == condition)

    @classmethod
    @retry(
        HTTPError,
        delay=RETRY_DELAY,
        backoff=RETRY_BACKOFF,
        tries=RETRY_COUNT,
        logger=logger,
    )
    def find_by_restock(cls) -> list:
        """Returns all items that need to be restocked
        An item needs to be restocked if quantity < restock_level
        :return: a collection of inventories that need to be restocked
        :rtype: list
        """
        logger.info("Returning items that need to be restocked")
        return cls.query.filter(cls.quantity < cls.restock_level)
