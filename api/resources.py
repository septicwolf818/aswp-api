"""ASWP-API Resources"""
from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime, timedelta
from flask_restful import Resource, reqparse
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from app import app
from models import Center, Animal, Specie, Authenticator
from database import db
from functools import wraps

# Create JWT manager
jwt = JWTManager(app)


def log(f):
    """ASWP-API logging wrapper

    Args:
        f (function): Resource method
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        app.logger.info(
            " | ".join(
                [string for string in
                 [request.method,
                  request.host_url[:-1]+request.path,
                  str(get_jwt_identity()["center_id"])] + [str(e) for e in request.path[1:].split("/")]
                 if string]))
        return f(*args, **kwargs)
    return wrapper


class AnimalsResource(Resource):
    """ASWP-API Animals Resource

    Args:
        Resource (Type[Resource]): FlaskRESTful Resource
    """

    def get(self):
        """ASWP-API Animals GET

        Returns:
            type[Response]: Flask JSON Response with list of Animals
        """
        animals = [Animal.to_dict(a) for a in Animal.get_all()]
        if animals:
            for animal in animals:
                if animal["price"] == None:
                    animal["price"] = Specie.get_price(animal["specie"])
        return jsonify(animals=animals)

    @jwt_required
    @log
    def post(self):
        """ASWP-API Animals POST

        Returns:
            dict: Dictionary with success message
            tuple: Tuple with error message and status code
        """
        data = self.parse_request()
        price = data.get("price", None)
        description = data.get("description", None)
        center_id = get_jwt_identity()["center_id"]
        if not Specie.exists(data["specie"]):
            return {"error": "Specified specie does not exist"}, 409
        Animal.add(center_id, data["name"], description,
                   data["age"], data["specie"], price)
        return {"message": "Animal added successfully"}

    def parse_request(self):
        """ASWP-API animal create request parser

        """
        animal_create_parser = reqparse.RequestParser(bundle_errors=True)
        animal_create_parser.add_argument(
            "name", help="No name specified or it's not valid. (name:str)", required=True, type=str)
        animal_create_parser.add_argument(
            "description", default=None, required=False, type=str)
        animal_create_parser.add_argument(
            "age", help="No age specified or it's not valid. (age:int)", required=True, type=int)
        animal_create_parser.add_argument(
            "specie", help="No specie specified or it's not valid. (specie:int)", required=True, type=int)
        animal_create_parser.add_argument(
            "price", default=None, required=False, type=float)
        return animal_create_parser.parse_args(strict=True)


class AnimalResource(Resource):
    """ASWP-API Animal Resource

    Args:
        Resource (Type[Resource]): FlaskRESTful Resource
    """

    def get(self, animal_id):
        """ASWP-API Animal GET

        Args:
            animal_id (int): Animal ID

        Returns:
            type[Response]: Flask JSON Response with Animal data
            tuple: Tuple with error message and status code
        """
        animal = Animal.get_by_id(animal_id)
        if animal:
            animal = Animal.to_dict(animal)
            if animal["price"] == None:
                animal["price"] = Specie.get_price(animal["specie"])
            return jsonify(animal)
        else:
            return {"error": "Animal not found"}, 404

    @jwt_required
    @log
    def put(self, animal_id):
        """ASWP-API Animal PUT

        Args:
            animal_id (int): ID of Animal to update

        Returns:
            dict: Dictionary with success message
            tuple: Tuple with error message and status code
        """
        data = self.parse_request()
        center_id = get_jwt_identity()["center_id"]
        if not Animal.exists(animal_id):
            return {"error": "Animal not found"}, 404
        if not Animal.is_owner(animal_id, center_id):
            return {"error": "You are not allowed to update this animal"}, 403
        if "specie" in data:
            if not Specie.exists(data["specie"]):
                return {"error": "Specified specie does not exist"}, 409
        Animal.update(animal_id, data)
        return {"message": "Animal updated successfully"}

    @jwt_required
    @log
    def delete(self, animal_id):
        """ASWP-API Animal DELETE

        Args:
            animal_id (int): ID of Animal to delete

        Returns:
            dict: Dictionary with success message
            tuple: Tuple with error message and status code
        """
        center_id = get_jwt_identity()["center_id"]
        if not Animal.exists(animal_id):
            return {"error": "Animal not found"}, 404
        if not Animal.is_owner(animal_id, center_id):
            return {"error": "You are not allowed to delete this animal"}, 403
        Animal.delete(animal_id)
        return {"message": "Animal deleted successfully"}

    def parse_request(self):
        """ASWP-API animal update request parser

        """
        animal_update_parser = reqparse.RequestParser(bundle_errors=True)
        animal_update_parser.add_argument(
            "name", store_missing=False, required=False, type=str)
        animal_update_parser.add_argument(
            "description", store_missing=False, required=False, type=str)
        animal_update_parser.add_argument(
            "age", store_missing=False, required=False, type=int)
        animal_update_parser.add_argument(
            "specie", store_missing=False, required=False, type=int)
        animal_update_parser.add_argument(
            "price", store_missing=False, required=False, type=float)
        return animal_update_parser.parse_args(strict=True)


class CentersResource(Resource):
    """ASWP-API Centers Resource

    Args:
        Resource (Type[Resource]): FlaskRESTful Resource
    """

    def get(self):
        """ASWP-API Centers GET

        Returns:
            type[Response]: Flask JSON Response with list of Centers
        """
        centers = [Center.to_safe_dict(c) for c in Center.get_all()]
        return jsonify(centers=centers)


class CenterResource(Resource):
    """ASWP-API Center Resource

    Args:
        Resource (Type[Resource]): FlaskRESTful Resource
    """

    def get(self, center_id):
        """ASWP-API Center GET

        Args:
            center_id (int): Center ID

        Returns:
            type[Response]: Flask JSON Response with Center data
            tuple: Tuple with error message and status code
        """
        center = Center.get_by_id(center_id)
        if center:
            center = Center.to_safe_dict(center)
        else:
            return {"error": "Center not found"}, 404
        center_animals = [Animal.to_safe_dict(a)
                          for a in Animal.get_owned_by(center_id)]
        center["animals"] = center_animals
        return jsonify(center=center)


class SpeciesResource(Resource):
    """ASWP-API Species Resource

    Args:
        Resource (Type[Resource]): FlaskRESTful Resource
    """

    def get(self):
        """ASWP-API Species GET

        Returns:
            type[Response]: Flask JSON Response with list of Species
        """
        species = [Specie.to_dict(s) for s in Specie.get_all()]
        species_safe = [{"id": s["id"], "name":s["name"],
                         "animals_count":Animal.get_count_by_specie(s["id"])} for s in species]
        return jsonify(species=species_safe)

    @jwt_required
    @log
    def post(self):
        """ASWP-API Species POST

        Returns:
            dict: Dictionary with success message
        """
        data = self.parse_request()
        Specie.add(data["name"], data["description"], data["price"])
        return {"message": "Specie added successfully"}

    def parse_request(self):
        """ASWP-API specie create request parser

        """
        specie_create_parser = reqparse.RequestParser(bundle_errors=True)
        specie_create_parser.add_argument(
            "name", help="No name specified or it's not valid. (name:str)", required=True, type=str)
        specie_create_parser.add_argument(
            "description", help="No description specified or it's not valid. (description:str)", required=True, type=str)
        specie_create_parser.add_argument(
            "price", help="No price specified or it's not valid. (price:float)", required=True, type=float)
        return specie_create_parser.parse_args(strict=True)


class SpecieResource(Resource):
    """ASWP-API Specie Resource

    Args:
        Resource (Type[Resource]): FlaskRESTful Resource
    """

    def get(self, specie_id):
        """ASWP-API Specie GET

        Args:
            specie_id (int): Specie ID

        Returns:
            type[Response]: Flask JSON Response with Specie data
            tuple: Tuple with error message and status code
        """
        specie = Specie.get_by_id(specie_id)
        if specie:
            specie = Specie.to_dict(specie)
        else:
            return {"error": "Specie not found"}, 404
        specie_animals = [Animal.to_safe_dict(a) 
            for a in Animal.get_all_by_specie(specie_id)]
        specie["animals"] = specie_animals
        return jsonify(specie=specie)


class RegisterResource(Resource):
    """ASWP-API Register Resource

    Args:
        Resource (Type[Resource]): FlaskRESTful Resource
    """

    def post(self):
        """ASWP-API Register POST

        Returns:
            dict: Dictionary with success message
            tuple: Tuple with error message and status code
        """
        data = self.parse_request()
        if not Center.exists(data["login"]):
            Center.register(data["name"], data["login"],
                            data["password"], data["address"])
            return {"message": "Center registered successfully"}
        else:
            return {"error": "This login is already in use"}, 409

    def parse_request(self):
        """ASWP-API center register request parser

        """
        center_register_parser = reqparse.RequestParser(
            bundle_errors=True)
        center_register_parser.add_argument(
            "name", help="No name specified or it's not valid. (name:str)", required=True, type=str)
        center_register_parser.add_argument(
            "address", help="No address specified or it's not valid. (address:str)", required=True, type=str)
        center_register_parser.add_argument(
            "login", help="No login specified or it's not valid. (login:str)", required=True, type=str)
        center_register_parser.add_argument(
            "password", help="No password specified or it's not valid. (password:str)", required=True, type=str)
        return center_register_parser.parse_args(strict=True)


class LoginResource(Resource):
    """ASWP-API Login Resource

    Args:
        Resource (Type[Resource]): FlaskRESTful Resource
    """

    def get(self):
        """ASWP-API Login GET

        Returns:
            type[Response]: Flask JSON Response with JWT access token
            tuple: Tuple with error message and status code
        """
        data = self.parse_request()
        auth_result = Center.authenticate(data["login"], data["password"])
        if auth_result:
            access_token = create_access_token(
                identity={"center_id": auth_result})
            Authenticator.log_auth(auth_result)
            return jsonify(access_token=access_token)
        else:
            return {"error": "Invalid credentials"}, 401

    def parse_request(self):
        """ASWP-API center login request parser

        """
        center_login_parser = reqparse.RequestParser(bundle_errors=True)
        center_login_parser.add_argument(
            "login", help="No login specified or it's not valid. (login:str)", required=True, type=str)
        center_login_parser.add_argument(
            "password", help="No password specified or it's not valid. (password:str)", required=True, type=str)
        return center_login_parser.parse_args(strict=True)
