from flask import Flask, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask_pymongo import PyMongo
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os
from .logger import logger
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config['S3_BUCKET'] = os.getenv('S3_BUCKET')
    app.config['S3_KEY'] = os.getenv('S3_KEY')
    app.config['S3_SECRET'] = os.getenv('S3_SECRET')
    app.config['S3_LOCATION'] = f'http://{app.config["S3_BUCKET"]}.s3.amazonaws.com/'

    mongo = PyMongo(app)
    scheduler = BackgroundScheduler()

    # Swagger UI configuration
    SWAGGER_URL = '/swagger'
    API_URL = '/swagger.yaml'  # URL to your Swagger API definition

    # Create a Swagger UI blueprint
    swagger_ui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "app"  # Swagger UI configuration
        }
    )

    # Register the Swagger UI blueprint with your Flask app
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    from app.routes import init_routes  # Import routes after initializing the app to avoid circular dependency
    init_routes(app, mongo)

    @app.route('/swagger.yaml')
    def swagger_yaml():
        return send_from_directory(os.path.dirname(app.root_path), 'swagger.yaml')

    from app.scheduler import init_scheduler, shutdown_scheduler
    # Initialize scheduler
    init_scheduler(mongo, scheduler)

    # Print all registered routes for debugging
    for rule in app.url_map.iter_rules():
        logger.info(f"Endpoint: {rule.endpoint}, URL: {rule}")

    atexit.register(lambda: shutdown_scheduler(scheduler))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
