from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from . import db



class Brand(db.Model):
    """This classs contains the brands sold on the Cycle website. Class attributes
    includes links to the Bicycle and OrderDetails classes."""
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(60), nullable=False)
    bicycles = db.relationship(
        'Bicycle', backref='Brand', cascade='all, delete-orphan')

    def __repr__(self):
        str = F"Id:{self.id}, Name:{self.name}, Description:{self.description}, Image: {self.image}"
        return str


class Bicycle(db.Model):
    """This class defines an object representing a bicycle. Attributes link to the Brand,
    Images, and OrderDetails classes."""
    __tablename__ = 'bicycles'
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    images = db.relationship("Images", backref='Bicycle',
                             cascade='all, delete-orphan')
    price = db.Column(db.Float, nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'))
    #sets relationship to the OrderDetails class
    orderdetails = db.relationship("OrderDetails", back_populates="bicycle", cascade='all, delete-orphan')

    def __repr__(self):
        str = (F"Id:{self.id}, Model:{self.model}, Description:{self.description}, Images: {self.images}/"
               F"Price:{self.price}, Brand:{self.brand_id}")
        return str


class Images(db.Model):
    """This class defines the images linked to each Bicycle object."""
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    bicycle_id = db.Column(db.Integer, db.ForeignKey("bicycles.id"))
    image = db.Column(db.String(60), nullable=False)


class OrderDetails(db.Model):
    """This class defines the bicycles and quantities associated with each Order."""
    __tablename__ = "orderdetails"
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, primary_key = True)
    bicycle_id = db.Column(db.Integer, db.ForeignKey('bicycles.id'), nullable=False, primary_key = True)
    quantity = db.Column(db.Integer, nullable=False, default = 1)
    #relationships with the Order and Bicycle class
    order = db.relationship("Order", back_populates ='orderdetails')
    bicycle = db.relationship("Bicycle", back_populates = 'orderdetails')



class Order(db.Model):
    """This class represents a customer order. It includes relationships with Bicycle objects
    and OrderDetails objects."""
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean, default=False)
    firstname = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    email = db.Column(db.String(128))
    phone = db.Column(db.String(32))
    totalcost = db.Column(db.Float)
    date = db.Column(db.DateTime)
    orderdetails = db.relationship("OrderDetails", back_populates="order", cascade='all, delete-orphan')


    def __repr__(self):
        str = "id: {}, Status: {}, Firstname: {}, Surname: {}, Email: {}, Phone: {}, Date: {}, Bicycles: {}, Total Cost: {}\n"
        str = str.format(self.id, self.status, self.firstname, self.surname,
                         self.email, self.phone, self.date, self.bicycles, self.totalcost)
        return str

#create relationship proxies so we can still use Order.bicycles to get all bicycles for an order
Order.bicycles = association_proxy("orderdetails", "bicycle")
Bicycle.orders = association_proxy("orderdetails", "order")