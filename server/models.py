from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)


    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza',back_populates='restaurant',cascade='all, delete-orphan')

    # add serialization rules
    serialize_rules=('-restaurant_pizzas.restaurant')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'restaurant_pizzas': [rp.to_dict() for rp in self.restaurant_pizzas]
        }


    def __repr__(self):
        return f'<Restaurant {self.name}>'


class Pizza(db.Model, SerializerMixin):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # add relationship
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza',cascade='all, delete-orphan')

    # add serialization rules
    serialize_rules=('-restaurant_pizzas.pizza')

    def to_dict(self):
        return{
            'id':self.id,
            'name':self.name,
            'ingredients':self.ingredients
            
        }

    def __repr__(self):
        return f'<Pizza {self.name}, {self.ingredients}>'


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'),nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'),nullable=False)


    # add relationships
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')

    # add serialization rules
    serialize_rules=('-restaurant.restaurant_pizzas','-pizza.restaurant_pizzas')

    def to_dict(self):
        return{
            'id':self.id,
            'price':self.price,
            'restaurant_id': self.restaurant_id,
            'pizza_id': self.pizza_id,
            'pizza': self.pizza.to_dict(),
            'restaurant': self.restaurant.to_dict()
        }

    # add validation
    @validates('price')
    def price_validation(self,key,rp_price):
        if not 1<= rp_price <= 30:
            raise ValueError("Price range is between 1-30")
        return rp_price
  

    def __repr__(self):
        return f'<RestaurantPizza ${self.price}>'