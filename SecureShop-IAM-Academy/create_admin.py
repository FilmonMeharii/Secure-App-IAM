import sqlite3
from pathlib import Path
from getpass import getpass
from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).with_name("secureshop.db")

username = input("Administratörens användarnamn: ").strip()
password = getpass("Lösenord: ")
confirm_password = getpass("Bekräfta lösenord: ")

if not username:
    raise SystemExit("Användarnamnet får inte vara tomt.")

if len(password) < 12:
    raise SystemExit("Lösenordet måste vara minst 12 tecken.")

if password != confirm_password:
    raise SystemExit("Lösenorden matchar inte.")

with sqlite3.connect(DB_PATH) as conn:
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if existing:
        raise SystemExit("Användarnamnet finns redan.")

    password_hash = generate_password_hash(password)

    conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, "admin")
    )

print("Administratörskontot har skapats.")
