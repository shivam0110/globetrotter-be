import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from app.models import prisma

def create_app():
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Enable CORS for all routes and all origins
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Import routes
    from app import routes
    # from app import users
    # from app import destinations
    
    # Register routes with the app
    routes.register_routes(app)
    # users.register_routes(app)
    # destinations.register_routes(app)
    
    # Add a test route directly in __init__.py to verify routing works
    @app.route('/test')
    def test():
        return "API is working!"
    
    print("Routes registered successfully")
    return app
