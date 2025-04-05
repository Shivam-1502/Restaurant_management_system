from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), default="Admin")
    contact_details = db.Column(db.String(100))
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"admin-{self.id}"


class Employee(UserMixin, db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), default="Employee")
    contact_details = db.Column(db.String(100))
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return f"employee-{self.id}"


class MenuItem(db.Model):
    __tablename__ = 'menu_item'
    menuItemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<MenuItem {self.name} - {self.category} - ₹{self.price}>"


class Inventory(db.Model):
    __tablename__ = 'inventory'
    itemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    reorder_level = db.Column(db.Integer, nullable=False)
    supplier = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Inventory {self.name} - {self.quantity} {self.unit} from {self.supplier}>"


class Orders(db.Model):
    __tablename__ = 'orders'
    orderID = db.Column(db.String(20), primary_key=True)
    employeeID = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    customerID = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    status = db.Column(db.Enum('Pending', 'Completed', name='order_status'), default='Pending')
    totalAmount = db.Column(db.Numeric(10, 2), nullable=False)

    employee = db.relationship('Employee', backref=db.backref('orders', lazy=True))
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return f"<Order {self.orderID} - {self.status} - ₹{self.totalAmount}>"


class Payment(db.Model):
    __tablename__ = 'payment'
    paymentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderID = db.Column(db.String(20), db.ForeignKey('orders.orderID'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    paymentMethod = db.Column(db.Enum('Cash', 'Card', 'UPI', name='payment_method'), nullable=False)

    order = db.relationship('Orders', backref=db.backref('payment', lazy=True))

    def __repr__(self):
        return f"<Payment {self.paymentID} - Order {self.orderID} - ₹{self.amount} - {self.paymentMethod}>"

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    orderID = db.Column(db.String(20), db.ForeignKey('orders.orderID'), nullable=False)
    menuItemID = db.Column(db.Integer, db.ForeignKey('menu_item.menuItemID'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship('Orders', backref=db.backref('items', lazy=True))
    menu_item = db.relationship('MenuItem', backref=db.backref('order_items', lazy=True))

    def __repr__(self):
        return f"<OrderItem {self.menu_item.name} - {self.quantity} x ₹{self.price}>"

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Customer {self.name} - {self.email}>"
