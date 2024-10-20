from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from routers.utils import ArabicLearningUtility
from typing import Dict, Optional

router = APIRouter()

# Initialize the ArabicLearningUtility
arabic_learning_utility = ArabicLearningUtility()

# Assume this is connected to an external storage system or the one from PDF processing
vector_stores: Dict[str, object] = {}

class QuestionRequest(BaseModel):
    question: str = Field(..., description="Question to be answered based on the processed content")
    vector_store_id: str = Field(..., description="Identifier of the vector store to use for answering the question")
    language: Optional[str] = Field("ar", description="Language of the question and expected answer (default: Arabic)")

class QuestionResponse(BaseModel):
    answer: str = Field(..., description="Answer to the provided question")
    confidence: float = Field(..., description="Confidence score of the answer", ge=0, le=1)

@router.post("/answer", response_model=QuestionResponse, summary="Answer a question based on processed content")
async def answer_question(question_request: QuestionRequest):
    """
    Answer a question based on pre-processed content stored in a vector store.

    Parameters:
    - question: The question to be answered
    - vector_store_id: The identifier of the vector store to use for answering the question
    - language: The language of the question and expected answer (default: Arabic)

    Returns:
    - A JSON object containing the answer to the provided question and a confidence score

    Raises:
    - HTTPException 404: If the specified vector store is not found
    - HTTPException 500: If there's an error in answering the question
    """
    vector_store = vector_stores.get(question_request.vector_store_id)
    if not vector_store:
        raise HTTPException(status_code=404, detail="Vector store not found")
    
    try:
        answer, confidence = await arabic_learning_utility.answer_question(
            vector_store,
            question_request.question,
            language=question_request.language
        )
        return QuestionResponse(answer=answer, confidence=confidence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")

@router.get("/vector_store/{vector_store_id}/info", summary="Get information about a vector store")
async def get_vector_store_info(vector_store_id: str):
    """
    Retrieve information about a specific vector store.

    Parameters:
    - vector_store_id: The identifier of the vector store

    Returns:
    - A JSON object containing information about the vector store

    Raises:
    - HTTPException 404: If the specified vector store is not found
    """
    vector_store = vector_stores.get(vector_store_id)
    if not vector_store:
        raise HTTPException(status_code=404, detail="Vector store not found")
    
    return {
        "id": vector_store_id,
        "document_count": len(vector_store.get("documents", [])),
        "language": vector_store.get("language", "Unknown")
    }

@router.get("/health", summary="Check the health of the question answering service")
async def health_check():
    """
    Perform a health check on the question answering service.
    
    Returns:
    - A JSON object indicating the status of the service and the number of available vector stores
    """
    return {
        "status": "healthy",
        "vector_stores_count": len(vector_stores),
        "utility_status": arabic_learning_utility.get_status()
    }

@router.get("/supported_languages", summary="Get supported languages for question answering")
async def get_supported_languages():
    """
    Retrieve a list of supported languages for question answering.

    Returns:
    - A JSON object containing a list of supported language codes and their names
    """
    supported_languages = {
        "ar": "Arabic",
        "en": "English",
        # Add more supported languages as needed
    }
    return {"supported_languages": supported_languages}