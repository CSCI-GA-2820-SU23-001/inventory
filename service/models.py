"""
Models for Inventory

All of the models are stored in this module
"""
import logging
from enum import Enum
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError 

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    Inventory.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

class Condition(Enum):
    """Enumeration of valid condition of products"""

    NEW = 1
    OPEN_BOX = 2
    USED = 3

class Inventory(db.Model):
    """
    Class that represents a Inventory
    """

    app = None

    # Table Schema
    product_id = db.Column(db.Integer, primary_key=True)
    condition = db.Column(db.Enum(Condition), server_default=(Condition.NEW.name), primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    restock_level = db.Column(db.Integer,default=1)
    last_updated_on = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Inventory product_id=[{self.product_id}] condition=[{self.condition}]>"

    def create(self):
        """
        Creates a Inventory to the database
        """
        logger.info("Creating new inventory...")
        db.session.add(self)
        try:
            db.session.commit()
        except IntegrityError:
            # error, there already is a user using this bank address or other
            # constraint failed
            db.session.rollback()
            raise

    def update(self):
        """
        Updates a Inventory to the database
        """
        logger.info("Updating inventory product_id=%s,condition=%s",self.product_id,self.condition)
        if not self.product_id:
            raise DataValidationError("Update called with empty ID field")
        if not self.condition:
            raise DataValidationError("Update called with empty Condition field")
        db.session.commit()

    def delete(self):
        """ Removes a Inventory from the data store """
        logger.info("Deleting inventory product_id=%s,condition=%s",self.product_id,self.condition)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Inventory into a dictionary """
        return {"product_id": self.product_id,
                "condition": self.condition.name,
                "quantity": self.quantity,
                "restock_level": self.restock_level,
                "last_updated_on": self.last_updated_on}

    def deserialize(self, data:dict):
        """
        Deserializes a Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_id = data["product_id"]
            self.condition = getattr(Condition, data["condition"])
            if isinstance(data["quantity"], int):
                self.quantity = data["quantity"]
            else:
                raise DataValidationError(
                    "Invalid type for integer [quantity]: "
                    + str(type(data["quantity"]))
                )
            if isinstance(data["restock_level"], int):
                self.restock_level = data["restock_level"]
            else:
                raise DataValidationError(
                    "Invalid type for integer [restock_level]: "
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
                "Invalid Inventory: body of request contained bad or no data " + str(error)
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Inventories in the database """
        logger.info("Processing all Inventories")
        return cls.query.all()

    @classmethod
    def find(cls, by_id, by_condition):
        """ Finds a Inventory by it's ID and condition """
        logger.info("Processing lookup for product_id %s and condition %s ...", by_id, by_condition)
        return cls.query.filter(cls.product_id == by_id, cls.condition == by_condition).first()

    @classmethod
    def find_or_404(cls, product_id: int, condition: Condition):
        """Find an Inventory by it's product product_id and condition

        :param product_id: the id of the Product to find
        :type condition: Condition

        :return: an instance with the Inventory, or 404_NOT_FOUND if not found
        :rtype: Inventory

        """
        logger.info("Processing lookup or 404 for product_id %s, condition %s", product_id, condition)
        return cls.query.get_or_404((product_id, condition))

    @classmethod
    def find_by_condition(cls, condition: Condition) -> list:
        """Returns all inventories by their condition

        :param condition: values are ['NEW', 'OPEN_BOX', 'USED']
        :type available: enum

        :return: a collection of inventories that are available
        :rtype: list

        """
        logger.info("Processing condition query for %s ...", condition.name)
        return cls.query.filter(cls.condition == condition)
