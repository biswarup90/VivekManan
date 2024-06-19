import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pymongo import MongoClient
import re

base_urls = ['https://www.ramakrishnavivekananda.info/vivekananda/master_index.htm']

urls_to_remove = ['https://www.ramakrishnavivekananda.info/index.htm',
                  'https://www.ramakrishnavivekananda.info/vivekananda/complete_works.htm',
                  'http://ramakrishnavivekananda.info/vivekananda/completeworksindex.xlsx',
                  'https://www.ramakrishnavivekananda.info/vivekananda/appendices',
                  'https://www.ramakrishnavivekananda.info/vivekananda/unpublished/unpublished_contents.htm']

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
    #print(soup)
    paragraphs = soup.find_all('p')
    main_body = []
    for paragraph in paragraphs:
        if 'nav' not in paragraph.get('class', []) and 'right' not in paragraph.get('class',
                                                                                    []) and 'center' not in paragraph.get(
                'class', []):
            main_body.append(paragraph.get_text(strip=True))

    # Join the extracted text into a single string
    main_text = ' '.join(main_body)
    return main_text


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


def clean_text(text):
    # Define regular expressions for different parts
    intro_pattern = r'^\s*(« Chronology »|« Addressee »|XIV)\n*'
    recipient_pattern = r'^\s*To [A-Za-z\s,.\-]+\n*'
    address_pattern = r'^\s*[A-Z0-9,.\s]+\n+'
    date_pattern = r'\d{1,2}[a-z]{2}\s+[A-Z][a-z]+\s*,\s*\d{4}'
    greeting_pattern = r'^\s*(DEAR [A-Z\s,.]+|TO [A-Z\s,.]+)\n+'
    closing_pattern = r'^\s*(Yours (affectionately|truly|sincerely),|Ever your aff\.\s*bro\.,|Yours in service,)\n+'
    signature_pattern = r'^\s*(VIVEKANANDA|SACHCHIDANANDA|Narendra\.)\n+'
    reference_pattern = r'\(\s*[A-Za-z\s,.\d]+\s*\)'
    number_pattern = r'\b\d+\b'

    # Apply regular expressions to remove unwanted parts
    text = re.sub(intro_pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(recipient_pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(address_pattern, '', text, flags=re.MULTILINE)
    text = re.sub(date_pattern, '', text, flags=re.MULTILINE)
    #text = re.sub(greeting_pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(closing_pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(signature_pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(reference_pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(number_pattern, '', text)

    # Remove bracketed information, which is typically non-essential
    text = re.sub(r'\[.*?\]', '', text)

    # Remove headers like "III. Religious Practice", "Brihadâranyaka Upanishad 3.8.1.-12."
    text = re.sub(r'^[IVXLCDM]+\.\s+.*\n', '', text, flags=re.MULTILINE)

    # Remove multiple newlines and trim the text
    text = re.sub(r'\n{2,}', '\n', text)
    text = text.strip()

    return text


def valid_sentence(sentence):
    # Function to validate if a sentence is meaningful
    # Discard if it is too short or doesn't contain alphabets
    return len(sentence) > 5 and re.search(r'[A-Za-z]', sentence)


def split_sentences(text):
    # Function to split text into sentences intelligently
    # This uses a regex to split on periods that are likely sentence enders
    sentence_endings = re.compile(r'(?<!\.\.\.)(?<!\.\s)(?<!\w\.\w.)(?<=\.|\?)\s')
    sentences = sentence_endings.split(text)
    return sentences


def main():
    print("Scrapper")
    url_list = []
    for url in base_urls:
        url_list = fetch_and_process_urls(url)

    collection = connect_to_mongodb()
    count = 0
    for link in url_list:
        if link in ['https://www.ramakrishnavivekananda.info/vivekananda/complete_works.htm',
                    'https://www.ramakrishnavivekananda.info/vivekananda/master_index.htm',
                    'https://www.ramakrishnavivekananda.info/vivekananda/volume_1/complete_works_v1_contents.htm',
                    'https://www.ramakrishnavivekananda.info/vivekananda/volume_2/volume_2_contents.htm',
                    'https://www.ramakrishnavivekananda.info/vivekananda/volume_3/volume_3_contents.htm',
                    'https://www.ramakrishnavivekananda.info/vivekananda/volume_4/volume_4_contents.htm',
                    'https://www.ramakrishnavivekananda.info/vivekananda/volume_5/volume_5_contents.htm',
                    'https://www.ramakrishnavivekananda.info/vivekananda/volume_6/volume_6_contents.htm',
                    'https://www.ramakrishnavivekananda.info/vivekananda/volume_7/volume_7_contents.htm',
                    'https://www.ramakrishnavivekananda.info/vivekananda/volume_8/volume_8_contents.htm',
                    'https://www.ramakrishnavivekananda.info/vivekananda/volume_9/volume_9_contents.htm'
                    ]:
            continue
        chapter = scrape_text(link)
        cleaned_text = clean_text(chapter)
        sentences = split_sentences(cleaned_text)
        sentences = [sentence.strip() for sentence in sentences if valid_sentence(sentence)]

        # Generate pairs of consecutive sentences concatenated with a period
        paired_texts = [sentences[i] + ". " + sentences[i + 1] for i in range(len(sentences) - 1)]
        count += len(paired_texts)
        for sentence in paired_texts:
            result = collection.update_one(
                {"url": link, "text": sentence},  # Criteria to match existing documents
                {"$setOnInsert": {"url": link, "text": sentence}},  # Fields to insert if no match is found
                upsert=True  # Perform an insert if no matching document is found
            )
            # print(f"Inserted document with id: {result.upserted_id}")
    print(f"Inserted {count} sentences into MongoDB")


if __name__ == "__main__":
    main()
