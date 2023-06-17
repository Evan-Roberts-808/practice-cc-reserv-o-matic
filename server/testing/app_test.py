import json
import os

os.environ["DB_URI"] = "sqlite:///:memory:"

from flask import request
import pytest
from sqlalchemy.exc import IntegrityError
from app import app, db
from models import Customer, Location, Reservation


class TestApp:
    """Flask application in app.py"""

    def test_gets_customers(self):
        """retrieves customers with GET requests to /customers."""

        with app.app_context():
            db.create_all()
            Customer.query.delete()
            db.session.commit()
            clark = Customer(
                name="Clark Kent", email="clarkkent@dailyplanet.com"
            )
            db.session.add(clark)
            db.session.commit()

            response = app.test_client().get("/customers").json
            customers = Customer.query.all()
            assert [customer["id"] for customer in response] == [
                customer.id for customer in customers
            ]
            assert [customer["name"] for customer in response] == [
                customer.name for customer in customers
            ]
            assert [customer["email"] for customer in response] == [
                customer.email for customer in customers
            ]

            Customer.query.delete()
            db.session.commit()

    def test_gets_customer_by_id(self):
        """retrieves one customer using its ID with GET request to /customers/<int:id>."""

        with app.app_context():
            bruce = Customer(
                name="Bruce Wayne", email="iamnotbatman@wayneindustries.com"
            )
            db.session.add(bruce)
            db.session.commit()

            response = app.test_client().get(f"/customers/{bruce.id}").json
            assert response["name"] == bruce.name
            assert response["email"] == bruce.email

    def test_returns_404_if_no_customer(self):
        """returns an error message and 404 status code when a customer is searched by a non-existent ID."""

        with app.app_context():
            Customer.query.delete()
            db.session.commit()

            response = app.test_client().get("/customers/1")
            assert response.json.get("error")
            assert response.status_code == 404

    def test_creates_customer(self):
        """creates one customer using a name and age with a POST request to /customers."""

        with app.app_context():
            Customer.query.delete()
            db.session.commit()

            response = (
                app.test_client()
                .post(
                    "/customers",
                    json={
                        "name": "Tony Stark",
                        "email": "therealironman@avengers.com",
                    },
                )
                .json
            )

            assert response["id"]
            assert response["name"] == "Tony Stark"
            assert response["email"] == "therealironman@avengers.com"

            tony = Customer.query.filter(
                Customer.name == "Tony Stark",
                Customer.email == "therealironman@avengers.com",
            ).one_or_none()
            assert tony

    def test_400_for_customer_validation_error(self):
        """returns a 400 status code and error message if a POST request to /customers fails."""

        with app.app_context():
            response = app.test_client().post(
                "/customers",
                json={
                    "name": "Tony Stark",
                    "email": "therealironman@avengers.com",
                },
            )

            assert response.status_code == 400
            assert response.json["error"]

            response = app.test_client().post(
                "customers", json={"name": "", "email": "none@none.com"}
            )

            assert response.status_code == 400
            assert response.json["error"]

    def test_gets_locations(self):
        """retrieves locations with GET request to /locations"""

        with app.app_context():
            location = Location(name="Swimming", max_party_size=12)
            db.session.add(location)
            db.session.commit()

            response = app.test_client().get("/locations").json
            locations = Location.query.all()

            assert [location["id"] for location in response] == [
                location.id for location in locations
            ]
            assert [location["name"] for location in response] == [
                location.name for location in locations
            ]
            assert [location["max_party_size"] for location in response] == [
                location.max_party_size for location in locations
            ]

    # def test_returns_404_if_no_location(self):
    #     """returns 404 status code with DELETE request to /locations/<int:id> if location does not exist."""

    #     with app.app_context():
    #         Location.query.delete()
    #         db.session.commit()

    #         response = app.test_client().delete("/locations/1")
    #         assert response.json.get("error")
    #         assert response.status_code == 404

    def test_creates_reservations(self):
        """creates reservations with POST request to /reservations"""

        with app.app_context():
            Reservation.query.delete()
            Customer.query.delete()
            Location.query.delete()
            db.session.commit()
            peter = Customer(
                name="Peter Parker",
                email="thehumanspider@wannabeanavenger.com",
            )
            pizza = Location(name="Happys Pizza", max_party_size=6)
            db.session.add_all([peter, pizza])
            db.session.commit()

            response = (
                app.test_client()
                .post(
                    "/reservations",
                    json={
                        "reservation_date": "2023-06-18",
                        "customer_id": peter.id,
                        "location_id": pizza.id,
                        "party_size": 4,
                        "party_name": "spider friends",
                    },
                )
                .json
            )
            print(response)
            assert response["id"]
            assert response["customer_id"] == peter.id
            assert response["location_id"] == pizza.id
            assert response["party_size"] == 4
            assert response["party_name"] == "spider friends"

            reservation = Reservation.query.filter(
                Reservation.party_name == "spider friends"
            ).first()
            assert reservation
            Reservation.query.delete()
            db.session.commit()

    def test_for_reservation_validation_error(self):
        """returns an error message if a POST request to /reservations fails."""

        with app.app_context():
            Customer.query.delete()
            Location.query.delete()
            db.session.commit()
            peter = Customer(
                name="Peter Parker",
                email="thehumanspider@wannabeanavenger.com",
            )
            pizza = Location(name="Happys Pizza", max_party_size=6)
            db.session.add_all([peter, pizza])
            db.session.commit()

            response = (
                app.test_client()
                .post(
                    "/reservations",
                    json={
                        "reservation_date": "2023-06-19",
                        "customer_id": peter.id,
                        "party_size": 24,
                        "party_name": "spider friends",
                    },
                )
                .json
            )
            print(response)

            assert response["error"]

    def test_deletes_reservation_by_id(self):
        """deletes locations with DELETE request to /reservations/<int:id>."""

        with app.app_context():
            Reservation.query.delete()
            Customer.query.delete()
            Location.query.delete()
            db.session.commit()
            peter = Customer(
                name="Peter Parker",
                email="thehumanspider@wannabeanavenger.com",
            )
            pizza = Location(name="Happys Pizza", max_party_size=6)
            db.session.add_all([peter, pizza])
            db.session.commit()

            response = (
                app.test_client()
                .post(
                    "/reservations",
                    json={
                        "reservation_date": "2023-06-18",
                        "customer_id": peter.id,
                        "location_id": pizza.id,
                        "party_size": 4,
                        "party_name": "spider friends",
                    },
                )
                .json
            )
            print(response)
            assert response["id"]
            assert response["customer_id"] == peter.id
            assert response["location_id"] == pizza.id
            assert response["party_size"] == 4
            assert response["party_name"] == "spider friends"

            db.session.query(Reservation).filter(
                Reservation.party_name == "spider friends"
            ).delete()
            db.session.commit()
            reservation = Reservation.query.filter(
                Reservation.party_name == "spider friends"
            ).first()
            assert not reservation
