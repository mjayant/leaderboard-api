from bson import ObjectId
import datetime

class User:
    @staticmethod
    def create(mongo, name, age, address, photo_url):
        user = {
            "name": name,
            "age": age,
            "address": address,
            "photo_url": photo_url,
            "points": 0,
            "created_at": datetime.datetime.utcnow()
        }
        return mongo.db.users.insert_one(user).inserted_id

    @staticmethod
    def get(mongo, user_id):
        return mongo.db.users.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def delete(mongo, user_id):
        result = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    @staticmethod
    def update_points(mongo, user_id, increment):
        result = mongo.db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$inc": {"points": increment}},
            return_document=True
        )
        return result

    @staticmethod
    def get_all_sorted_by_points(mongo):
        return list(mongo.db.users.find().sort("points", -1))

    @staticmethod
    def get_grouped_by_points(mongo):
        pipeline = [
            {
                "$group": {
                    "_id": "$points",
                    "names": {"$push": "$name"},
                    "average_age": {"$avg": "$age"}
                }
            },
            {"$sort": {"_id": -1}}
        ]
        results = list(mongo.db.users.aggregate(pipeline))

        # Transform the results to match the required format
        grouped_by_points = {}
        for result in results:
            grouped_by_points[result["_id"]] = {
                "names": result["names"],
                "average_age": result["average_age"]
            }
        return grouped_by_points


class Winner:
    @staticmethod
    def create(mongo, user_id, points):
        winner = {
            "user_id": ObjectId(user_id),
            "points": points,
            "timestamp": datetime.datetime.utcnow()
        }
        return mongo.db.winners.insert_one(winner).inserted_id

    @staticmethod
    def get_all(mongo):
        return list(mongo.db.winners.find().sort("timestamp", -1))
