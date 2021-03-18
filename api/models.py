"""ASWP-API SQLAlchemy Models"""

from flask_sqlalchemy import SQLAlchemy
from database import db
from datetime import datetime


class Center(db.Model):
    """ASWP-API SQLAlchemy Center model

    Args:
        db.Model (Type[Model]): SQLAlchemy Model
    """
    __tablename__ = "centers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    login = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(128), nullable=False)

    def register(_name, _login, _password, _address):
        """Register new Center in database

        Args:
            _name (str): New Center name
            _login (str): New Center login
            _password (str): New Center password
            _address (str): New Center address
        """
        new_center = Center(name=_name, login=_login,
                            password=_password, address=_address)
        db.session.add(new_center)
        db.session.commit()

    def exists(_login):
        """Check if Center exist for specified login

        Args:
            _login (str): Login to search in database

        Returns:
            bool: True if Center is in database, otherwise False
        """
        center = Center.query.filter_by(login=_login).first()
        return bool(center)

    def get_by_id(_id):
        """Get Center from database using ID

        Args:
            _id (int): ID to search in database

        Returns:
            Center: SQLAlchemy Center model with all stored data
            None: Center not found 
        """
        center = Center.query.filter_by(id=_id).first()
        return center

    def get_all():
        """Get all Centers from database

        Returns:
            list: List of all Centers in database
        """
        return Center.query.all()

    def authenticate(_login, _password):
        """Authenticate Center by login and password 

        Args:
            _login (str): Center login
            _password (str): Center password

        Returns:
            int: Center ID if matching credentials found
            None: Center not found
        """
        center = Center.query.filter_by(
            login=_login, password=_password).first()
        if center:
            return center.id
        else:
            return None

    def to_dict(_obj):
        """Convert SQLAlchemy Center model to dictionary

        Args:
            _obj (Model): SQLAlchemy Center model to convert

        Returns:
            dict: Dictionary with all the data
        """
        return {i.name: getattr(_obj, i.name) for i in _obj.__table__.columns}

    def to_safe_dict(_obj):
        """Convert SQLAlchemy Center model to dictionary without sensitive data

        Args:
            _obj (Model): SQLAlchemy Center model to convert

        Returns:
            dict: Dictionary with all the data
        """
        return {i.name: getattr(_obj, i.name) for i in _obj.__table__.columns if not i.name in ["login", "password", "address"]}


class Animal(db.Model):
    """ASWP-API SQLAlchemy Animal model

    Args:
        db.Model (Type[Model]): SQLAlchemy Model
    """
    __tablename__ = "animals"
    id = db.Column(db.Integer, primary_key=True)
    center_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(1024), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    specie = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=True)

    def add(_center_id, _name, _description, _age, _specie, _price):
        """Add new animal to database

        Args:
            _center_id (int): ID of the Center creating a new Animal
            _name (str): Name of the new Animal
            _description (str): Description of the new Animal (Can be None)
            _age (int): Age of the new Animal
            _specie (int): ID of the new Animal's specie
            _price (flat): Price of the new Animal (Can be None)
        """
        new_animal = Animal(center_id=_center_id, name=_name,
                            description=_description, age=_age, specie=_specie, price=_price)
        db.session.add(new_animal)
        db.session.commit()

    def get_by_id(_id):
        """Get Animal from database using ID

        Args:
            _id (int): ID to search in database

        Returns:
            Animal: SQLAlchemy Animal model with all stored data
            None: Animal not found 
        """
        animal = Animal.query.filter_by(id=_id).first()
        return animal

    def get_owned_by(_center_id):
        """Get all animals added by Center with specified ID

        Args:
            _center_id (int): ID to search in database

        Returns:
            list: List of all animals added to database by specified Center 
        """
        animals = Animal.query.filter_by(center_id=_center_id).all()
        return animals

    def get_all_by_specie(_specie_id):
        """Get all Animals from database with specified specie

        Args:
            _specie_id (int): Specie ID to search in database

        Returns:
            list: List of all Animals with specified specie
        """
        return Animal.query.filter_by(specie=_specie_id).all()

    def get_count_by_specie(_specie_id):
        """Get Animals count with specified specie

        Args:
            _specie_id (int): Specie ID to search in database

        Returns:
            int: Count of Animals with specified specie
        """
        animals = Animal.query.filter_by(specie=_specie_id).all()
        return len(animals)

    def get_all():
        """Get all Animals from database

        Returns:
            list: List of all Animals in database
        """
        return Animal.query.all()

    def exists(_animal_id):
        """Check if Animal exist for specified ID

        Args:
            _animal_id (int): ID to search in database

        Returns:
            bool: True if Animal is in database, otherwise False
        """
        animal = Animal.query.filter_by(id=_animal_id).first()
        return bool(animal)

    def is_owner(_animal_id, _center_id):
        """Check if specified Center is owner of the specified Animal

        Args:
            _animal_id (int): Animal's ID
            _center_id (int): Center's ID

        Returns:
            bool: True if specified Center ID matches Animal's Center ID
        """
        animal = Animal.query.filter_by(id=_animal_id).first()
        return animal.center_id == _center_id

    def update(_animal_id, _update_data):
        """Update Animal in database

        Args:
            _animal_id (int): ID of the animal to update
            _update_data (dict): Dictionary containing Animal's update data
        """
        animal = Animal.query.filter_by(id=_animal_id).first()
        for key in _update_data.keys():
            if key == "name":
                animal.name = _update_data[key]
            elif key == "description":
                animal.description = _update_data[key]
            elif key == "age":
                animal.age = _update_data[key]
            elif key == "specie":
                animal.specie = _update_data[key]
            elif key == "price":
                animal.price = _update_data[key]
        db.session.commit()

    def delete(_animal_id):
        """Delete Animal from database

        Args:
            _animal_id (int): ID of the Animal to delete
        """
        animal = Animal.query.filter_by(id=_animal_id).first()
        db.session.delete(animal)
        db.session.commit()

    def to_dict(_obj):
        """Convert SQLAlchemy Animal model to dictionary

        Args:
            _obj (Model): SQLAlchemy Animal model to convert

        Returns:
            dict: Dictionary with all the data
        """
        return {i.name: getattr(_obj, i.name) for i in _obj.__table__.columns}

    def to_safe_dict(_obj):
        """Convert SQLAlchemy Animal model to dictionary without owner data

        Args:
            _obj (Model): SQLAlchemy Animal model to convert

        Returns:
            dict: Dictionary with all the data
        """
        return {i.name: getattr(_obj, i.name) for i in _obj.__table__.columns if i.name in ["name", "id", "specie"]}


