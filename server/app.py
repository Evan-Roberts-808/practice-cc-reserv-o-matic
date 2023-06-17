#!/usr/bin/env python3

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DATABASE = os.environ.get(
#     "DB_URI", f"sqlite://{os.path.join(BASE_DIR, 'instance/app.db')}"
# )

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from models import db, Customer, Location, Reservation
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    BASE_DIR, "instance/app.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def home():
    return ""

class Customers(Resource):

    def get(self):
        customers = [customer.to_dict() for customer in Customer.query.all()]
        return customers, 200

    def post(self):
        try:
            data = request.get_json()

            new_customer = Customer(
                name = data.get('name'),
                email = data.get('email')
            )
            db.session.add(new_customer)
            db.session.commit()

            return new_customer.to_dict(), 201
        except:
            return {"error": "400: Validation Error"}, 400

api.add_resource(Customers, "/customers")

class CustomerById(Resource):
    
    def get(self, id):
        try:
            customer = Customer.query.filter_by(id=id).first().to_dict(only=("id", "name", "email", "reservations"))
            return customer
        except:
            return {"error": "404: customer not found"}, 404

api.add_resource(CustomerById, "/customers/<int:id>")

class Locations(Resource):

    def get(self):
        locations = [location.to_dict() for location in Location.query.all()]
        return locations, 200

api.add_resource(Locations, "/locations")    

class Reservations(Resource):

    def get(self):
        try:
            reservations = [reservation.to_dict() for reservation in Reservation.query.all()]
            return reservations, 200
        except:
            return {"error": "400 bad request"}, 400
        
    def post(self):
        try:
            data = request.get_json()

            new_reservation = Reservation(
                reservation_date = datetime.datetime.strptime(data.get("reservation_date"), "%Y-%m-%d").date(),
                customer_id = data.get('customer_id'),
                location_id = data.get('location_id'),
                party_size = data.get('party_size'),
                party_name = data.get('party_name')
            )
            db.session.add(new_reservation)
            db.session.commit()
            return new_reservation.to_dict(), 201
        except:
            return {"error": "400: Validation error"}

api.add_resource(Reservations, "/reservations")    

class ReservationById(Resource):

    def get(self, id):
        try:
            reservation = Reservation.query.filter(Reservation.id == id).first().to_dict()
            return reservation, 200
        except:
            return {"error": "404 not found"}, 404

    def delete(self, id):
        try:
            reservation = Reservation.query.filter_by(id=id).first()
            db.session.delete(reservation)
            db.session.commit()
            return make_response({}, 204)
        except:
            return {"error": "404: Reservation not found"}, 404

api.add_resource(ReservationById, '/reservations/<int:id>')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
