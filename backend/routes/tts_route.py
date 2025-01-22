from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from starlette.responses import StreamingResponse
from contextlib import closing
import json

tts_router = APIRouter()

# Function to generate WAV header
def generate_wav_header(pcm_data_size, sample_rate, channels=1, bits_per_sample=16):
    """Generate a WAV header for raw PCM data."""
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    header = (
        b"RIFF" +
        (pcm_data_size + 36).to_bytes(4, 'little') +  # File size (36 + PCM data size)
        b"WAVE" +
        b"fmt " +
        (16).to_bytes(4, 'little') +  # Subchunk size (16 for PCM)
        (1).to_bytes(2, 'little') +  # Audio format (1 for PCM)
        (channels).to_bytes(2, 'little') +
        (sample_rate).to_bytes(4, 'little') +
        (byte_rate).to_bytes(4, 'little') +
        (block_align).to_bytes(2, 'little') +
        (bits_per_sample).to_bytes(2, 'little') +
        b"data" +
        pcm_data_size.to_bytes(4, 'little')
    )
    return header

@tts_router.post("/text-to-speech")
async def text_to_speech(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Text input is required")

    try:
        # Initialize the Polly client
        polly_client = boto3.client("polly", region_name="us-east-1")
        
        # Request speech synthesis in PCM format
        audio_response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat="pcm",  # Raw PCM format
            VoiceId="Joanna",
            SampleRate="16000"  # High-quality audio
        )
        
        # Stream the audio response
        if "AudioStream" in audio_response:
            def wav_audio_stream():
                with closing(audio_response["AudioStream"]) as audio_stream:
                    # Read the PCM data
                    pcm_data = audio_stream.read()
                    # Generate WAV header
                    wav_header = generate_wav_header(len(pcm_data), sample_rate=16000)
                    # Yield WAV header followed by PCM data
                    yield wav_header + pcm_data

            # Return a combined response
            return StreamingResponse(
                wav_audio_stream(),
                media_type="audio/wav"
            )
        
        else:
            raise HTTPException(status_code=500, detail="Audio stream not found")
    except (BotoCoreError, ClientError) as error:
        print(f"Polly error: {error}")
        raise HTTPException(status_code=500, detail="Error with AWS Polly TTS service")
    
@tts_router.post("/get-visemes")
async def get_visemes(request: Request):
    data = await request.json()
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Text input is required")
    
    try:
        polly_client = boto3.client("polly", region_name="us-east-1")
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat="json",
            VoiceId="Joanna",
            SpeechMarkTypes=["viseme"]
        )

        if "AudioStream" in response:
            viseme_data = response["AudioStream"].read().decode("utf-8")
            # Convert newline-separated JSON objects into a list
            viseme_list = [json.loads(line) for line in viseme_data.strip().split("\n")]
            print(viseme_list)
            return JSONResponse(content={"visemes":viseme_list})
        else:
            raise HTTPException(status_code=500, detail="Audio stream not found")
    except (BotoCoreError, ClientError) as error:
        raise HTTPException(status_code=500, detail=str(error))