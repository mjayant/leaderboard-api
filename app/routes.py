from flask import request, jsonify
from bson import ObjectId


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
        data = request.json

        # Check for mandatory fields
        if 'name' not in data or 'photo_url' not in data:
            return jsonify({"error": "Missing required fields: 'name' and 'photo_url' are mandatory"}), 400

        # Extract mandatory fields
        name = data['name']
        photo_url = data['photo_url']

        # Extract optional fields
        age = data.get('age')
        address = data.get('address')

        # Create user document
        user_data = {
            "name": name,
            "photo_url": photo_url,
            "points": 0
        }

        # Add optional fields if provided
        if age is not None:
            user_data["age"] = int(age)
        if address is not None:
            user_data["address"] = address

        # Insert user document into MongoDB
        user_id = mongo.db.users.insert_one(user_data).inserted_id
        return jsonify({"user_id": str(user_id)}), 201

    @app.route('/users/<user_id>', methods=['GET'])
    def get_user(user_id):
        user = User.get(mongo, user_id)
        if user:
            return jsonify(user), 200
        return jsonify({"error": "User not found"}), 404

    @app.route('/users/<user_id>', methods=['DELETE'])
    def delete_user(user_id):
        if User.delete(mongo, user_id):
            return jsonify({"message": "User deleted"}), 200
        return jsonify({"error": "User not found"}), 404

    @app.route('/users/<user_id>/points', methods=['PATCH'])
    def update_user_points(user_id):
        try:
            data = request.json
            # Check for mandatory fields
            if 'increment' not in data:
                return jsonify({"error": "Missing required field: 'increment' is mandatory"}), 400

            # Ensure increment value is an integer
            try:
                increment = int(data['increment'])
            except ValueError:
                return jsonify({"error": "Invalid value for 'increment': must be an integer"}), 400

            # Update user points
            result = User.update_points(mongo, user_id, increment)
            if result:
                result['_id'] = str(result['_id'])
                return jsonify(result), 200
            return jsonify({"error": "User not found"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/leaderboard', methods=['GET'])
    def get_leaderboard():
        users = User.get_all_sorted_by_points(mongo)
        leaderboard = []
        for user in users:
            user['_id'] = str(user['_id'])
            leaderboard.append({
                "name": user["name"],
                "points": user["points"],
                "_id": user["_id"]
            })
        return jsonify(leaderboard), 200

    @app.route('/grouped_users', methods=['GET'])
    def get_grouped_users():
        users = User.get_grouped_by_points(mongo)
        users = convert_object_ids(users)
        app.logger.info("Users list", users)
        return jsonify(users), 200

