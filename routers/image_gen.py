from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from gradio_client import Client
import os
import shutil
import uuid
from typing import Optional

router = APIRouter()

# Initialize the Gradio client
GRADIO_API_URL = os.getenv("GRADIO_API_URL", "black-forest-labs/FLUX.1-schnell")
gradio_client = Client(GRADIO_API_URL)

class GenerateImageRequest(BaseModel):
    story: str = Field(..., description="The story for which to generate an image")
    seed: Optional[int] = Field(None, description="Seed for random number generation (optional)")
    width: int = Field(1024, description="Width of the generated image")
    height: int = Field(1024, description="Height of the generated image")
    num_inference_steps: int = Field(4, description="Number of inference steps")

class GenerateImageResponse(BaseModel):
    image_path: str = Field(..., description="Path to the generated image")

@router.post("/generate", response_model=GenerateImageResponse)
async def generate_image_endpoint(request: GenerateImageRequest):
    """
    Generate an image based on a given story using the FLUX.1-schnell model.

    Parameters:
    - story: The story to base the image on
    - seed: Optional seed for random number generation
    - width: Width of the generated image (default: 1024)
    - height: Height of the generated image (default: 1024)
    - num_inference_steps: Number of inference steps (default: 4)

    Returns:
    - A JSON object containing the path to the generated image

    Raises:
    - HTTPException 500: If there's an error in generating the image
    """
    try:
        image_prompt = f"Create a visual description for this story: {request.story}"
        result = gradio_client.predict(
            prompt=image_prompt,
            seed=request.seed if request.seed is not None else 0,
            randomize_seed=request.seed is None,
            width=request.width,
            height=request.height,
            num_inference_steps=request.num_inference_steps,
            api_name="/infer",
        )
        image_path = result[0] if isinstance(result, tuple) else result
        
        # Generate a unique filename
        unique_filename = f"{uuid.uuid4()}.png"
        output_dir = os.getenv("IMAGE_OUTPUT_DIR", "images")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, unique_filename)
        
        # Move the generated image to the output directory
        shutil.move(image_path, output_path)
        
        return GenerateImageResponse(image_path=output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating image: {str(e)}")

@router.get("/model-info", response_model=dict)
async def get_model_info():
    """
    Retrieve information about the currently used image generation model.

    Returns:
    - A JSON object containing the Gradio API URL being used
    """
    return {"gradio_api_url": GRADIO_API_URL}