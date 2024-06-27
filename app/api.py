from flask import request, jsonify
from . import app, mongo
from .utils import upload_file_to_s3, allowed_file
from bson.objectid import ObjectId
import random

@app.route('/users', methods=['POST'])
def create_user():
    name = request.form.get('name')
    age = request.form.get('age')
    address = request.form.get('address')
    points = 0

    if 'photo' not in request.files:
        return jsonify({"error": "No photo provided"}), 400

    file = request.files['photo']

    if file and allowed_file(file.filename):
        photo_url = upload_file_to_s3(file, app.config["S3_BUCKET"])
    else:
        return jsonify({"error": "Invalid file type"}), 400

    user_id = mongo.db.users.insert_one({
        "name": name,
        "age": int(age),
        "address": address,
        "points": points,
        "photo_url": photo_url
    }).inserted_id

    return jsonify({"id": str(user_id)}), 201

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": "User deleted"}), 200

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    user['_id'] = str(user['_id'])
    return jsonify(user), 200

@app.route('/users/<user_id>/points', methods=['PATCH'])
def update_points(user_id):
    increment = request.json.get('increment', 0)
    result = mongo.db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$inc": {"points": increment}},
        return_document=True
    )
    if not result:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"points": result["points"]}), 200


@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    users = mongo.db.users.find().sort("points", -1)
    leaderboard = [{"name": user["name"], "points": user["points"]} for user in users]
    return jsonify(leaderboard), 200

@app.route('/grouped_users', methods=['GET'])
def get_grouped_users():
    pipeline = [
        {"$group": {"_id": "$points", "names": {"$push": "$name"}, "average_age": {"$avg": "$age"}}}
    ]
    results = list(mongo.db.users.aggregate(pipeline))
    response = {str(result["_id"]): {"names": result["names"], "average_age": result["average_age"]} for result in
                results}
    return jsonify(response), 200

@app.route('/test-mongo')
def test_mongo():
    try:
        mongo.db.command('ping')
        return 'MongoDB connected successfully!'
    except Exception as e:
        return f'MongoDB connection failed: {str(e)}'
