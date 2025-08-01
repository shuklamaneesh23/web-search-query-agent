# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import answer_query

app = FastAPI()

# ✅ Add CORS middleware before defining routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str

@app.post("/query")
async def query_api(q: Query):
    try:
        resp = answer_query(q.text)
        return {"answer": resp}
    except Exception as e:
        raise HTTPException(500, str(e))
