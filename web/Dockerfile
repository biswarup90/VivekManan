# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install necessary dependencies
RUN apt-get update && \
    apt-get -y install gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install requests beautifulsoup4 numpy pandas pymongo annoy flask sentence_transformers

# Expose the port the app runs on
EXPOSE 5000

# Run app.py (the Flask app) when the container launches
CMD ["python", "app.py"]
