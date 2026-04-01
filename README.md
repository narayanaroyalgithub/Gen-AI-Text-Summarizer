Simple Summarization Service
----------------------------

Overview:
- Upload a text file to /summarize
- Service chunks text, builds embeddings, selects top chunks, calls LLM for summary, caches result.

Setup:
1. Create a .env with OPENAI_API_KEY and REDIS_URL if using Redis.
2. python -m venv venv && source venv/bin/activate
3. pip install -r requirements.txt
4. uvicorn app.main:app --reload

Notes:
- This is a minimal demo. Add PDF parsing, better chunking, retries and error handling for production.
- Replace OpenAI call if you use a different LLM provider.
