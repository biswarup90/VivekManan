import requests
from bs4 import BeautifulSoup
# import numpy as np
import cohere
# from annoy import AnnoyIndex
# import pandas as pd
from urllib.parse import urljoin

api_key = 'your-api-key-here'
co = cohere.Client(api_key)

base_urls = ['https://www.ramakrishnavivekananda.info/vivekananda/master_index.htm']

urls_to_remove = ['https://www.ramakrishnavivekananda.info/index.htm',
                  'https://www.ramakrishnavivekananda.info/vivekananda/complete_works.htm',
                  'http://ramakrishnavivekananda.info/vivekananda/completeworksindex.xlsx']

from pymongo import MongoClient

# MongoDB connection settings
MONGO_HOST = "mongodb"
MONGO_PORT = 27017
MONGO_DB = "scraped_data"
MONGO_COLLECTION = "swami_vivekananda"


# Function to connect to MongoDB
def connect_to_mongodb():
    client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    return collection


def scrape_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    text = ' '.join(paragraph.text for paragraph in paragraphs)
    return text


def fetch_and_process_urls(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    url_list = []
    # Extract all links from the page
    links = soup.find_all('a', href=True)

    for link in links:
        # Get the absolute URL
        absolute_url = urljoin(base_url, link['href'])
        url_list.append(absolute_url)

    my_list = [x for x in url_list if x not in urls_to_remove]
    return my_list


def main():
    url_list = []
    for url in base_urls:
        url_list = fetch_and_process_urls(url)

    collection = connect_to_mongodb()

    for link in url_list[:1]:
        chapter = scrape_text(link)
        sentences = chapter.split('.')
        print("Scrapper")
        for sentence in sentences:
            result = collection.update_one(
                {"url": link, "text": sentence},  # Criteria to match existing documents
                {"$setOnInsert": {"url": link, "text": sentence}},  # Fields to insert if no match is found
                upsert=True  # Perform an insert if no matching document is found
            )
            print(f"Inserted document with id: {result.upserted_id}")


if __name__ == "__main__":
    main()
