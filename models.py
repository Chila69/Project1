from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# --- Category ---
class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(255))
    products = db.relationship("Product", back_populates="category", cascade="all,delete", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}

# --- Customer ---
class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    orders = db.relationship("Order", back_populates="customer", cascade="all,delete", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}

# --- Product (привязываем к Category) ---
class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="available")
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    # 🔹 Новые поля
    description = db.Column(db.String(255))
    supplier = db.Column(db.String(100))

    category = db.relationship("Category", back_populates="products")
    orders = db.relationship("Order", back_populates="product", cascade="all,delete", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "status": self.status,
            "description": self.description,
            "supplier": self.supplier,
            "category": self.category.to_dict() if self.category else None,
            "category_id": self.category_id,
        }

# --- Order ---
class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    product = db.relationship("Product", back_populates="orders")
    customer = db.relationship("Customer", back_populates="orders")

    def to_dict(self):
        return {
            "id": self.id,
            "product": self.product.to_dict() if self.product else None,
            "product_id": self.product_id,
            "customer": self.customer.to_dict() if self.customer else None,
            "customer_id": self.customer_id,
            "quantity": self.quantity,
            "order_date": self.order_date.isoformat()
        }
    
# --- User --
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique = True, nullable = False)
    password_hash = db.Column(db.String(200), nullable = False)
    role = db.Column(db.String(20), default="USER") 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

