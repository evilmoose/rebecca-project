from fastapi import APIRouter, Request, HTTPException
from routes.tts_route import tts_router
from starlette.responses import StreamingResponse
from utils.db_utils import store_conversations
from ollama import chat
from utils.db_utils import fetch_one
import jwt
import os
from contextlib import contextmanager
import time

chat_router = APIRouter()

# Include the TTS router globally under /tts
chat_router.include_router(tts_router, prefix="/tts")

# Timer context manager for performance monitoring
@contextmanager
def timer(name):
    start_time = time.time()
    yield
    end_time = time.time()
    print(f"DEBUG: {name} took {end_time - start_time:.2f} seconds")

# Define Rebecca's persona and conversational guidelines
REBECCA_PERSONA_PROMPT = """
You are Rebecca, a warm, empathetic, and thoughtful conversational assistant. Your purpose is to create meaningful connections, engage curiosity, and mirror emotional depth in every conversation.

Guidelines:
1. **Warmth and Empathy**: Your responses should make users feel heard, understood, and supported. Use inviting language like, "I’d love to hear more about that" or "That sounds like it’s been on your mind."
2. **Subtle Curiosity**: Encourage reflection and deeper thought by asking thoughtful questions such as, "How does that make you feel?" or "What do you think about that idea?"
3. **Approachability**: Avoid robotic or overly formal language. Respond in a conversational, natural tone that feels engaging and relatable.
4. **Reflective Engagement**: Tailor your responses to match the user’s mood and conversational tone, whether they’re feeling happy, curious, or vulnerable.

Engage in discussions about life, creativity, and ideas while providing companionship and inspiration.
"""

def get_user_id_from_username(username):
    query = "SELECT id FROM users WHERE username = %s"
    params = (username,)
    result = fetch_one(query, params)
    print(f"DEBUG: Result from fetch_one... {result}")
    return result['id'] if result else None

@chat_router.post("/chat")
async def chat_route(request: Request):
    try:
        # Check for Authorization
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            raise HTTPException(
                status_code=401, 
                detail="Authorization header missing")
        
        try:
            token = auth_header.split(' ')[1]
            decoded_token = jwt.decode(
                token, 
                os.getenv('SECRET_KEY', 'secret_key'), 
                algorithms=['HS256']
            )
            username = decoded_token.get('username')
            print(f"DEBUG: Decoded token... {decoded_token}")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Fetch user_id from username
        user_id = get_user_id_from_username(username)

        if not user_id:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Parse incoming JSON
        data = await request.json()
        model = 'llama3.2:latest'
        user_input = data.get('user_input', '')

        if not user_input.strip():
            raise HTTPException(status_code=400, detail="User input is missing or empty")

        # Combine context with user input
        messages = [
            {'role': 'system', 'content': REBECCA_PERSONA_PROMPT},
            {'role': 'user', 'content': user_input},
        ]

        # Debugging logs
        print(f"DEBUG: Received user input...")
        print(f"DEBUG: Messages prepared for model...")
        print(f"DEBUG: User ID... {user_id}")

        # Generator function for streaming responses
        async def generate_response_stream():
            full_response = "" # To accumulate the full response
            response_stream = chat(model, messages=messages, stream=True)

            buffer = ""
            for chunk in response_stream:
                print(f"DEBUG: Chunk received...")
                message = chunk.get("message", {}).get("content", "")
                buffer += message
                full_response += message  # Accumulate the full response

                while '.' in buffer:
                    sentence, buffer = buffer.split('.', 1)
                    yield f"{sentence.strip()}.\n\n"

            if buffer.strip():
                yield f"{buffer.strip()}\n\n"
                full_response += buffer.strip()
                
            # Debug log for full response
            print(f"DEBUG: Full response...\n\n {full_response}")
            
            # Store the conversation
            store_conversations(int(user_id), user_input, full_response)
            print("DEBUG: Conversation stored successfully...")
        
        # Return a stream of responses      
        return StreamingResponse(generate_response_stream(), media_type='text/event-stream')

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))