# backend/agent.py
import os
import redis
import requests
import google.generativeai as genai
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs, unquote

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
VECTOR_INDEX_PATH = "vector.index"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
SIM_THRESHOLD = 0.75

# Setup Redis
redis_client = redis.Redis.from_url(REDIS_URL)

# Setup Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")
chat = model.start_chat()

# Summarizer helper
def get_summary(text: str) -> str:
    try:
        response = chat.send_message(f"Summarize the following content: {text}")
        return response.text.strip()
    except Exception as e:
        print(f"Summarization error: {e}")
        return ""

# Setup Embedding model and FAISS index
embedder = SentenceTransformer(EMBEDDING_MODEL)
if os.path.exists(VECTOR_INDEX_PATH):
    index = faiss.read_index(VECTOR_INDEX_PATH)
    with open(VECTOR_INDEX_PATH + '.keys', 'rb') as f:
        keys = np.load(f, allow_pickle=True).tolist()
else:
    dim = embedder.get_sentence_embedding_dimension()
    index = faiss.IndexFlatIP(dim)
    keys = []

def classify_query(query: str) -> bool:
    prompt = f"Is this a valid web search query? Answer YES or NO.\nQuery: {query}"
    try:
        response = chat.send_message(prompt)
        return response.text.strip().upper().startswith("YES")
    except Exception:
        return False

def search_vector_cache(query: str):
    vec = embedder.encode(query.lower())
    faiss.normalize_L2(vec.reshape(1, -1))
    if index.ntotal == 0:
        return None
    D, I = index.search(vec.reshape(1, -1), 1)
    if D[0][0] >= SIM_THRESHOLD:
        orig_q = keys[I[0][0]]
        return redis_client.get(orig_q).decode()
    return None

def store_cache(query: str, result: str):
    redis_client.set(query, result)
    vec = embedder.encode(query.lower())
    faiss.normalize_L2(vec.reshape(1, -1))
    index.add(vec.reshape(1, -1))
    keys.append(query)
    faiss.write_index(index, VECTOR_INDEX_PATH)
    with open(VECTOR_INDEX_PATH + '.keys', 'wb') as f:
        np.save(f, np.array(keys, dtype=object))

def fetch_search_results(query: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(f"https://duckduckgo.com/html?q={query}", headers=headers, timeout=15)
    if resp.status_code != 200:
        return "Failed to fetch search results."
    soup = BeautifulSoup(resp.text, 'html.parser')
    anchors = soup.find_all('a', class_='result__a')[:5]
    urls = [a.get('href') for a in anchors if a.get('href')]
    if not urls:
        return "No results could be processed."

    collected_text = []
    for url in urls:
        if url.startswith("//"):
            url = "https:" + url
        if "/l/?uddg=" in url:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            url = unquote(qs.get('uddg', [url])[0])

        try:
            dr = requests.get(url, headers=headers, timeout=15)
            if dr.status_code != 200:
                continue
            ps = BeautifulSoup(dr.text, 'html.parser').find_all('p')[:5]
            brief = "\n".join([p.get_text(strip=True) for p in ps])
            if brief:
                collected_text.append(brief)
        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue

    combined = "\n".join(collected_text)
    return get_summary(combined) if combined else "No content to summarize."

def answer_query(raw_query: str) -> str:
    query = raw_query.lower().strip()
    if not classify_query(query):
        return "❌ Invalid query."
    cached = search_vector_cache(query)
    if cached:
        return cached
    result = fetch_search_results(query)
    store_cache(query, result)
    return result
