from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from models import db, Product, Category, Customer, Order

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
from flask_migrate import Migrate
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()

# ---------- Pages ----------
@app.route('/')
def index():
    return render_template('index.html')

# ---------- Products ----------
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    p = Product.query.get(id)
    if not p:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(p.to_dict())

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.get_json() or {}
    if not data.get("name") or data.get("price") is None:
        return jsonify({"error": "Missing required fields: name, price"}), 400

    category_id = data.get("category_id")
    if category_id:
        cat = Category.query.get(category_id)
        if not cat:
            return jsonify({"error": "Category not found"}), 400

    p = Product(
        name=data["name"],
        price=float(data["price"]),
        status=data.get("status", "available"),
        category_id=category_id
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    p = Product.query.get(id)
    if not p:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json() or {}
    if "name" in data: p.name = data["name"]
    if "price" in data: p.price = float(data["price"])
    if "status" in data: p.status = data["status"]
    if "category_id" in data:
        if data["category_id"] is None:
            p.category_id = None
        else:
            cat = Category.query.get(data["category_id"])
            if not cat:
                return jsonify({"error": "Category not found"}), 400
            p.category_id = data["category_id"]

    db.session.commit()
    return jsonify(p.to_dict())

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    p = Product.query.get(id)
    if not p:
        return jsonify({"error": "Product not found"}), 404
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Product deleted"})

# ---------- Categories ----------
@app.route('/api/categories', methods=['GET'])
def get_categories():
    cats = Category.query.all()
    return jsonify([c.to_dict() for c in cats])

@app.route('/api/categories/<int:id>', methods=['GET'])
def get_category(id):
    c = Category.query.get(id)
    if not c:
        return jsonify({"error": "Category not found"}), 404
    return jsonify(c.to_dict())

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": "Missing required field: name"}), 400
    c = Category(name=data["name"], description=data.get("description"))
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201

@app.route('/api/categories/<int:id>', methods=['PUT'])
def update_category(id):
    c = Category.query.get(id)
    if not c:
        return jsonify({"error": "Category not found"}), 404
    data = request.get_json() or {}
    if "name" in data: c.name = data["name"]
    if "description" in data: c.description = data["description"]
    db.session.commit()
    return jsonify(c.to_dict())

@app.route('/api/categories/<int:id>', methods=['DELETE'])
def delete_category(id):
    c = Category.query.get(id)
    if not c:
        return jsonify({"error": "Category not found"}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Category deleted"})

# ---------- Customers ----------
@app.route('/api/customers', methods=['GET'])
def get_customers():
    cs = Customer.query.all()
    return jsonify([c.to_dict() for c in cs])

@app.route('/api/customers/<int:id>', methods=['GET'])
def get_customer(id):
    c = Customer.query.get(id)
    if not c:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(c.to_dict())

@app.route('/api/customers', methods=['POST'])
def create_customer():
    data = request.get_json() or {}
    if not data.get("name") or not data.get("email"):
        return jsonify({"error": "Missing required fields: name, email"}), 400
    c = Customer(name=data["name"], email=data["email"])
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201

@app.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    c = Customer.query.get(id)
    if not c:
        return jsonify({"error": "Customer not found"}), 404
    data = request.get_json() or {}
    if "name" in data: c.name = data["name"]
    if "email" in data: c.email = data["email"]
    db.session.commit()
    return jsonify(c.to_dict())

@app.route('/api/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    c = Customer.query.get(id)
    if not c:
        return jsonify({"error": "Customer not found"}), 404
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Customer deleted"})

# ---------- Orders ----------
@app.route('/api/orders', methods=['GET'])
def get_orders():
    os = Order.query.order_by(Order.id.desc()).all()
    return jsonify([o.to_dict() for o in os])

@app.route('/api/orders/<int:id>', methods=['GET'])
def get_order(id):
    o = Order.query.get(id)
    if not o:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(o.to_dict())

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json() or {}
    if not data.get("product_id") or not data.get("customer_id"):
        return jsonify({"error": "Missing required fields: product_id, customer_id"}), 400
    qty = int(data.get("quantity", 1))

    p = Product.query.get(data["product_id"])
    c = Customer.query.get(data["customer_id"])
    if not p: return jsonify({"error": "Product not found"}), 400
    if not c: return jsonify({"error": "Customer not found"}), 400

    o = Order(product_id=p.id, customer_id=c.id, quantity=qty)
    db.session.add(o)
    db.session.commit()
    return jsonify(o.to_dict()), 201

@app.route('/api/orders/<int:id>', methods=['PUT'])
def update_order(id):
    o = Order.query.get(id)
    if not o:
        return jsonify({"error": "Order not found"}), 404
    data = request.get_json() or {}
    if "product_id" in data:
        p = Product.query.get(data["product_id"])
        if not p: return jsonify({"error": "Product not found"}), 400
        o.product_id = p.id
    if "customer_id" in data:
        c = Customer.query.get(data["customer_id"])
        if not c: return jsonify({"error": "Customer not found"}), 400
        o.customer_id = c.id
    if "quantity" in data:
        o.quantity = int(data["quantity"])
    db.session.commit()
    return jsonify(o.to_dict())

@app.route('/api/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    o = Order.query.get(id)
    if not o:
        return jsonify({"error": "Order not found"}), 404
    db.session.delete(o)
    db.session.commit()
    return jsonify({"message": "Order deleted"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # если ты уже менял порт — оставь свой
