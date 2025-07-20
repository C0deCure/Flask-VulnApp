from flask import Flask
from app.blueprints.message import message_bp
# from app.extensions import db
# from app.config import Config

def create_app():
    app = Flask(__name__)
    
    # app.config.from_object(Config)
    
    # db.init_app(app)
    
    app.register_blueprint(message_bp, url_prefix="/message")
    
    return app