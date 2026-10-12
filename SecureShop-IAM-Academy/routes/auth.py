import sqlite3

from audit import log_event

from flask import (
    Blueprint, current_app, request, session, redirect, url_for
)
from flask_wtf.csrf import generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    error = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username:
            error = "Användarnamn krävs."
        elif len(username) > 80:
            error = "Användarnamnet får vara högst 80 tecken."
        elif len(password) < 12:
            error = "Lösenordet måste vara minst 12 tecken."
        elif password != confirm_password:
            error = "Lösenorden matchar inte."
        else:
            try:
                with sqlite3.connect(
                    current_app.config["DATABASE_PATH"]
                ) as conn:
                    conn.execute(
                        """
                        INSERT INTO users (username, password_hash, role)
                        VALUES (?, ?, ?)
                        """,
                        (
                            username,
                            generate_password_hash(password),
                            "customer",
                        ),
                    )
                return redirect(url_for("auth.login"))
            except sqlite3.IntegrityError:
                error = "Användarnamnet finns redan."

    return """
    <h1>Skapa konto</h1>
    <p>{error}</p>
    <form method="POST">
        <label for="username">Användarnamn:</label>
        <input type="text" id="username" name="username"
               maxlength="80" required>

        <label for="password">Lösenord, minst 12 tecken:</label>
        <input type="password" id="password" name="password" required>

        <label for="confirm_password">Bekräfta lösenord:</label>
        <input type="password" id="confirm_password"
               name="confirm_password" required>

        <input type="hidden" name="csrf_token" value="{csrf}">
        <button type="submit">Skapa konto</button>
    </form>
    <p><a href="/login">Till inloggningen</a></p>
    """.format(error=error, csrf=generate_csrf())


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with sqlite3.connect(
            current_app.config["DATABASE_PATH"]
        ) as conn:
            conn.row_factory = sqlite3.Row
            user = conn.execute(
                """
                SELECT username, password_hash, role
                FROM users
                WHERE username = ?
                """,
                (username,),
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["username"] = user["username"]
            session["role"] = user["role"]

            log_event(
                event="login_success",
                username=user["username"],
                result="success",
            )

            return redirect(url_for("shop.home"))

        log_event(
            event="login_failed",
            username=username or None,
            result="failure",
            details="Fel användarnamn eller lösenord.",
        )

        error = "Fel användarnamn eller lösenord."

    return """
    <h1>Logga in</h1>
    <p>{error}</p>
    <form method="POST">
        <label for="username">Användarnamn:</label>
        <input type="text" id="username" name="username" required>

        <label for="password">Lösenord:</label>
        <input type="password" id="password" name="password" required>

        <input type="hidden" name="csrf_token" value="{csrf}">
        <button type="submit">Logga in</button>
    </form>
    <p><a href="/register">Skapa konto</a></p>
    """.format(error=error, csrf=generate_csrf())


@auth_bp.route("/logout", methods=["POST"])
def logout():
    username = session.get("username")

    log_event(
        event="logout",
        username=username,
        result="success",
    )

    session.clear()
    return redirect(url_for("shop.home"))
