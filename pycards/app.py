from flask import Flask

from pycards.models import init_db
from .config import Config
from .routes.home import home_bp
from .routes.sentence import sentence_bp
from .routes.word import word_bp

app = Flask(__name__)
app.config.from_object(Config)
# Register blueprints
app.register_blueprint(home_bp)
app.register_blueprint(sentence_bp)
app.register_blueprint(word_bp)


def main():
    with app.app_context():
        init_db()
    app.run(debug=False)


if __name__ == "__main__":
    main()
