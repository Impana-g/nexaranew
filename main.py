from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analyze, kb, sentiment

app = FastAPI(
    title="Nexara Investment Intelligence API",
    description="AI-powered investment query analysis with NLP pipeline, background checks, and live KB via Tavily",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api/v1", tags=["Analyze"])
app.include_router(kb.router, prefix="/api/v1", tags=["Knowledge Base"])
app.include_router(sentiment.router, prefix="/api/v1", tags=["Sentiment"])

@app.get("/")
def root():
    return {"service": "Nexara Investment Intelligence", "status": "running"}