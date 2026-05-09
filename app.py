import os
from dotenv import load_dotenv
from flask import Flask

from flourish.routes import bp


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")
    app.register_blueprint(bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
