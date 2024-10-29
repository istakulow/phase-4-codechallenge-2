#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/restaurants', methods=['GET'])
def restaurants():
    restaurants = []
    for restaurant in Restaurant.query.all():
        restaurant_dict = {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name

        }
        restaurants.append(restaurant_dict)

    response = make_response(
        restaurants,
        200,
        {'Content-Type':'application/json'}
    )
    return response

@app.route('/restaurants/<int:id>', methods=['GET','DELETE'])
def restaurantsid(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if request.method == 'GET':
        if restaurant is None:
            return make_response(
                {'error': 'Restaurant not found'}, 
                404, 
                {'Content-Type': 'application/json'})
        
        restaurant_serialized = restaurant.to_dict()
        response = make_response(
            restaurant_serialized,
            200, 
            {'Content-Type': 'application/json'}
            )
        return response

    elif request.method == 'DELETE':
        if restaurant is None:
            return make_response(
                {'error': 'Restaurant not found'}, 
                404, 
                {'Content-Type': 'application/json'})
        else:
            db.session.delete(restaurant)
            db.session.commit()

            response = make_response(
                '',
                204,
                {'Content-Type': 'application/json'}
            )
            return response

@app.route('/pizzas', methods=['GET'])
def pizzas():
    pizzas = []
    for pizza in Pizza.query.all():
        pizza_serialized = pizza.to_dict()
        pizzas.append(pizza_serialized)

    response = make_response(
        pizzas,
        200,
        {'Content-Type': 'application/json'}
    )
    return response

@app.route('/restaurant_pizzas', methods=['POST'])
def restaurant_pizzas():
    if 'price' in request.json and 'pizza_id' in request.json and 'restaurant_id' in request.json:
        try:
            pizza = db.session.get(Pizza, request.json.get("pizza_id"))
            restaurant = db.session.get(Restaurant, request.json.get("restaurant_id"))

            if pizza is None or restaurant is None:
                error_response = jsonify({"errors": ["pizza or restaurant not found"]})
                error_response.status_code = 404
                return error_response

            if not isinstance(request.json.get("price"), int) or not 1 <= request.json.get("price") <= 30:
                error_response = jsonify({"errors": ["validation errors"]})
                error_response.status_code = 400
                return error_response

            new_restaurantpizza = RestaurantPizza(
                price=request.json.get("price"),
                pizza=pizza,
                restaurant=restaurant
            )
            db.session.add(new_restaurantpizza)
            db.session.commit()

            restaurant_pizza_serialized = {
                "id": new_restaurantpizza.id,
                "pizza": {
                    "id": pizza.id,
                    "ingredients": pizza.ingredients,
                    "name": pizza.name
                },
                "pizza_id": pizza.id,
                "price": new_restaurantpizza.price,
                "restaurant": {
                    "address": restaurant.address,
                    "id": restaurant.id,
                    "name": restaurant.name
                },
                "restaurant_id": restaurant.id
            }

            response = make_response(
                restaurant_pizza_serialized,
                201,
                {'Content-Type': 'application/json'}
            )
            return response
        except Exception as e:
            error_response = jsonify({"errors": ["validation error"]})
            error_response.status_code = 400
            return error_response
    else:
        error_response = jsonify({"errors": ["invalid request body"]})
        error_response.status_code = 400
        return error_response

if __name__ == '__main__':
    app.run(port=5555, debug=True)