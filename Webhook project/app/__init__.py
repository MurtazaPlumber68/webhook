from flask import Flask
from app.webhook.routes import webhook
from app.extensions import mongo

def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = "mongodb://localhost:27017/github_events"
    
    mongo.init_app(app)
    
    app.register_blueprint(webhook)
    return app