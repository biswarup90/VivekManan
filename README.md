# Semantic Search in Swami Vivekananda's Complete Works
## Overview
This project provides a semantic search tool for Swami Vivekananda's Complete Works. It allows students, researchers, and enthusiasts to search topics, keywords, and quotes from the vast collection of Swami Vivekananda's writings. The search leverages advanced text embedding techniques to ensure that the results are contextually relevant, going beyond simple keyword matching.
## Features
Comprehensive Coverage: Includes the entire collection of Swami Vivekananda's works.
Semantic Search: Uses state-of-the-art text embeddings to understand the context and return relevant results.
Top Matches: Returns the top 3 most relevant passages for each query.
Scalable and Fast: Utilizes Annoy indexes for quick retrieval of search results.
Dockerized Deployment: The entire project is containerized for easy setup and deployment.
## Project Structure
### Scraper
Scrap the CWSV
Save the scrapped content to db
### Indexer
Read Scrapped Text
Create Text Embeddings
ANN Index Embeddings 
Save to DB
### Analyzer
Take Query String
Create text embedding of query
Find closest texts from ANN indices
### Web Tier
Host web page to accept user query
Query Analyzer; get response
Display closest items

![VivekManan](https://github.com/biswarup90/VivekManan/assets/3035219/a6b0f08e-31a0-4bf9-b6c9-ddaa1a6a1c5a)


## Semantic Search Explained
Semantic search is an advanced technique that uses natural language processing (NLP) to understand the meaning and context of the text. Unlike traditional keyword-based search, which looks for exact matches of words, semantic search interprets the user's query to find contextually relevant information.
## How It Works
Data Scraping: The complete works of Swami Vivekananda are scraped and preprocessed.
Text Embedding: Each document is converted into a dense vector representation (embedding) using a pre-trained NLP model.
Indexing: The embeddings are indexed using Annoy (Approximate Nearest Neighbors Oh Yeah), which allows for efficient similarity search.
Query Processing: When a user submits a query, it is also converted into an embedding.
Similarity Search: The query embedding is compared against the precomputed embeddings using the Annoy index to find the closest matches.
Results: The top 3 most similar passages are returned to the user
## Setup and Installation
### Prerequisites
Docker
### Steps
1. Clone the Repository
2. Build and Run the Docker Services
```
docker-compose up --build
```
3. Access the Web Application
Open your web browser and navigate to http://localhost:5000 to access the search interface.
4. Note - You will need to use your api-key for cohere from here - https://dashboard.cohere.com/api-keys
## Enhancements
This project can be further improved by:

1. Using Better Embedding Models: Implementing more advanced models like BERT, GPT, or other transformer-based models for improved accuracy.
2. Expanding the Database: Including more texts and related literature.
3. Optimizing Performance: Enhancing indexing and retrieval mechanisms for faster results.

We hope this project aids in your research and exploration of Swami Vivekananda's profound works. Happy searching!

For any questions or support, please contact [biswarup.cst@gmail.com].

