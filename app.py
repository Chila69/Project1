from flask import Flask, jsonify, request, render_template, url_for
from flask_cors import CORS
from models import db, Product, Category, Customer, Order
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #Забирает лишнюю память

    db.init_app(app)
    Migrate(app, db)

    # --- Глобальная инициализация БД + сидирование (работает и с `flask run`) ---
    with app.app_context():
        db.create_all()
        if Category.query.count() == 0:
            db.session.add_all([
                Category(name="Elektronika"),
                Category(name="Jedzenie"),
                Category(name="Ubrania"),
                Category(name="Inne")
            ])
            db.session.commit()

    # ---------- Pages ----------
    @app.route('/')
    def index():
        return render_template('index.html')  # в шаблоне подключай CSS через url_for('static', filename='style.css')

    # ---------- Products ----------
    @app.get('/api/products')
    def get_products():
        products = Product.query.all()
        return jsonify([p.to_dict() for p in products])

    @app.get('/api/products/<int:id>')
    def get_product(id):
        p = Product.query.get(id)
        if not p:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(p.to_dict())

    @app.post('/api/products')
    def add_product():
        data = request.get_json() or {}
        if not data.get("name") or len(data["name"].strip()) < 2:
            return jsonify({"error": "Nazwa produktu jest wymagana i musi mieć co najmniej 2 znaki"}), 400
        if data.get("price") is None:
            return jsonify({"error": "Pole 'price' jest wymagane"}), 400
        try:
            price = float(data["price"])
        except (TypeError, ValueError):
            return jsonify({"error": "Cena musi być liczbą"}), 400
        if price <= 0:
            return jsonify({"error": "Cena musi być dodatnia"}), 400

        category_id = data.get("category_id")
        if category_id:
            if not Category.query.get(category_id):
                return jsonify({"error": "Podana kategoria nie istnieje"}), 400

        p = Product(
            name=data["name"].strip(),
            price=price,
            status=data.get("status", "available"),
            category_id=category_id,
            description=data.get("description"),
            supplier=data.get("supplier")
        )
        db.session.add(p)
        db.session.commit()
        return jsonify(p.to_dict()), 201

    @app.put('/api/products/<int:id>')
    def update_product(id):
        p = Product.query.get(id)
        if not p:
            return jsonify({"error": "Produkt nie znaleziony"}), 404
        data = request.get_json() or {}

        if "name" in data:
            if not data["name"] or len(data["name"].strip()) < 2:
                return jsonify({"error": "Nazwa produktu musi mieć co najmniej 2 znaki"}), 400
            p.name = data["name"].strip()

        if "price" in data:
            try:
                price = float(data["price"])
            except (TypeError, ValueError):
                return jsonify({"error": "Cena musi być liczbą"}), 400
            if price <= 0:
                return jsonify({"error": "Cena musi być dodatnia"}), 400
            p.price = price

        if "status" in data:
            p.status = data["status"]

        if "category_id" in data:
            if data["category_id"] is None:
                p.category_id = None
            else:
                if not Category.query.get(data["category_id"]):
                    return jsonify({"error": "Podana kategoria nie istnieje"}), 400
                p.category_id = data["category_id"]

        if "description" in data:
            p.description = data["description"]

        if "supplier" in data:
            p.supplier = data["supplier"]

        db.session.commit()
        return jsonify(p.to_dict()), 200

    @app.delete('/api/products/<int:id>')
    def delete_product(id):
        p = Product.query.get(id)
        if not p:
            return jsonify({"error": "Product not found"}), 404
        db.session.delete(p)
        db.session.commit()
        # Можно 204 No Content, но оставим JSON:
        return jsonify({"message": "Product deleted"}), 200

    # ---------- Categories ----------
    @app.get('/api/categories')
    def get_categories():
        cats = Category.query.all()
        return jsonify([c.to_dict() for c in cats])

    @app.get('/api/categories/<int:id>')
    def get_category(id):
        c = Category.query.get(id)
        if not c:
            return jsonify({"error": "Category not found"}), 404
        return jsonify(c.to_dict())

    @app.post('/api/categories')
    def create_category():
        data = request.get_json() or {}
        if not data.get("name"):
            return jsonify({"error": "Missing required field: name"}), 400
        c = Category(name=data["name"], description=data.get("description"))
        db.session.add(c)
        db.session.commit()
        return jsonify(c.to_dict()), 201

    @app.put('/api/categories/<int:id>')
    def update_category(id):
        c = Category.query.get(id)
        if not c:
            return jsonify({"error": "Category not found"}), 404
        data = request.get_json() or {}
        if "name" in data: c.name = data["name"]
        if "description" in data: c.description = data["description"]
        db.session.commit()
        return jsonify(c.to_dict())

    @app.delete('/api/categories/<int:id>')
    def delete_category(id):
        c = Category.query.get(id)
        if not c:
            return jsonify({"error": "Category not found"}), 404
        db.session.delete(c)
        db.session.commit()
        return jsonify({"message": "Category deleted"}), 200

    # ---------- Customers ----------
    @app.get('/api/customers')
    def get_customers():
        cs = Customer.query.all()
        return jsonify([c.to_dict() for c in cs])

    @app.get('/api/customers/<int:id>')
    def get_customer(id):
        c = Customer.query.get(id)
        if not c:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify(c.to_dict())

    @app.post('/api/customers')
    def create_customer():
        data = request.get_json() or {}
        if not data.get("name") or not data.get("email"):
            return jsonify({"error": "Missing required fields: name, email"}), 400
        c = Customer(name=data["name"], email=data["email"])
        db.session.add(c)
        db.session.commit()
        return jsonify(c.to_dict()), 201

    @app.put('/api/customers/<int:id>')
    def update_customer(id):
        c = Customer.query.get(id)
        if not c:
            return jsonify({"error": "Customer not found"}), 404
        data = request.get_json() or {}
        if "name" in data: c.name = data["name"]
        if "email" in data: c.email = data["email"]
        db.session.commit()
        return jsonify(c.to_dict())

    @app.delete('/api/customers/<int:id>')
    def delete_customer(id):
        c = Customer.query.get(id)
        if not c:
            return jsonify({"error": "Customer not found"}), 404
        db.session.delete(c)
        db.session.commit()
        return jsonify({"message": "Customer deleted"}), 200

    # ---------- Orders ----------
    @app.get('/api/orders')
    def get_orders():
        os = Order.query.order_by(Order.id.desc()).all()
        return jsonify([o.to_dict() for o in os])

    @app.get('/api/orders/<int:id>')
    def get_order(id):
        o = Order.query.get(id)
        if not o:
            return jsonify({"error": "Order not found"}), 404
        return jsonify(o.to_dict())

    @app.post('/api/orders')
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

    @app.put('/api/orders/<int:id>')
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

    @app.delete('/api/orders/<int:id>')
    def delete_order(id):
        o = Order.query.get(id)
        if not o:
            return jsonify({"error": "Order not found"}), 404
        db.session.delete(o)
        db.session.commit()
        return jsonify({"message": "Order deleted"}), 200

    return app


app = create_app()

def seed_categories():
    with app.app_context():
        db.create_all()
        if Category.query.count() == 0:
            db.session.add_all([
                Category(name="Elektronika"),
                Category(name="Jedzenie"),
                Category(name="Ubrania"),
                Category(name="Inne")
            ])
            db.session.commit()
            print("✅ Default categories added!")
        else:
            print("ℹ️ Categories already exist.")

seed_categories()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
