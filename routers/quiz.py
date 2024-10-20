from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from routers.utils import IBMWatsonXAIWrapper
from typing import List, Optional
import os

router = APIRouter()

# Initialize the AI wrapper
watson_wrapper = IBMWatsonXAIWrapper(
    api_key=os.getenv('IBM_WATSONX_API_KEY'),
    project_id=os.getenv('IBM_WATSONX_PROJECT_ID'),
    url=os.getenv('IBM_WATSONX_URL')
)

class QuizQuestion(BaseModel):
    question: str = Field(..., description="The quiz question in Arabic")
    options: List[str] = Field(..., description="List of answer options in Arabic", min_items=2, max_items=4)
    correct_answer: int = Field(..., description="Index of the correct answer (0-based)", ge=0, lt=4)
    explanation: Optional[str] = Field(None, description="Explanation of the correct answer in Arabic")

class GenerateQuizRequest(BaseModel):
    quiz_type: str = Field(..., description="Type of quiz to generate (e.g., vocabulary, grammar, culture)")
    difficulty: str = Field("medium", description="Difficulty level of the quiz")
    num_questions: int = Field(5, description="Number of questions to generate", ge=1, le=10)

class GenerateQuizResponse(BaseModel):
    questions: List[QuizQuestion] = Field(..., description="List of generated quiz questions")

@router.post("/generate", response_model=GenerateQuizResponse)
async def generate_quiz_endpoint(request: GenerateQuizRequest):
    """
    Generate an Arabic language quiz based on the specified parameters.

    Parameters:
    - quiz_type: Type of quiz to generate (e.g., vocabulary, grammar, culture)
    - difficulty: Difficulty level of the quiz (default: medium)
    - num_questions: Number of questions to generate (default: 5, max: 10)

    Returns:
    - A JSON object containing a list of generated quiz questions

    Raises:
    - HTTPException 500: If there's an error in generating the quiz
    """
    try:
        prompt = f"""Create an Arabic language quiz with the following parameters:
        Type: {request.quiz_type}
        Difficulty: {request.difficulty}
        Number of questions: {request.num_questions}

        For each question, provide:
        1. The question in Arabic
        2. 3 or 4 answer options in Arabic
        3. The index of the correct answer (0-based)
        4. A brief explanation of the correct answer in Arabic

        Format the response as a JSON array of objects, each containing 'question', 'options', 'correct_answer', and 'explanation' fields.
        """
        
        response = watson_wrapper.generate_text(prompt)
        
        # Parse the response and convert it to QuizQuestion objects
        # Note: In a real-world scenario, you'd want to add more robust parsing and error handling here
        import json
        questions_data = json.loads(response)
        questions = [QuizQuestion(**q) for q in questions_data]
        
        return GenerateQuizResponse(questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating quiz: {str(e)}")

@router.get("/quiz_types", summary="Get available quiz types")
async def get_quiz_types():
    """
    Retrieve a list of available quiz types.

    Returns:
    - A JSON object containing a list of available quiz types and their descriptions
    """
    quiz_types = {
        "vocabulary": "Tests knowledge of Arabic vocabulary",
        "grammar": "Focuses on Arabic grammar rules and usage",
        "culture": "Questions about Arab culture and traditions",
        "listening": "Audio-based questions to test listening comprehension",
        "reading": "Tests reading comprehension with short passages"
    }
    return {"quiz_types": quiz_types}

@router.get("/difficulty_levels", summary="Get available difficulty levels")
async def get_difficulty_levels():
    """
    Retrieve a list of available difficulty levels for quizzes.

    Returns:
    - A JSON object containing a list of available difficulty levels
    """
    difficulty_levels = ["beginner", "medium", "advanced", "expert"]
    return {"difficulty_levels": difficulty_levels}

@router.get("/health", summary="Check the health of the quiz generation service")
async def health_check():
    """
    Perform a health check on the quiz generation service.
    
    Returns:
    - A JSON object indicating the status of the service
    """
    return {
        "status": "healthy",
        "ai_wrapper": watson_wrapper.__class__.__name__,
        "ai_wrapper_status": watson_wrapper.get_status()  # Assuming there's a get_status method
    }