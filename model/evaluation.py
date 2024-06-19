from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load the trained model
model_save_path = 'trained_model'
model = SentenceTransformer(model_save_path)

# Example sentences
sentences = [
    "This is a sentence for which we want to generate embeddings.",
    "Here is another sentence to test the model.",
    "This is a different sentence to see how similar it is to the first one."
]

# Generate embeddings
embeddings = model.encode(sentences)

# Print embeddings
for sentence, embedding in zip(sentences, embeddings):
    print(f"Sentence: {sentence}")
    print(f"Embedding: {embedding[:5]}... (truncated for brevity)\n")

# Perform similarity search
# Compute cosine similarity between the first sentence and the rest
cosine_similarities = cosine_similarity([embeddings[0]], embeddings[1:])[0]

# Print similarities
for i, similarity in enumerate(cosine_similarities, start=1):
    print(f"Similarity between sentence 1 and sentence {i+1}: {similarity:.4f}")
