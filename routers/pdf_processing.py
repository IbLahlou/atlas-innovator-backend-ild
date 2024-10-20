from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from routers.utils import ArabicLearningUtility
import uuid
import base64
from typing import Dict, Optional

router = APIRouter()

# Initialize the ArabicLearningUtility
arabic_learning_utility = ArabicLearningUtility()

# In-memory storage for vector stores (replace with a proper database in production)
vector_stores: Dict[str, object] = {}

class PDFRequest(BaseModel):
    file_content: str = Field(..., description="Base64 encoded PDF content")
    file_name: Optional[str] = Field(None, description="Original filename of the PDF")

class PDFResponse(BaseModel):
    vector_store_id: str = Field(..., description="Unique identifier for the processed vector store")

class VectorStoreInfo(BaseModel):
    id: str = Field(..., description="Unique identifier of the vector store")
    file_name: Optional[str] = Field(None, description="Original filename of the processed PDF")
    status: str = Field(..., description="Status of the vector store")

@router.post("/process", response_model=PDFResponse, summary="Process a PDF file")
async def process_pdf(pdf_request: PDFRequest):
    """
    Process a PDF file and create a vector store for future querying.

    Parameters:
    - file_content: Base64 encoded content of the PDF file to be processed
    - file_name: Optional original filename of the PDF

    Returns:
    - A JSON object containing a unique identifier for the created vector store

    Raises:
    - HTTPException 400: If there's an error processing the PDF file
    - HTTPException 500: If there's an internal server error during processing
    """
    try:
        file_content = base64.b64decode(pdf_request.file_content)
        vector_store = await arabic_learning_utility.process_pdf(file_content)
        vector_store_id = str(uuid.uuid4())
        vector_stores[vector_store_id] = {
            "store": vector_store,
            "file_name": pdf_request.file_name,
            "status": "available"
        }
        return PDFResponse(vector_store_id=vector_store_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

@router.get("/vector_store/{vector_store_id}", response_model=VectorStoreInfo, summary="Retrieve vector store information")
async def get_vector_store(vector_store_id: str):
    """
    Retrieve information about a vector store by its ID.

    Parameters:
    - vector_store_id: The unique identifier of the vector store to retrieve

    Returns:
    - A JSON object containing information about the vector store

    Raises:
    - HTTPException 404: If the vector store is not found
    """
    vector_store = vector_stores.get(vector_store_id)
    if not vector_store:
        raise HTTPException(status_code=404, detail="Vector store not found")
    return VectorStoreInfo(
        id=vector_store_id,
        file_name=vector_store["file_name"],
        status=vector_store["status"]
    )

@router.delete("/vector_store/{vector_store_id}", summary="Delete a vector store")
async def delete_vector_store(vector_store_id: str):
    """
    Delete a vector store by its ID.

    Parameters:
    - vector_store_id: The unique identifier of the vector store to delete

    Returns:
    - A JSON object confirming the deletion

    Raises:
    - HTTPException 404: If the vector store is not found
    """
    if vector_store_id not in vector_stores:
        raise HTTPException(status_code=404, detail="Vector store not found")
    del vector_stores[vector_store_id]
    return JSONResponse(content={"message": f"Vector store {vector_store_id} has been deleted"})

@router.get("/vector_stores", response_model=Dict[str, VectorStoreInfo], summary="List all vector stores")
async def list_vector_stores():
    """
    List all available vector stores.

    Returns:
    - A JSON object containing information about all vector stores
    """
    return {
        id: VectorStoreInfo(id=id, file_name=info["file_name"], status=info["status"])
        for id, info in vector_stores.items()
    }

@router.get("/health", summary="Check the health of the PDF processing service")
async def health_check():
    """
    Perform a health check on the PDF processing service.
    
    Returns:
    - A JSON object indicating the status of the service
    """
    return {"status": "healthy", "vector_stores_count": len(vector_stores)}