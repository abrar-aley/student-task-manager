import os
from app import create_app

config_class = os.environ.get("FLASK_CONFIG", "app.config.DevConfig")
app = create_app(config_class)

if __name__ == "__main__":
    app.run(debug=True)
