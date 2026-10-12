from flask import Flask
from flask_wtf.csrf import generate_csrf

from config import Config
from extensions import csrf
from routes.auth import auth_bp
from routes.shop import shop_bp
from routes.iam import iam_bp

app = Flask(__name__)
app.config.from_object(Config)
app.jinja_env.globals["generate_csrf"] = generate_csrf

csrf.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(iam_bp)


if __name__ == "__main__":
    app.run(debug=True)