from fastapi import APIRouter, Request, HTTPException
from routes.tts_route import tts_router
from starlette.responses import StreamingResponse
from utils.db_utils import store_conversations, get_user_id_from_username, find_similar_conversations
from utils.redis_utils import RedisClient
from services.scoring import calculate_scores
from difflib import SequenceMatcher
from ollama import chat, embeddings
import jwt
import os

chat_router = APIRouter()

# Include the TTS router globally under /tts
chat_router.include_router(tts_router, prefix="/tts")

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
# Initialize Redis client
redis_client = RedisClient()

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
        try:
            data = await request.json()
            if not isinstance(data, dict):
                raise ValueError("Parsed JSON is not a dictionary")
            print(f"DEBUG: Parsed JSON data... {data}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

        model = 'llama3.2:latest'
        user_input = data.get('user_input', '').strip()

        # Ensure user_input is a valid string
        if not isinstance(user_input, str) or not user_input:
            raise HTTPException(status_code=400, detail="User input is missing or not a valid string")

        # Debugging log for user_input
        print(f"DEBUG: Extracted user input content... {user_input}\n")

        # Generate embedding for user input
        try:
            user_embedding_response = embeddings(
                model="nomic-embed-text:latest",
                prompt=user_input  # Pass the plain string directly
            )
            user_embedding = user_embedding_response["embedding"]  # Extract the embedding
        except Exception as e:
            print(f"ERROR: Failed to generate embedding: {e}")
            raise HTTPException(status_code=500, detail="Embedding generation failed")

        # Debugging log for embeddings
        # print(f"DEBUG: Generated embedding for user input... {user_embedding}")
        print(f"** DEBUG **: Generated embedding for user input...")


        # Retrieve similar conversations
        similar_conversations = find_similar_conversations(user_embedding)

        conversation_history = [
            msg for msg in redis_client.get_conversation_history(user_id)
            if msg.get("role") and msg.get("content")
        ]


        print(f"DEBUG: user_input... {user_input}")
        print(f"DEBUG: conversation_history... {conversation_history}")
        print(f"DEBUG: similar_conversations... {similar_conversations}")

        
        # Combine context with user input
        messages = [{'role': 'system', 'content': REBECCA_PERSONA_PROMPT}] + conversation_history
        messages.append({'role': 'user', 'content': user_input})

        print(f"DEBUG: Final messages for chat:\n {messages}")

        # Validate messages
        for message in messages:
            if not message.get("role") or not message.get("content"):
                raise HTTPException(status_code=400, detail="Invalid message format in conversation history")

        # Include similar conversations in context
        for conv in similar_conversations:
            messages.append({'role': 'assistant', 'content': conv.get("response", "")})

        # Debugging logs
        # print(f"DEBUG: Received user input...")
        # print(f"DEBUG: Messages prepared for model...")
        print(f"DEBUG: User ID... {user_id}")


        # Generator function for streaming responses
        async def generate_response_stream():
            """Stream the response while ensuring uniqueness."""
            response_stream = chat(model, messages=messages, stream=True)

            full_response = "" # To accumulate the full response
            buffer = ""

            for chunk in response_stream:
                # print(f"DEBUG: Chunk received...")
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

            # Calculate scores
            context = " ".join([msg["content"] for msg in conversation_history])
            user_scores = calculate_scores(user_input, context)
            assistant_scores = calculate_scores(full_response, context)

            # Update Redis with the latest user and assistant messages
            redis_client.add_message_to_history(
                user_id,
                "user", 
                {**{'content': user_input}, **user_scores}
            )
            redis_client.add_message_to_history(
                user_id,
                'assistant', 
                {**{'content': full_response}, **assistant_scores}
            )
            redis_client.trim_history(user_id)  # Keep history within the limit
            
            # Store the conversation
            store_conversations(
                user_id=int(user_id),
                role="user", 
                prompt=user_input,
                response=None, 
                metadata=user_scores
            )
            
            store_conversations(
                user_id=int(user_id),
                role="assistant", 
                prompt=None,
                response=full_response, 
                metadata=assistant_scores
            )
            print("DEBUG: Conversation stored successfully...")
        
        # Return a stream of responses      
        return StreamingResponse(generate_response_stream(), media_type='text/event-stream')

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))