from flask import (
    Blueprint, render_template, session, redirect, url_for
)
from flask_wtf.csrf import generate_csrf

shop_bp = Blueprint("shop", __name__)

products = [
    {
        "id": 1,
        "name": "Security Key",
        "category": "IDENTITY SECURITY",
        "description": "Fysisk säkerhetsnyckel för starkare autentisering.",
        "price": 299,
        "icon": "◈",
        "tag": "SÄKERT VAL",
    },
    {
        "id": 2,
        "name": "USB-C Hub",
        "category": "CONNECTIVITY",
        "description": "Samla dina anslutningar i en kompakt hubb.",
        "price": 199,
        "icon": "▦",
        "tag": "",
    },
    {
        "id": 3,
        "name": "Privacy Screen",
        "category": "DATA PRIVACY",
        "description": "Mer integritet när du arbetar på offentliga platser.",
        "price": 249,
        "icon": "⬡",
        "tag": "POPULÄR",
    },
]


@shop_bp.route("/")
def home():
    cart = session.get("cart", {})
    cart_items = sum(cart.values())
    username = session.get("username", "Gäst")

    return render_template(
        "home.html",
        products=products,
        cart_items=cart_items,
        username=username,
        role=session.get("role", "anonymous"),
        csrf_token=generate_csrf(),
    )


@shop_bp.route("/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    if "username" not in session:
        return redirect(url_for("auth.login"))

    product = next(
        (p for p in products if p["id"] == product_id),
        None,
    )

    if product is None:
        return "Produkten hittades inte.", 404

    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session["cart"] = cart

    return redirect(url_for("shop.home"))


@shop_bp.route("/cart")
def view_cart():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    cart = session.get("cart", {})
    items = []
    total = 0

    for product in products:
        quantity = cart.get(str(product["id"]), 0)

        if quantity > 0:
            subtotal = product["price"] * quantity
            total += subtotal
            items.append({
                **product,
                "quantity": quantity,
                "subtotal": subtotal,
            })

    return render_template(
        "cart.html",
        items=items,
        total=total,
        csrf_token=generate_csrf(),
    )


@shop_bp.route("/clear-cart", methods=["POST"])
def clear_cart():
    if "username" not in session:
        return redirect(url_for("auth.login"))

    session["cart"] = {}
    return redirect(url_for("shop.view_cart"))