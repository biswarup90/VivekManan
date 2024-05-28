from annoy import AnnoyIndex
from pymongo import MongoClient
import pandas as pd
import cohere
import os
pd.set_option('display.max_colwidth', None)

MONGO_HOST = "mongodb"
MONGO_PORT = 27017
MONGO_DB = "scraped_data"
MONGO_COLLECTION = "swami_vivekananda"

api_key = 'your-api-key-here'
co = cohere.Client(api_key)
num_responses = 4


def connect_to_mongodb():
    client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    return collection


def rerank_responses(query, responses, num_responses=num_responses):
    reranked_responses = co.rerank(
        model='rerank-english-v2.0',
        query=query,
        documents=responses,
        top_n=num_responses,
        return_documents=True
    )
    return reranked_responses


def analyze(query):
    collection = connect_to_mongodb()
    cursor = collection.find({"embedding": {"$exists": True}})
    embeds = []
    texts = []
    for doc in cursor:
        embeds.append(doc["embedding"])
        texts.append(doc["text"])

    if embeds:
        search_index = AnnoyIndex(len(embeds[0]), 'euclidean')
        for i in range(len(embeds)):
            search_index.add_item(i, embeds[i])
        search_index.build(10)

        query_embed = co.embed(texts=[query]).embeddings
        similar_item_ids = search_index.get_nns_by_vector(query_embed[0], num_responses, include_distances=True)
        extracted_text = [texts[i] for i in similar_item_ids[0]]

        results = pd.DataFrame(data={'texts': extracted_text, 'distance': similar_item_ids[1]})
        reranked_text = rerank_responses(query, results['texts'].tolist())

        response_texts = []
        for rerank_result in reranked_text:
            if isinstance(rerank_result, tuple) and rerank_result[0] == 'results':
                for item in rerank_result[1]:
                    response_texts.append(item.document.text)
        print(response_texts)
    return []

def analyze_v2(query):
    collection = connect_to_mongodb()
    cursor = collection.find({"embedding": {"$exists": True}})
    embeds = []
    texts = []
    for doc in cursor:
        embeds.append(doc["embedding"])
        texts.append(doc["text"])

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
    search_index = AnnoyIndex(len(embeds[0]), 'euclidean')
    search_index.load(index_file_path)
    print("Annoy index loaded successfully")

    query_embed = co.embed(texts=[query]).embeddings
    similar_item_ids = search_index.get_nns_by_vector(query_embed[0], num_responses, include_distances=True)
    extracted_text = [texts[i] for i in similar_item_ids[0]]

    results = pd.DataFrame(data={'texts': extracted_text, 'distance': similar_item_ids[1]})
    reranked_text = rerank_responses(query, results['texts'].tolist())

    response_texts = []
    for rerank_result in reranked_text:
        if isinstance(rerank_result, tuple) and rerank_result[0] == 'results':
            for item in rerank_result[1]:
                response_texts.append(item.document.text)
    print(response_texts)



if __name__ == "__main__":
    analyze_v2("What is attachment?")
