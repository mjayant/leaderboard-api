from datetime import datetime
from app.logger import logger


def identify_winner(mongo):
    try:
        highest_point_users = list(mongo.db.users.find().sort("points", -1).limit(2))

        if len(highest_point_users) >= 2:
            if highest_point_users[0]['points'] != highest_point_users[1]['points']:
                logger.info("Inserting winner into DB")
                logger.info("Winner Details: %s", highest_point_users)
                mongo.db.winners.insert_one({
                    "user_id": highest_point_users[0]["_id"],
                    "points": highest_point_users[0]["points"],
                    "timestamp": datetime.utcnow()
                })
        else:
            logger.warning("Not enough users to identify winners.")

    except Exception as e:
        logger.error(f"An error occurred while identifying winners: {str(e)}")


def init_scheduler(mongo, scheduler):
    try:
        if not scheduler.running:
            scheduler.add_job(func=lambda: identify_winner(mongo), trigger="interval", minutes=5)
            scheduler.start()
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {str(e)}")


def shutdown_scheduler(scheduler):
    try:
        if scheduler.running:
            scheduler.shutdown()
    except Exception as e:
        logger.error(f"Failed to shutdown scheduler: {str(e)}")
