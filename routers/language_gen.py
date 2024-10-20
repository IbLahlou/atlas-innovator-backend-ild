from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from langchain import PromptTemplate
from typing import List
import os

router = APIRouter()
from .utils import IBMWatsonXAIWrapper
watson_wrapper = IBMWatsonXAIWrapper(
    api_key=os.getenv('IBM_WATSONX_API_KEY'),
    project_id=os.getenv('IBM_WATSONX_PROJECT_ID'),
    url=os.getenv('IBM_WATSONX_URL')
)

class VocabularyResponse(BaseModel):
    words: List[dict] = []

class SentenceResponse(BaseModel):
    sentence: str
    explanation: str

class StoryResponse(BaseModel):
    story: str
    explanation: str

class CulturalFactResponse(BaseModel):
    fact: str

@router.post("/vocabulary", response_model=VocabularyResponse)
async def generate_vocabulary_endpoint(category: str = Query(..., description="Category for vocabulary generation")):
    """
    Generate Arabic vocabulary words related to a specific category.

    Parameters:
    - category: The category for which to generate vocabulary

    Returns:
    - A JSON object containing a list of Arabic words with explanations

    Raises:
    - HTTPException 500: If there's an error in generating vocabulary
    """
    try:
        prompt = PromptTemplate(
            input_variables=["category"],
            template="Create 5 Arabic words related to {category} with a simple explanation for each word in Arabic."
        ).format(category=category)
        response = watson_wrapper.generate_text(prompt)
        
        # Parse the response and convert it to the required format
        words = [{'word': word.strip(), 'explanation': explanation.strip()} 
                 for word, explanation in (line.split(':', 1) for line in response.split('\n') if ':' in line)]
        
        return VocabularyResponse(words=words)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating vocabulary: {str(e)}")

@router.post("/sentence", response_model=SentenceResponse)
async def generate_sentence_endpoint():
    """
    Generate a simple Arabic sentence suitable for beginners.

    Returns:
    - A JSON object containing the generated sentence and its explanation

    Raises:
    - HTTPException 500: If there's an error in generating the sentence
    """
    try:
        prompt = "Create a simple Arabic sentence suitable for beginners with an explanation of its meaning."
        response = watson_wrapper.generate_text(prompt)
        
        # Parse the response
        sentence, explanation = response.split('\n', 1)
        return SentenceResponse(sentence=sentence.strip(), explanation=explanation.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating sentence: {str(e)}")

@router.post("/story", response_model=StoryResponse)
async def generate_story_endpoint():
    """
    Generate a very short story in Arabic for children.

    Returns:
    - A JSON object containing the generated story and its explanation

    Raises:
    - HTTPException 500: If there's an error in generating the story
    """
    try:
        prompt = "Tell a very short story (3-4 sentences) in Arabic for children, then explain its meaning simply."
        response = watson_wrapper.generate_text(prompt)
        
        # Parse the response
        story, explanation = response.split('\n\n', 1)
        return StoryResponse(story=story.strip(), explanation=explanation.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating story: {str(e)}")

@router.post("/cultural-fact", response_model=CulturalFactResponse)
async def generate_cultural_fact_endpoint():
    """
    Generate an interesting fact about Arabic culture or an Arabic-speaking country.

    Returns:
    - A JSON object containing the generated cultural fact

    Raises:
    - HTTPException 500: If there's an error in generating the cultural fact
    """
    try:
        prompt = "Share an interesting fact about Arabic culture or an Arabic-speaking country."
        response = watson_wrapper.generate_text(prompt)
        return CulturalFactResponse(fact=response.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating cultural fact: {str(e)}")

@router.get("/model-info", response_model=dict)
async def get_model_info():
    """
    Retrieve information about the currently used language model.

    Returns:
    - A JSON object containing information about the IBM Watson X AI model being used
    """
    return {"model": "IBM Watson X AI", "wrapper": watson_wrapper.__class__.__name__}