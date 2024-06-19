# Use an official Python runtime as a parent image
FROM python:3.9-slim

RUN apt-get update && \
    apt-get -y install gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install requests beautifulsoup4 cohere numpy pandas pymongo annoy sentence_transformers

# Run scrapper.py when the container launches
CMD ["python", "indexer_local_embedding.py"]