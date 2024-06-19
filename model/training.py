import pandas as pd
from datasets import load_dataset
from sentence_transformers import InputExample
from sentence_transformers import losses
from torch.utils.data import DataLoader

from sentence_transformers import SentenceTransformer

df = load_dataset('csv', data_files='dataset.csv')

print(f"- The dataset has {df.num_rows} examples.")
print(f"- Each example is a {type(df['train'][0])} with a {type(df['train'][0]['positive'])} as value.")
print(f"- Examples look like this: {df['train'][0]}")

train_examples = []
train_data = df['train']

n_examples = len(df)

for i in range(n_examples):
    example = train_data[i]
    train_examples.append(InputExample(texts=[example['query'], example['positive'][0]]))

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

model_id = "sentence-transformers/all-mpnet-base-v2"
model = SentenceTransformer(model_id)

train_loss = losses.MultipleNegativesRankingLoss(model=model)

model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=10)
