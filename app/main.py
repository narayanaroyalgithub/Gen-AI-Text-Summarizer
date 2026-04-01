from fastapi import FastAPI, UploadFile, File, HTTPException
from .summarizer import generate_summary
from .utils import doc_to_text

app = FastAPI(title="Simple Summarizer")

@app.post("/summarize")
async def summarize(file: UploadFile = File(...)):
    content = await file.read()
    text = doc_to_text(content, file.filename)
    if not text:
        raise HTTPException(status_code=400, detail="Unable to parse file. Only plain text supported in this demo.")
    result = generate_summary(text)
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}
