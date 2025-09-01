import os
import json
from pathlib import Path
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import stripe

# ------------------------------
# Cargar variables de entorno
# ------------------------------
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Variables importantes (configura en .env)
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")  # sk_test_...
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")  # opcional (para validar webhooks)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")

if not STRIPE_SECRET_KEY:
    raise RuntimeError("Define STRIPE_SECRET_KEY en tu archivo .env")

stripe.api_key = STRIPE_SECRET_KEY

# ------------------------------
# Configurar Flask y SQLAlchemy
# ------------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR / 'database.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------------------------------
# Modelos
# ------------------------------
class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    supplier = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price_cents = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    brand = db.Column(db.String(120), nullable=True)
    weight = db.Column(db.String(50), nullable=True)
    ingredients = db.Column(db.Text, nullable=True)
    allergens = db.Column(db.Text, nullable=True)
    nutritional_info = db.Column(db.Text, nullable=True)
    stock = db.Column(db.Integer, nullable=False, default=0)

    def price_display(self):
        return f"{self.price_cents / 100:.2f}"



class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    stripe_session_id = db.Column(db.String(255), nullable=False, unique=True)
    amount_total = db.Column(db.Integer, nullable=False)  # centavos
    currency = db.Column(db.String(10), default="usd")
    paid = db.Column(db.Boolean, default=False)
    payload = db.Column(db.Text)  # JSON con datos del evento (opcional)

# ------------------------------
# Inicializar DB con productos demo
# ------------------------------

def init_db():
    with app.app_context():
        db.create_all()

# ------------------------------
# Helpers carrito sesión
# ------------------------------
CART_SESSION_KEY = "cart"  # estructura {product_id: cantidad, ...}

# Guardar el carrito en la sesión
def save_cart(cart):
    session['cart'] = cart

# Recuperar el carrito de la sesión
def get_cart():
    return session.get('cart', {})

def add_to_cart(product_id, qty=1):
    cart = get_cart()
    cart[str(product_id)] = cart.get(str(product_id), 0) + int(qty)
    save_cart(cart)

def update_cart_item(product_id, qty):
    cart = get_cart()
    if int(qty) <= 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = int(qty)
    save_cart(cart)

def clear_cart():
    session.pop(CART_SESSION_KEY, None)
    session.modified = True

def cart_items_with_products():
    cart = get_cart()
    items = []
    total = 0
    for pid, qty in cart.items():
        p = Product.query.get(int(pid))
        if not p:
            continue
        subtotal = p.price_cents * qty
        items.append({"product": p, "quantity": qty, "subtotal": subtotal})
        total += subtotal
    return items, total

# ------------------------------
# Rutas públicas
# ------------------------------
@app.route("/")
def index():
    products = Product.query.all()
    products_by_supplier = {}
    for p in products:
        proveedor = p.supplier or "Otros"
        if proveedor not in products_by_supplier:
            products_by_supplier[proveedor] = []
        products_by_supplier[proveedor].append(p)
    return render_template(
        "index.html",
        products_by_supplier=products_by_supplier,
        now=datetime.now()  # <-- agrega esto
    )


@app.route("/producto/<int:product_id>")
def producto_detalle(product_id):
    producto = Product.query.get_or_404(product_id)
    return render_template("producto.html", producto=producto, now=datetime.now())


@app.route("/add-to-cart", methods=["POST"])
def route_add_to_cart():
    product_id = request.form.get("product_id")
    cantidad = request.form.get("cantidad", type=int)
    product = Product.query.get(product_id)
    if not product:
        flash("Producto no encontrado.", "error")
        return redirect(url_for("index"))
    if not cantidad or cantidad < 1:
        flash("Cantidad inválida.", "error")
        return redirect(url_for("producto_detalle", product_id=product_id))
    if cantidad > product.stock:
        flash("No hay suficiente stock disponible.", "error")
        return redirect(url_for("producto_detalle", product_id=product_id))
    cart = get_cart()
    cart[product_id] = cart.get(product_id, 0) + cantidad
    save_cart(cart)
    flash("Producto agregado al carrito.", "success")
    return redirect(url_for("view_cart"))

@app.route("/cart")
def view_cart():
    cart = get_cart()
    items, total = cart_items_with_products()
    return render_template("cart.html", items=items, total=total, now=datetime.now())

@app.route("/update-cart", methods=["POST"])
def route_update_cart():
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = request.get_json()
        product_id = str(data.get("product_id"))
        cart = get_cart()
        product = Product.query.get(product_id)
        if not product:
            return jsonify(success=False, message="Producto no encontrado.")
        if data.get("remove"):
            cart.pop(product_id, None)
        else:
            qty = int(data.get("quantity", 1))
            if qty < 1 or qty > product.stock:
                return jsonify(success=False, message="Cantidad inválida.")
            cart[product_id] = qty
        save_cart(cart)
        subtotal = "%.2f" % ((cart.get(product_id, 0) * product.price_cents) / 100) if product_id in cart else "0.00"
        total = "%.2f" % (sum(Product.query.get(pid).price_cents * qty for pid, qty in cart.items()) / 100)
        return jsonify(success=True, subtotal=subtotal, total=total)
    # --- Manejo tradicional (no AJAX) ---
    # Actualiza cantidades y elimina productos usando request.form
    cart = get_cart()
    quantities = request.form.getlist("quantity")
    # Si usas un dict en el name, usa request.form.to_dict(flat=False)
    for key in request.form:
        if key.startswith("quantity["):
            pid = key.split("[")[1].split("]")[0]
            qty = int(request.form.get(key, 1))
            if qty < 1:
                cart.pop(pid, None)
            else:
                cart[pid] = qty
    # Eliminar producto si se envió el botón remove
    remove_id = request.form.get("remove")
    if remove_id:
        cart.pop(remove_id, None)
    save_cart(cart)
    return redirect(url_for("view_cart"))

