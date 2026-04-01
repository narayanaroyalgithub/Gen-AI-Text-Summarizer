import os
import openai
from .config import OPENAI_API_KEY, TOP_K
from .embeddings import EmbeddingIndex
from .utils import make_cache_key
import redis
import json
import time

openai.api_key = OPENAI_API_KEY

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

# simple chunker
def chunk_text(text, max_chars=1000, overlap=200):
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        end = min(i + max_chars, n)
        chunk = text[i:end]
        chunks.append(chunk)
        i = max(end - overlap, end)
        if i == end:
            i += 1
    return chunks

def build_index_for_text(text):
    chunks = chunk_text(text)
    emb_index = EmbeddingIndex()
    emb_index.build(chunks)
    return emb_index, chunks

def make_prompt(chunks):
    # combine top chunks into prompt
    combined = "\n\n---\n\n".join(chunks)
    prompt = (
        "You are a concise assistant. Summarize the following text into 3 short bullet points "
        "focusing on diagnosis/issue, treatment/plan, and next steps. Do not give medical advice.\n\n"
        f"Text:\n{combined}\n\nSummary:"
    )
    return prompt

def call_llm(prompt, model="gpt-4o-mini", max_tokens=256, temperature=0.2):
    # Example using OpenAI API; adapt for other LLM providers
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{"role":"user","content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    text = resp["choices"][0]["message"]["content"].strip()
    return text

def generate_summary(text):
    key = make_cache_key(text)
    cached = r.get(key)
    if cached:
        return json.loads(cached)

    # build index & query for top K chunks relevant to general summary
    index, chunks = build_index_for_text(text)

    # for generic summary, use the whole text as query (or first N chars)
    query_text = text[:500]
    results = index.query(query_text, top_k=TOP_K)
    selected_chunks = [t for t, _ in results]

    prompt = make_prompt(selected_chunks)
    start = time.time()
    summary = call_llm(prompt)
    latency = time.time() - start

    result = {"summary": summary, "selected_chunks": selected_chunks, "latency": latency}
    r.set(key, json.dumps(result), ex=int(os.getenv("CACHE_TTL", 3600)))
    return result
