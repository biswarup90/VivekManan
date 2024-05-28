from pymongo import MongoClient
import numpy as np
import cohere
from annoy import AnnoyIndex
from datetime import datetime
import httpx
import time
# MongoDB connection settings
MONGO_HOST = "mongodb"
MONGO_PORT = 27017
MONGO_DB = "scraped_data"
MONGO_COLLECTION = "swami_vivekananda"

api_key = 'your-api-key-here'
co = cohere.Client(api_key)


def serialize_annoy(index):
    f = index.f
    trees = index.get_n_trees()
    num_items = index.get_n_items()
    vectors = [index.get_item_by_index(i) for i in range(num_items)]  # Extract vector data
    # Include other metadata if needed
    return {'f': f, 'trees': trees, 'vectors': vectors}


# Function to connect to MongoDB
def connect_to_mongodb():
    client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    return collection


# Function to analyze scraped contents
def generate_embeddings():
    collection = connect_to_mongodb()
    print(f"Connected to MongoDB: {collection}")
    # Find all documents that do not have embeddings
    cursor = collection.find({
        "embedding": {"$exists": False},
        "_id": {"$ne": "index_metadata"}
    })

    texts = []
    ids = []

    for doc in cursor:
        texts.append(doc["text"])
        ids.append(doc["_id"])

    if texts:
        # Create embeddings for the texts
        embeddings = co.embed(texts=texts).embeddings
        embeds = np.array(embeddings)

        # Update each document with the corresponding embedding
        for doc_id, embedding in zip(ids, embeds):
            collection.update_one(
                {"_id": doc_id},
                {"$set": {"embedding": embedding.tolist()}}
            )
        print("Embeddings generated and saved to MongoDB with dimensionality shap: ", embeds.shape[1])
        search_index = AnnoyIndex(embeds.shape[1], 'euclidean')
        print(search_index)
        # Add all the vectors to the search index
        for i in range(len(embeds)):
            search_index.add_item(i, embeds[i])

        search_index.build(10)

        index_file_path = '/shared-data/annoy_index.ann'
        search_index.save(index_file_path)
        print(f"Annoy index saved to {index_file_path}")

        # Store metadata in MongoDB
        index_metadata = {
            "index_file_path": index_file_path,
            "description": "Annoy index for text embeddings",
            "created_at": datetime.utcnow()
        }
        collection.update_one(
            {"_id": "index_metadata"},
            {"$set": index_metadata},
            upsert=True
        )
        print("Index metadata saved to MongoDB")


def generate_embeddings_batched(batch_size=2, sleep_time=5):
    collection = connect_to_mongodb()
    print(f"Connected to MongoDB: {collection}")

    # Find all documents that do not have embeddings and exclude 'index_metadata'
    cursor = collection.find({
        "embedding": {"$exists": False},
        "_id": {"$ne": "index_metadata"}
    })

    texts = []
    ids = []

    for doc in cursor:
        texts.append(doc["text"])
        ids.append(doc["_id"])

    if texts:
        all_embeddings = []
        all_ids = []

        # Process texts in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            embeddings = None
            # Retry logic for embedding API call
            for attempt in range(3):
                try:
                    # Create embeddings for the batch
                    embeddings = co.embed(texts=batch_texts).embeddings
                    break  # Exit retry loop if successful
                except (httpx.RequestError, httpx.HTTPStatusError) as e:
                    print(f"Error during embedding API call: {e}")
                    if attempt < 2:
                        print(f"Retrying... (Attempt {attempt + 2}/3)")
                        time.sleep(sleep_time)
                    else:
                        raise

            batch_embeds = np.array(embeddings)
            all_embeddings.extend(batch_embeds)
            all_ids.extend(batch_ids)

            # Update each document with the corresponding embedding
            for doc_id, embedding in zip(batch_ids, batch_embeds):
                collection.update_one(
                    {"_id": doc_id},
                    {"$set": {"embedding": embedding.tolist()}}
                )
            print(f"Processed batch {i // batch_size + 1}, sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)

        embeds = np.array(all_embeddings)
        print("Embeddings generated and saved to MongoDB with dimensionality shape:", embeds.shape[1])

        # Create the Annoy index
        search_index = AnnoyIndex(embeds.shape[1], 'euclidean')
        for i in range(len(embeds)):
            search_index.add_item(i, embeds[i])

        search_index.build(10)

        # Save the Annoy index to a file
        index_file_path = '/shared-data/annoy_index.ann'
        search_index.save(index_file_path)
        print(f"Annoy index saved to {index_file_path}")

        # Store metadata in MongoDB
        index_metadata = {
            "_id": "index_metadata",
            "index_file_path": index_file_path,
            "description": "Annoy index for text embeddings",
            "created_at": datetime.utcnow()
        }
        collection.update_one(
            {"_id": "index_metadata"},
            {"$set": index_metadata},
            upsert=True
        )
        print("Index metadata saved to MongoDB")


if __name__ == "__main__":
    generate_embeddings()
