import os
from flask import request, jsonify
from bson import ObjectId
from .logger import logger
from . import utils

def init_routes(app, mongo):
    from app.models import User, Winner

    def convert_object_ids(data):
        if isinstance(data, list):
            return [convert_object_ids(item) for item in data]
        elif isinstance(data, dict):
            return {key: convert_object_ids(value) for key, value in data.items()}
        elif isinstance(data, ObjectId):
            return str(data)
        else:
            return data

    @app.route('/users', methods=['POST'])
    def create_user():
        try:
            # Get other form data
            name = request.form.get('name')
            photo_url = ''
            if not name:
                logger.error("Missing mandatory fields: 'name' is required")
                return jsonify({"error": "Missing mandatory fields: 'name' and 'photo_url' are required"}), 400
            age = request.form.get('age')
            address = request.form.get('address')
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo.filename == '':
                    return jsonify({"error": "No selected file"}), 400
                s3_obj = utils.create_s3_object(os.getenv("S3_KEY"), os.getenv("S3_SECRET"))
                if s3_obj is None:
                    logger.error("Failed to create S3 client")
                    return jsonify({"error": "Failed to create S3 client"}), 500
                photo_url = utils.upload_file_to_s3(photo, os.getenv('S3_BUCKET'), s3_obj, app.config['S3_LOCATION'])
                if photo_url is None:
                    logger.error("Failed to upload photo")
                    return jsonify({"error": "Failed to upload photo"}), 500

            user_data = {
                "name": name,
                "photo_url": photo_url,
                "points": 0  # Initialize points to 0
            }

            # Optional fields
            if age:
                user_data["age"] = int(age)
            if address:
                user_data["address"] = address

            user_id = mongo.db.users.insert_one(user_data).inserted_id

            logger.info("User created with ID: %s", str(user_id))
            return jsonify({"user_id": str(user_id)}), 201

        except Exception as e:
            logger.error("An error occurred while creating user: %s", str(e))
            return jsonify({"error": "Internal Server Error"}), 500

    @app.route('/users/<user_id>', methods=['GET'])
    def get_user(user_id):
        try:
            user = User.get(mongo, user_id)
            if user:
                user = convert_object_ids(user)
                return jsonify(user), 200
            else:
                logger.warning("User not found: %s", user_id)
                return jsonify({"error": "User not found"}), 404
        except Exception as e:
            logger.error("An error occurred while retrieving user: %s", str(e))
            return jsonify({"error": "Internal Server Error"}), 500

    @app.route('/users/<user_id>', methods=['DELETE'])
    def delete_user(user_id):
        try:
            if User.delete(mongo, user_id):
                logger.info("User deleted: %s", user_id)
                return jsonify({"message": "User deleted"}), 200
            else:
                logger.warning("User not found: %s", user_id)
                return jsonify({"error": "User not found"}), 404
        except Exception as e:
            logger.error("An error occurred while deleting user: %s", str(e))
            return jsonify({"error": "Internal Server Error"}), 500

    @app.route('/users/<user_id>/points', methods=['PATCH'])
    def update_user_points(user_id):
        try:
            data = request.json
            # Check for mandatory fields
            if 'increment' not in data:
                logger.error("Missing required field: 'increment'")
                return jsonify({"error": "Missing required field: 'increment' is mandatory"}), 400

            # Ensure increment value is an integer
            try:
                increment = int(data['increment'])
            except ValueError:
                logger.error("Invalid value for 'increment': must be an integer")
                return jsonify({"error": "Invalid value for 'increment': must be an integer"}), 400

            # Update user points
            result = User.update_points(mongo, user_id, increment)
            if result:
                result['_id'] = str(result['_id'])
                logger.info("Updated points for user %s: %s", user_id, result)
                return jsonify(result), 200
            else:
                logger.warning("User not found: %s", user_id)
                return jsonify({"error": "User not found"}), 404

        except Exception as e:
            logger.error("An error occurred while updating user points: %s", str(e))
            return jsonify({"error": "Internal Server Error"}), 500

    @app.route('/leaderboard', methods=['GET'])
    def get_leaderboard():
        try:
            users = User.get_all_sorted_by_points(mongo)
            leaderboard = []
            for user in users:
                user['_id'] = str(user['_id'])
                leaderboard.append({
                    "name": user["name"],
                    "points": user["points"],
                    "_id": user["_id"]
                })
            logger.info("Fetched leaderboard")
            return jsonify(leaderboard), 200
        except Exception as e:
            logger.error("An error occurred while fetching the leaderboard: %s", str(e))
            return jsonify({"error": "Internal Server Error"}), 500

    @app.route('/grouped_users', methods=['GET'])
    def get_grouped_users():
        try:
            users = User.get_grouped_by_points(mongo)
            users = convert_object_ids(users)
            logger.info("Fetched grouped users: %s", users)
            return jsonify(users), 200
        except Exception as e:
            logger.error("An error occurred while fetching grouped users: %s", str(e))
            return jsonify({"error": "Internal Server Error"}), 500
