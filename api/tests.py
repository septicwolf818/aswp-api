import unittest
from config import config
from database import db
import main
from app import app, api


app.config["SQLALCHEMY_DATABASE_URI"] = config["TESTING"]["SQLALCHEMY_DATABASE_URI"]
api_tester = app.test_client()


class ApiTests(unittest.TestCase):
    """ASWP-API Tests

    Args:
        unittest (Type[TestCase]): unittest TestCase
    """

    def setUp(self):
        """unittest setup method
        """
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """unittest teardown method
        """
        with app.app_context():
            db.drop_all()

    def test_register(self):
        """ASWP-API - Test for successfull Center register
        """
        self.assertEqual("Center registered successfully",
                         api_tester.post(
                             "/register",
                             data='{"login":"login","password":"password","name":"Name", "address":"Address"}',
                             content_type="application/json")
                         .get_json()
                         ["message"])

    def test_login(self):
        """ASWP-API - Test for successfull Center login
        """
        api_tester.post(
            "/register",
            data='{"login":"login","password":"password","name":"Name", "address":"Address"}',
            content_type="application/json")

        self.assertIn("access_token",
                      api_tester.get(
                          "/login",
                          data='{"login":"login","password":"password"}',
                          content_type="application/json")
                      .get_json())

    def test_add_specie(self):
        """ASWP-API - Test for successfull Specie addition
        """
        api_tester.post(
            "/register",
            data='{"login":"login","password":"password","name":"Name", "address":"Address"}',
            content_type="application/json")

        access_token = api_tester.get(
            "/login",
            data='{"login":"login","password":"password"}',
            content_type="application/json").get_json()["access_token"]

        self.assertEqual("Specie added successfully",
                         api_tester.post(
                             "/species",
                             data='{"name": "Specie name","price": 150,"description": "Specie description"}',
                             content_type="application/json",
                             headers={"Authorization": "Bearer {access_token}".format(access_token=access_token)})
                         .get_json()["message"])
