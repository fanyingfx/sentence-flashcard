from flask import Flask

from pycards.models import init_db
from .config import Config
from .routes import main_bp

app = Flask(__name__)
app.config.from_object(Config)
# Register blueprints
app.register_blueprint(main_bp)
def main():
    with app.app_context():
        init_db()
    app.run(debug=True)


if __name__ == '__main__':
    main()