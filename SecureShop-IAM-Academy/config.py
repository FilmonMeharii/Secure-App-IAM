import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "secureshop.db"

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError(
            "FLASK_SECRET_KEY saknas. Ange miljövariabeln innan appen startas."
        )

    DATABASE_PATH = DATABASE_PATH