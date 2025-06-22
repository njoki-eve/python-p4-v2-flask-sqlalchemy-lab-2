from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()

class SerializerMixin:
    def to_dict(self, include_relationships=True):
        data = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
        if include_relationships:
            for relationship in self.__mapper__.relationships:
                if relationship.direction.name == 'MANYTOONE':
                    related_obj = getattr(self, relationship.key)
                    if related_obj:
                        data[relationship.key] = related_obj.to_dict(include_relationships=False)
                elif relationship.direction.name == 'ONETOMANY':
                    data[relationship.key] = [
                        item.to_dict(include_relationships=False)
                        for item in getattr(self, relationship.key)
                    ]
        return data

class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    
    reviews = db.relationship('Review', back_populates='customer')
    items = association_proxy('reviews', 'item',
                            creator=lambda item: Review(item=item))

class Item(db.Model, SerializerMixin):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    
    reviews = db.relationship('Review', back_populates='item')
    customers = association_proxy('reviews', 'customer',
                                creator=lambda customer: Review(customer=customer))

class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    
    customer = db.relationship('Customer', back_populates='reviews')
    item = db.relationship('Item', back_populates='reviews')
    