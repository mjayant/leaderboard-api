# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy all files from current directory to /app in the container
COPY . .

# Set PYTHONPATH environment variable to /app so Python can find your modules
ENV PYTHONPATH=/app

# Expose port 5000 (default Flask port)
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app/__init__.py"]
