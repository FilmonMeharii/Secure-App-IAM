from flask import Flask, session, redirect, url_for
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask import request

app = Flask(__name__)
app.secret_key = "64eda5cf41104938709034afb18989d11a6b631b5568a443241775ad238de07e" 
csrf = CSRFProtect(app)

products = [
    {"id": 1, "name": "Security Key", "price": 299},
    {"id": 2, "name": "USB-C Hub", "price": 199},
    {"id": 3, "name": "Privacy Screen", "price": 249},
]


@app.route("/add/<int:product_id>")
def add_to_cart(product_id):
    if "username" not in session:
        return redirect(url_for("login"))

    cart = session.get("cart", {})
    product_key = str(product_id)

    cart[product_key] = cart.get(product_key, 0) + 1
    session["cart"] = cart

    return redirect(url_for("home"))


@app.route("/cart")
def view_cart():
    if "username" not in session:
        return redirect(url_for("login"))

    cart = session.get("cart", {})
    token = generate_csrf()
    cart_items = ""
    total = 0

    for product in products:
        quantity = cart.get(str(product["id"]), 0)

        if quantity > 0:
            subtotal = product["price"] * quantity
            total += subtotal

            cart_items += (
                f"<li>{product['name']} x {quantity} "
                f"= {subtotal} kr</li>"
            )

    if not cart_items:
        cart_items = "<li>Varukorgen är tom.</li>"

    return f"""
    <h1>Min varukorg</h1>
    <ul>{cart_items}</ul>
    <h2>Totalt: {total} kr</h2>
    <a href="/">Tillbaka till butiken</a>
    <form action="/clear-cart" method="POST">
        <input type="hidden" name="csrf_token" value="{token}"> 
        <button type="submit">Töm varukorgen</button>
    </form>
    
    """

@app.route("/clear-cart", methods=["POST"])
def clear_cart():
    session["cart"] = {}
    return redirect(url_for("view_cart"))

@app.route("/")
def home():
    product_list = ""

    for product in products:
        product_list += (
            f"<li>{product['name']} - "
            f"{product['price']} kr "
            f"<a href='/add/{product['id']}'>"
            f"Lägg till i varukorgen</a></li>"
        )
        cart = session.get("cart", {})
        cart_items = sum(cart.values()) 
    
    username = session.get("username", "Gäst")
    role = session.get("role", "anonymous")
    return f"""

    <!DOCTYPE html>
    <html lang="sv">
    <head>
        <meta charset="UTF-8">
        <title>SecureShop IAM Academy</title>
    </head>
    <body>
        <h1>SecureShop IAM Academy</h1>
        <p>Välkommen, {username}!</p>
        <p>Roll: {role}</p>
        <p><a href="/account">Mitt konto</a></p>
        <p><a href="/iam">IAM-översikt</a></p>
        {f'<p><a href="/admin">Adminpanel</a></p>' if role == 'admin' else ''}
        <form action="/logout" method="POST">
            <input type="hidden" name="csrf_token" value="{generate_csrf()}">
            <button type="submit">Logga ut</button>
        </form>

        <h2>Produkter</h2>
        <ul>{product_list}</ul>
        <p>Alla köp är simulerade.</p>
        <p><a href="/cart">Visa varukorg ({cart_items} produkter)</a></p>
    </body>
    </html>
    """


@app.route("/health")
def health():
    return {
        "application": "SecureShop IAM Academy",
        "status": "ok",
        "csrf_protection": "enabled"
    }


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")

        if username:
            session["username"] = username
            session["role"] = "admin" if username == "admin" else "customer"
            return redirect(url_for("home"))

    return """
    <h1>Logga in</h1>
    <form method="POST">
        <label for="username">Användarnamn:</label>
        <input type="text" id="username" name="username" required>
        <input type="hidden" name="csrf_token" value="{}">
        <button type="submit">Logga in</button>
    </form>
    """.format(generate_csrf())


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))


@app.route("/admin")
def admin_page():
    if session.get("role") != "admin":
        return "Åtkomst nekad: adminbehörighet krävs.", 403

    return """
    <h1>Adminpanel</h1>
    <p>Du har adminbehörighet.</p>
    <a href="/">Tillbaka till butiken</a>
    """


@app.route("/account")
def account_page():
    if "username" not in session:
        return redirect(url_for("login"))

    return f"""
    <h1>Mitt konto</h1>
    <p>Användare: {session["username"]}</p>
    <p>IAM-roll: {session.get("role", "unknown")}</p>
    <a href="/">Tillbaka till butiken</a>
    """

@app.route("/iam")
def iam_overview():
    if "username" not in session:
        return redirect(url_for("login"))

    return f"""
    <h1>IAM-översikt</h1>
    <p>Användaridentitet: {session["username"]}</p>
    <p>Tilldelad roll: {session.get("role", "unknown")}</p>
    <p>Inloggad: Ja</p>
    <a href="/">Tillbaka till butiken</a>
    """


if __name__ == "__main__":
    app.run(debug=True)