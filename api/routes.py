from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from vector_store.index_documents import index_pdf_chunks
from vector_store.query_documents import search_similar_chunks
import os

router = APIRouter()

class QueryRequest(BaseModel):
    prompt: str
    top_k: int = 3

@router.post("/query")
def query_handler(body: QueryRequest):
    try:
        results = search_similar_chunks(body.prompt, top_k=body.top_k)

        if "error" in results:
            raise HTTPException(status_code=404, detail=results["error"])

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/index")
def index_handler(file: UploadFile = File(...), doc_id: str = Form(...)):
    try:
        # Save uploaded file to output/ directory
        os.makedirs("output", exist_ok=True)
        file_path = f"output/{doc_id}_chunked.txt"

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        index_pdf_chunks(file_path, doc_id)
        return {"message": "Indexed successfully", "doc_id": doc_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
