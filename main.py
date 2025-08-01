import os
import asyncio
import redis
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Load environment variables
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
    """Summarize text via Gemini chat."""
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

async def classify_query(query: str) -> bool:
    """Determine if a query is a valid web search."""
    prompt = f"Is this a valid web search query? Answer YES or NO.\nQuery: {query}"
    try:
        response = chat.send_message(prompt)
        return response.text.strip().upper().startswith("YES")
    except Exception:
        return False

async def search_vector_cache(query: str) -> str | None:
    """Search for semantically similar queries in the FAISS index."""
    vec = embedder.encode(query.lower())
    faiss.normalize_L2(vec.reshape(1, -1))
    if index.ntotal == 0:
        return None
    scores, ids = index.search(vec.reshape(1, -1), 1)
    if scores[0][0] >= SIM_THRESHOLD:
        orig_q = keys[ids[0][0]]
        cached = redis_client.get(orig_q)
        return cached.decode() if cached else None
    return None

async def store_cache(query: str, result: str) -> None:
    """Cache the result in Redis and update the FAISS index."""
    # Redis
    redis_client.set(query, result)
    # FAISS
    vec = embedder.encode(query.lower())
    faiss.normalize_L2(vec.reshape(1, -1))
    index.add(vec.reshape(1, -1))
    keys.append(query)
    faiss.write_index(index, VECTOR_INDEX_PATH)
    with open(VECTOR_INDEX_PATH + '.keys', 'wb') as f:
        np.save(f, np.array(keys, dtype=object))

async def fetch_search_results(query: str) -> str:
    """Scrape DuckDuckGo, extract snippets, and produce a combined summary."""
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(f"https://duckduckgo.com/html?q={query}", headers=headers, timeout=15)
    if resp.status_code != 200:
        return "Failed to fetch search results."

    soup = BeautifulSoup(resp.text, 'html.parser')
    anchors = soup.find_all('a', class_='result__a')[:5]
    urls = [a.get('href') for a in anchors if a.get('href')]
    if not urls:
        return "No results could be processed."

    briefs: list[str] = []
    for url in urls:
        # Normalize URL scheme
        if url.startswith("//"):
            url = "https:" + url
        # Extract uddg redirect parameter
        if "/l/?uddg=" in url:
            from urllib.parse import urlparse, parse_qs, unquote
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            url = unquote(qs.get('uddg', [url])[0])
        try:
            detail_resp = requests.get(url, headers=headers, timeout=15)
            if detail_resp.status_code != 200:
                continue
            ps = BeautifulSoup(detail_resp.text, 'html.parser').find_all('p')[:5]
            snippet = "\n".join(p.get_text(strip=True) for p in ps if p.get_text(strip=True))
            if snippet:
                briefs.append(snippet)
        except Exception:
            continue

    if not briefs:
        return "No content to summarize."

    combined_text = "\n\n".join(briefs)
    combined_summary = get_summary(combined_text)
    return combined_summary

async def main() -> None:
    raw = input("🔎 Enter your query: ").strip()
    query = raw.lower()

    if not await classify_query(query):
        print("❌ Invalid query.")
        return

    cached = await search_vector_cache(query)
    if cached:
        print("[✅ Cached Result]")
        print(cached)
        return

    print("🔄 Fetching live results...")
    result = await fetch_search_results(query)
    await store_cache(query, result)
    print("[✅ Fresh Result]")
    print(result)

if __name__ == '__main__':
    asyncio.run(main())
