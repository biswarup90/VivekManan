from flask import Flask, request, jsonify, send_from_directory
from annoy import AnnoyIndex
from pymongo import MongoClient
import pandas as pd
import os

pd.set_option('display.max_colwidth', None)

app = Flask(__name__)

MONGO_HOST = "mongodb"
MONGO_PORT = 27017
MONGO_DB = "scraped_data"
MONGO_COLLECTION = "swami_vivekananda"

num_responses = 4
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-mpnet-base-v2')


def connect_to_mongodb():
    client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    return collection





def analyze_sbert(query):
    collection = connect_to_mongodb()
    cursor = collection.find({"embedding": {"$exists": True}})
    embeds = []
    texts = []
    urls = []
    for doc in cursor:
        embeds.append(doc["embedding"])
        texts.append(doc["text"])
        urls.append(doc["url"])

    index_metadata = collection.find_one({"_id": "index_metadata"})
    if not index_metadata:
        print("Index metadata not found in MongoDB")
        return None

    index_file_path = index_metadata["index_file_path"]
    if not os.path.isfile(index_file_path):
        print(f"File not found: {index_file_path}")
        return None
    print(f"Loading Annoy index from {index_file_path}")

    # Assuming the dimensionality of the embeddings is known
    print("Embedding dim: ", len(embeds[0]))
    f = 4096  # Replace with the actual dimensionality
    search_index = AnnoyIndex(len(embeds[0]), 'angular')
    search_index.load(index_file_path)
    print("Annoy index loaded successfully")

    query_embed = model.encode(query)
    similar_item_ids = search_index.get_nns_by_vector(query_embed, num_responses, include_distances=True)
    extracted_text = [texts[i] for i in similar_item_ids[0]]
    extracted_url = [urls[i] for i in similar_item_ids[0]]

    results = pd.DataFrame(data={'texts': extracted_text, 'urls': extracted_url, 'distance': similar_item_ids[1]})
    result_text = results['texts'].tolist()
    result_url = results['urls'].tolist()

    return result_text, result_url


@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    data = request.get_json()
    query = data.get('query')
    print("Query: ", query)
    if not query:
        return jsonify({"error": "Query parameter is missing"}), 400

    response_texts, response_urls = analyze_sbert(query)
    response_data = [{"text": text, "url": url} for text, url in zip(response_texts, response_urls)]
    print(response_urls)
    return jsonify(response_data)


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