class Specie(db.Model):
    """ASWP-API SQLAlchemy Specie model

    Args:
        db.Model (Type[Model]): SQLAlchemy Model
    """
    __tablename__ = "species"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(1024), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def add(_name, _description, _price):
        """Add new specie to database

        Args:
            _name (str): Name of the new Specie
            _description (str): Description of the new Specie
            _price (float): Price of the new Specie
        """
        new_specie = Specie(name=_name, description=_description, price=_price)
        db.session.add(new_specie)
        db.session.commit()

    def get_all():
        """Get all Species from database

        Returns:
            list: List of all Species in database
        """
        return Specie.query.all()

    def get_by_id(_id):
        """Get Specie from database using ID

        Args:
            _id (int): ID to search in database

        Returns:
            Specie: SQLAlchemy Specie model with all stored data
            None: Specie not found 
        """
        specie = Specie.query.filter_by(id=_id).first()
        return specie

    def get_price(_specie_id):
        """Get price of the specified Specie

        Args:
            _specie_id (int): Specie ID to search in database

        Returns:
            float: Price of the specified Specie
            None: Specie not found
        """
        specie = Specie.query.filter_by(id=_specie_id).first()
        if specie:
            return specie.price
        else:
            return None

    def exists(_specie_id):
        """Check if Specie exist for specified ID

        Args:
            _specie_id (int): ID to search in database

        Returns:
            bool: True if Specie is in database, otherwise False
        """
        specie = Specie.query.filter_by(id=_specie_id).first()
        return bool(specie)

    def to_dict(_obj):
        """Convert SQLAlchemy Specie model to dictionary

        Args:
            _obj (Model): SQLAlchemy Specie model to convert

        Returns:
            dict: Dictionary with all the data
        """
        return {i.name: getattr(_obj, i.name) for i in _obj.__table__.columns}


class Authenticator(db.Model):
    """ASWP-API SQLAlchemy Authenticator model

    Args:
        db.Model (Type[Model]): SQLAlchemy Model
    """
    __tablename__ = "auths"
    id = db.Column(db.Integer, primary_key=True)
    center_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.TIMESTAMP, nullable=False)

    def log_auth(_center_id):
        """Save authentication log to database

        Args:
            _center_id (int): ID of the Center that is being authenticated
        """
        new_log = Authenticator(center_id=_center_id,
                                timestamp=datetime.utcnow())
        db.session.add(new_log)
        db.session.commit()
