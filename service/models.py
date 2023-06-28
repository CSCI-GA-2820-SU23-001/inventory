"""
Models for Inventory

All of the models are stored in this module
"""
import logging
from enum import Enum
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

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
    id = db.Column(db.Integer, primary_key=True)
    condition = db.Column(db.Enum(Condition), server_default=(Condition.NEW.name), primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    restock_level = db.Column(db.Integer,default=1)
    last_updated_on = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


    def __repr__(self):
        return f"<Inventory id=[{self.id}] condition=[{self.condition}]>"

    def create(self):
        """
        Creates a Inventory to the database
        """
        logger.info("Creating new inventory...")
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Inventory to the database
        """
        logger.info("Updating inventory id=%s , condition=%s", self.id, self.condition)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a Inventory from the data store """
        logger.info("Deleting inventory id=%s , condition=%s", self.id, self.condition)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Inventory into a dictionary """
        return {"id": self.id,
                "condition": self.condition.name,
                "quantity": self.quantity,
                "restock_level": self.restock_level}

    def deserialize(self, data:dict):
        """
        Deserializes a Inventory from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data["id"]
            self.condition = getattr(Condition, data["condition"])
            if isinstance(data["quantity"], int):
                self.quantity = data["quantity"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [quantity]: "
                    + str(type(data["quantity"]))
                )
            if isinstance(data["restock_level"], int):
                self.restock_level = data["restock_level"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [restock_level]: "
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
        """ Returns all of the Inventorys in the database """
        logger.info("Processing all Inventorys")
        return cls.query.all()

    # @classmethod
    # def find(cls, by_id):
    #     """ Finds a Inventory by it's ID """
    #     logger.info("Processing lookup for id %s ...", by_id)
    #     return cls.query.get(by_id)

    @classmethod
    def find(cls, by_id, by_condition):
        """ Finds a Inventory by it's ID and condition """
        logger.info("Processing lookup for id %s and condition %s ...", by_id, by_condition)
        return cls.query.filter(cls.id == by_id, cls.condition == by_condition).first()

    @classmethod
    def find_by_name(cls, name):
        """Returns all Inventorys with the given name

        Args:
            name (string): the name of the Inventorys you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
