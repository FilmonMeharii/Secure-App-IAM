# SecureShop IAM Academy

This repository contains a small Flask-based e-commerce demo application used to practice identity, access control, and secure application hardening.

The app simulates a retail shop with user registration, login, role-based access, shopping cart functionality, and a protected admin area for audit log review.

## Project purpose

SecureShop IAM Academy is designed as a hands-on learning project for:

- authentication and password handling
- role-based authorization
- CSRF protection
- failed-login lockout logic
- audit logging and access monitoring
- secure configuration and secret management

## Tech stack

- Python 3
- Flask
- Flask-WTF
- SQLite
- Pytest

## App overview

The application includes:

- customer registration and login
- cart management for products
- account and IAM pages
- admin-only access to administrative features
- audit log view restricted to administrators
- login lockout after repeated failed attempts

## Repository structure

```text
SecureShop-IAM-Academy/
├── app.py                  # Flask app bootstrap
├── audit.py                # Security event logging
├── config.py               # Application configuration and DB path
├── create_admin.py         # Helper to create an admin user
├── extensions.py           # Flask extension initialization
├── security.py             # Login lockout logic
├── secureshop.db           # SQLite database
├── routes/
│   ├── auth.py             # Login/register/logout routes
│   ├── iam.py              # IAM and admin authorization routes
│   └── shop.py             # Store and cart routes
├── static/
│   └── style.css           # Styling
├── templates/              # HTML templates
├── tests/
│   └── test_security.py    # Security-related tests
└── ...
```

## Requirements

Install the required Python packages:

```bash
pip install flask flask-wtf pytest
```

## Configuration

The app expects a secret key in the environment before startup.

```bash
export FLASK_SECRET_KEY="your-secret-key"
```

On Windows PowerShell:

```powershell
$env:FLASK_SECRET_KEY = "your-secret-key"
```

## Running the app

From the project directory:

```bash
cd SecureShop-IAM-Academy
python app.py
```

Then open the app in your browser at:

```text
http://127.0.0.1:5000/
```

## Creating an admin account

Use the helper script:

```bash
python create_admin.py
```

Follow the prompts to create an administrator account with the `admin` role.

## Testing

Run the automated tests with:

```bash
pytest
```

The test suite checks:

- customer restrictions on admin pages
- admin access to protected routes
- invalid login handling
- audit event logging
- CSRF enforcement

## Security notes

This project is intentionally structured as a security training application. It demonstrates common application security controls and helps users explore issues around access control, secrets, and secure authentication practices.

## License

This project is provided for educational and training purposes.