@app.route("/carrito/eliminar/<int:product_id>", methods=["POST"])
def route_remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)  # Elimina el producto del carrito dict
    save_cart(cart)
    flash("Producto eliminado del carrito.", "info")
    return redirect(url_for("view_cart"))

# ------------------------------
# Checkout Stripe
# ------------------------------
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    cart = get_cart()
    line_items = []
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if not product or qty < 1:
            continue
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': product.price_cents,
                'product_data': {
                    'name': product.name,
                },
            },
            'quantity': qty,
        })
    if not line_items:
        flash("No hay productos válidos en el carrito.", "error")
        return redirect(url_for("view_cart"))
    session_obj = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode='payment',
        success_url=url_for('success', _external=True),
        cancel_url=url_for('view_cart', _external=True),
        metadata={'cart_items': json.dumps(cart)}
    )
    return redirect(session_obj.url, code=303)

# ------------------------------
# Resultados
# ------------------------------
@app.route("/success")
def success():
    session_id = request.args.get("session_id")
    return render_template("success.html", session_id=session_id)

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

# ------------------------------
# Webhook Stripe
# ------------------------------
@app.route("/webhook", methods=["POST"])
def webhook_received():
    payload = request.data
    sig_header = request.headers.get("stripe-signature")
    event = None

    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(
                payload=payload, sig_header=sig_header, secret=STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            app.logger.error("Invalid payload: %s", e)
            return jsonify({"error": "Invalid payload"}), 400
        except stripe.error.SignatureVerificationError as e:
            app.logger.error("Invalid signature: %s", e)
            return jsonify({"error": "Invalid signature"}), 400
    else:
        try:
            event = json.loads(payload)
        except Exception as e:
            app.logger.error("No se pudo parsear el payload: %s", e)
            return jsonify({"error": "Invalid payload"}), 400

    event_type = event.get("type")
    app.logger.info("Webhook recibido: %s", event_type)

    if event_type == "checkout.session.completed":
        session_obj = event["data"]["object"]
        stripe_session_id = session_obj.get("id")
        order = Order.query.filter_by(stripe_session_id=stripe_session_id).first()
        if order:
            order.paid = True
            order.payload = json.dumps(session_obj)
            order.amount_total = session_obj.get("amount_total", order.amount_total)
            order.currency = session_obj.get("currency", order.currency)
            db.session.commit()
            app.logger.info("Orden %s marcada como pagada.", order.id)
        else:
            new_order = Order(
                stripe_session_id=stripe_session_id,
                amount_total=session_obj.get("amount_total", 0),
                currency=session_obj.get("currency", "usd"),
                paid=True,
                payload=json.dumps(session_obj),
            )
            db.session.add(new_order)
            db.session.commit()
            app.logger.info("Orden creada desde webhook: %s", new_order.id)

        # Descontar stock de productos comprados
        cart_items = session_obj.get('metadata', {}).get('cart_items')
        if cart_items:
            cart = json.loads(cart_items)
            for pid, qty in cart.items():
                product = Product.query.get(int(pid))
                if product:
                    product.stock = max(product.stock - int(qty), 0)
            db.session.commit()
            app.logger.info("Stock actualizado por compra Stripe.")

        # Limpiar carrito del comprador (sesión actual)
        clear_cart()

    return jsonify({"received": True}), 200

# ------------------------------
# Admin simple (sin auth)
# ------------------------------
@app.route("/admin")
def admin_index():
    products = Product.query.all()
    return render_template("admin/index.html", products=products)

@app.route("/admin/product/new", methods=["GET", "POST"])
def admin_new_product():
    if request.method == "POST":
        name = request.form.get("name")
        supplier = request.form.get("supplier")
        desc = request.form.get("description")
        price = int(float(request.form.get("price")) * 100)  # 25.00 -> 2500
        image = request.form.get("image")  # ruta relativa en /static/img/
        p = Product(
            supplier=supplier,
            name=name,
            description=desc,
            price_cents=price,
            image=image
        )
        db.session.add(p)
        db.session.commit()
        flash("Producto creado", "success")
        return redirect(url_for("admin_index"))
    return render_template("admin/new_product.html")


@app.route("/ayuda")
def ayuda():
    return render_template("ayuda.html")

# ------------------------------
# Main
# ------------------------------
if __name__ == "__main__":
    init_db()
    app.run(port=4242, debug=True)
