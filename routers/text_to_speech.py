from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .utils import ArabicLearningUtility
import base64
from typing import Optional
import time

router = APIRouter()


total_requests=0
total_characters_processed=0
sum_duration=0
average_request_time=0


# Initialize the ArabicLearningUtility
arabic_learning_utility = ArabicLearningUtility()

class TextToSpeechRequest(BaseModel):
    text: str = Field(..., description="Arabic text to be converted to speech")

class TextToSpeechResponse(BaseModel):
    audio_content: str = Field(..., description="Base64 encoded audio content")

@router.post("/convert", response_model=TextToSpeechResponse)
async def text_to_speech(request: TextToSpeechRequest):
    """
    Convert Arabic text to speech.

    Parameters:
    - text: The Arabic text to be converted to speech

    Returns:
    - A JSON object containing the Base64 encoded audio content

    Raises:
    - HTTPException 400: If there's an error in the input text
    - HTTPException 500: If there's an error in the text-to-speech conversion
    """
    total_requests = total_requests + 1
    
    total_characters_processed= total_characters_processed + len(request.text)
    
    
    
    
    
    
    
    try:
        start_time = time.time()
        audio_base64 = await arabic_learning_utility.text_to_speech(request.text)
        end_time = time.time()
        duration = end_time - start_time
        sum_duration = duration + sum_duration
        average_request_time = sum_duration/total_requests
        
        return TextToSpeechResponse(audio_content=audio_base64)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in text-to-speech conversion: {str(e)}")

@router.get("/health", summary="Check the health of the text-to-speech service")
async def health_check():
    """
    Perform a health check on the text-to-speech service.
    
    Returns:
    - A JSON object indicating the status of the service
    """
    return {
        "status": "healthy",
        "utility_status": "operational"  # Assuming the utility is always operational
    }

@router.get("/usage", summary="Get usage statistics")
async def get_usage_statistics():
    """
    Retrieve usage statistics for the text-to-speech service.

    Returns:
    - A JSON object containing usage statistics
    """
    return {
        "total_requests": total_requests,
        "total_characters_processed": total_characters_processed,
        "average_request_time": average_request_time  
    }