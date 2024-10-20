from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
import torch
import numpy as np
import io
import soundfile as sf
import librosa
from pydantic import BaseModel
import os
import base64

router = APIRouter()

# Whisper model setup
device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = os.getenv("WHISPER_MODEL_ID", "openai/whisper-large-v3-turbo")

print(f"Loading Whisper model on {device}...")
model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id).to(device)
processor = AutoProcessor.from_pretrained(model_id)

class TranscriptionRequest(BaseModel):
    audio: str

class TranscriptionResponse(BaseModel):
    transcription: str

@router.post("/transcribe/", 
             response_model=TranscriptionResponse,
             summary="Transcribe an audio file",
             response_description="Transcription of the provided audio")
async def transcribe_audio(request: TranscriptionRequest):
    """
    Transcribe a base64-encoded audio using the Whisper-large-v3-turbo model.

    Parameters:
    - request: A JSON object containing the base64-encoded audio data.

    Returns:
    - A JSON object containing the transcription of the audio.

    Raises:
    - HTTPException 400: If there's an error processing the audio data.
    - HTTPException 500: If there's an internal server error during transcription.
    """
    try:
        # Decode the base64 audio data
        audio_data = base64.b64decode(request.audio)
        
        # Read the audio data and convert it to the correct format
        audio, sample_rate = sf.read(io.BytesIO(audio_data))
        
        # Ensure audio is mono
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
        
        # Resample to 16kHz if necessary
        if sample_rate != 16000:
            print(f"Resampling from {sample_rate}Hz to 16000Hz")
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)
        
        # Preprocess audio to match Whisper's requirements
        input_features = processor.feature_extractor(audio, sampling_rate=16000, return_tensors="pt").input_features.to(device)
        
        # Perform inference
        with torch.no_grad():
            generated_ids = model.generate(input_features=input_features)
        
        # Decode and return the transcription
        transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)
        return TranscriptionResponse(transcription=transcription[0])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during transcription: {str(e)}")

@router.get("/model-info", summary="Get information about the current Whisper model")
async def get_model_info():
    """
    Retrieve information about the currently loaded Whisper model.

    Returns:
    - A JSON object containing the model ID and the device it's running on.
    """
    return {"model_id": model_id, "device": device}