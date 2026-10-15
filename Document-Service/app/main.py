from fastapi import FastAPI
from app.api.documents import router as documents_router
app=FastAPI(
     title="Research Intelligence Platform - Document Service",
    description="Upload and process research papers for downstream RAG and knowledge graph pipelines.",
    version="1.0.0",
)
app.include_router(documents_router)
@app.get("/health")


def check_health():
    return {
        "status": "healthy",
        "service": "document-ingestion-service",
    }
