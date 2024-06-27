from datetime import datetime

def identify_winner(mongo):
    highest_point_user = list(mongo.db.users.find().sort("points", -1).limit(2))
    # Check if there are at least 2 users with highest points
    if len(highest_point_user) >= 2:
        if highest_point_user[0]['points'] != highest_point_user[1]['points']:
            mongo.db.winners.insert_one({
                "user_id": highest_point_user[0]["_id"],
                "points": highest_point_user[0]["points"],
                "timestamp": datetime.utcnow()
            })
    else:
        # Handle the case where there are fewer than 2 users
        print("Not enough users to identify winners.")

def init_scheduler(mongo, scheduler):
    if not scheduler.running:
        scheduler.add_job(func=lambda: identify_winner(mongo), trigger="interval", minutes=5)
        scheduler.start()

def shutdown_scheduler(scheduler):
    if scheduler.running:
        scheduler.shutdown()
