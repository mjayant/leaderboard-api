Here's a more organized and clear version of your README file:

# Leaderboard API

This project is a Flask-based API for managing a leaderboard. It includes endpoints for user management, point updates, and leaderboard retrieval. The application uses MongoDB for data storage and AWS S3 for file storage.

## Prerequisites

1. **Docker**: Ensure that Docker and Docker Compose are installed on your machine. You can download Docker from [here](https://www.docker.com/get-started).

2. **MongoDB Atlas**: You can use the provided MongoDB Atlas cluster or set up your own.

## Using the Provided MongoDB Atlas Cluster

1. **Whitelist Your IP Address**:
   - Ask the project owner to whitelist your IP address on their MongoDB Atlas cluster.

2. **Update `.env` File**:
   - The project owner will provide you with the MongoDB connection string. Update your `.env` file with this connection string.
   - Your `.env` file should look like this:
     ```plaintext
     MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/leaderboard?retryWrites=true&w=majority
     S3_BUCKET=your-s3-bucket
     S3_KEY=your-aws-access-key
     S3_SECRET=your-aws-secret-key
     ```

## Setting Up MongoDB Atlas (If Setting Up Your Own Cluster)

1. **Sign Up / Log In**:
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and sign up for a free account or log in if you already have one.

2. **Create a Cluster**:
   - Follow the prompts to create a new cluster. Choose the free tier (M0 Sandbox) for a basic setup.

3. **Create a Database User**: 
   - Go to the "Database Access" tab and create a new database user with a username and password. Ensure the user has read and write access to your databases.

4. **Network Access**: 
   - Go to the "Network Access" tab and add your IP address to the IP whitelist to allow your local machine to connect to the cluster.

5. **Get Connection String**: 
   - Go to the "Clusters" tab, click "Connect", and follow the steps to get your connection string. It will look something like this:
     ```
     mongodb+srv://<username>:<password>@cluster0.mongodb.net/leaderboard?retryWrites=true&w=majority
     ```
   - Replace `<username>`, `<password>`, and `<dbname>` with your database user credentials and desired database name (e.g., `leaderboard`).

6. **Update `.env` File**:
   - Your `.env` file should look like this:
     ```plaintext
     MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/leaderboard?retryWrites=true&w=majority
     S3_BUCKET=your-s3-bucket
     S3_KEY=your-aws-access-key
     S3_SECRET=your-aws-secret-key
     ```

## Setting Up the Project

1. **Clone the Repository**:
   ```bash
   git clone <your-repo-url>
   cd leaderboard-api
   ```

2. **Install Dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Build and run the Docker containers**:
   ```bash
   docker-compose up --build
   ```

4. **Access the API**:
   - Open your browser and go to `http://localhost:5000`

## Populating the Database with Initial Users

To populate the database with initial users with random values, use the model factory:

1. Ensure your virtual environment is activated.
2. Run the `populate_db.py` script.
   ```bash
   docker-compose exec api python populate_db.py
   ```
3. Enter the number of users you want to create when prompted.

This will insert the specified number of users into the MongoDB database with random values.

## Endpoints

- `POST /users`: Create a new user with a photo upload
- `DELETE /users/<user_id>`: Delete a user
- `GET /users/<user_id>`: Get user details
- `PATCH /users/<user_id>/points`: Update user points
- `GET /leaderboard`: Get the leaderboard
- `GET /grouped_users`: Get users grouped by score with average age

## Running Tests
To run the unit tests:

    Using Docker Compose: Run the tests using the following command:
    docker-compose run test
This will execute all unit tests in the tests directory.
 
This setup ensures that your tests run in the same environment as your application, providing consistency across different development environments.


## Swagger Documentation

Access the Swagger documentation at `http://localhost:5000/swagger`

---

