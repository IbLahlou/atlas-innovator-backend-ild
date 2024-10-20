from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import transcription, image_gen, language_gen, pdf_processing, question_answering, quiz, text_to_speech
from dotenv import load_dotenv
import os


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Arabic Learning API",
    description="A comprehensive API for Arabic language learning and processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(transcription.router, prefix="/audio", tags=["Audio Transcription"])
app.include_router(image_gen.router, prefix="/image", tags=["Image Generation"])
app.include_router(language_gen.router, prefix="/language", tags=["Language Generation"])
app.include_router(pdf_processing.router, prefix="/pdf", tags=["PDF Processing"])
app.include_router(question_answering.router, prefix="/qa", tags=["Question Answering"])
app.include_router(quiz.router, prefix="/quiz", tags=["Quiz Generation"])
app.include_router(text_to_speech.router, prefix="/tts", tags=["Text-to-Speech"])

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that provides a welcome message and basic API information.
    """
    return {
        "message": "Welcome to the Arabic Learning API",
        "version": app.version,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to verify if the API is running properly.
    """
    return {"status": "healthy", "api_version": app.version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )