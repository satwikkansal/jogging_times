from dotenv import load_dotenv
import os

from flask import Flask

from server.users.views import user_blueprint, jwt, api
from server.models import bcrypt, db

STATIC_FOLDER = './../client/static'
TEMPLATE_FOLDER = './../client/templates'

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER, static_url_path='')

load_dotenv('.flaskenv', verbose=True)
app_settings = os.getenv(
    'APP_SETTINGS'
)
app.config.from_object(app_settings)

bcrypt.init_app(app)
db.init_app(app)
jwt.init_app(app)
api.init_app(app)

# Blueprints
app.register_blueprint(user_blueprint, url_prefix='/user')

if __name__ == "__main__":
    port = os.getenv("PORT", 5000)
    app.run(port=port, host='0.0.0.0')

