
import sqlite3
from urllib import response

import pytest
import app as app_module
from werkzeug.security import generate_password_hash


@pytest.fixture
def test_app(tmp_path, monkeypatch):
    """Använd en separat databas för varje test."""

    database_path = tmp_path / "test_secureshop.db"

    with sqlite3.connect(database_path) as conn:
        conn.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event TEXT NOT NULL,
                username TEXT,
                result TEXT NOT NULL,
                details TEXT
            )
            """
        )

        conn.executemany(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
            """,
            [
                (
                    "test_customer",
                    generate_password_hash("customer-test-password"),
                    "customer",
                ),
                (
                    "test_admin",
                    generate_password_hash("admin-test-password"),
                    "admin",
                ),
            ],
        )

    monkeypatch.setattr("audit.DATABASE_PATH", database_path)

    app = app_module.app
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        DATABASE_PATH=database_path,
        SECRET_KEY="test-only-secret-key",
    )

    with app.test_client() as client:
        yield client


def login_as(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


def test_customer_cannot_access_admin(test_app):
    login_as(
        test_app,
        "test_customer",
        "customer-test-password",
    )

    response = test_app.get("/admin")

    assert response.status_code == 403 
    assert "Åtkomst nekad".encode("utf-8") in response.data

def test_customer_cannot_access_audit_logs(test_app):
    login_as(
        test_app,
        "test_customer",
        "customer-test-password",
    )

    response = test_app.get("/admin/audit-logs")

    assert response.status_code == 403


def test_admin_can_access_admin_page(test_app):
    login_as(
        test_app,
        "test_admin",
        "admin-test-password",
    )

    response = test_app.get("/admin")

    assert response.status_code == 200


def test_admin_can_access_audit_logs(test_app):
    login_as(
        test_app,
        "test_admin",
        "admin-test-password",
    )

    response = test_app.get("/admin/audit-logs")

    assert response.status_code == 200
    assert b"Audit Log | IAM Academy" in response.data

def test_wrong_password_is_rejected(test_app):
    response = login_as(
        test_app,
        "test_customer",
        "wrong-password",
    )

    assert response.status_code == 200
    assert "Fel användarnamn eller lösenord.".encode() in response.data


def test_failed_login_is_logged(test_app):
    login_as(
        test_app,
        "test_customer",
        "wrong-password",
    )

    with sqlite3.connect(
        test_app.application.config["DATABASE_PATH"]
    ) as conn:
        row = conn.execute(
            """
            SELECT event, username, result
            FROM audit_logs
            WHERE event = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            ("login_failed",),
        ).fetchone()

    assert row == ("login_failed", "test_customer", "failure")


def test_csrf_rejects_post_without_token(test_app):
    test_app.application.config["WTF_CSRF_ENABLED"] = True

    response = test_app.post(
        "/login",
        data={
            "username": "test_customer",
            "password": "customer-test-password",
        },
    )

    assert response.status_code == 400
