import redis
import os
import json
from ollama import embeddings
from utils.db_utils import connect_db, find_similar_conversations

class RedisClient:
    def __init__(self):
        self.redis_client = redis.StrictRedis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )

    def get_conversation_history(self, user_id, max_messages=10):
        """Retrieve the conversation history for a user."""
        conversation_key = f"chat_history:{user_id}"
        messages = self.redis_client.lrange(conversation_key, -max_messages, -1)
        print(f"** DEBUG **: Retrieved conversation history for user {user_id}... \n{messages}")
        # Deserialize and ensure role is included
        return [
            {
                "role": json.loads(message).get("role"),
                "content": json.loads(message).get("content")
            }
            for message in messages
        ] if messages else []

    def add_message_to_history(self, user_id, role, message):
        """Add a message to the user's conversation history."""
        conversation_key = f"chat_history:{user_id}"
        msg_data = {
            "role": role,
            "content": message  # Use 'message' here, as it matches the parameter name
        }
        if message:  # Skip empty messages
            self.redis_client.rpush(conversation_key, json.dumps(message))
            print(f"DEBUG: Added message to history for user {user_id}: {msg_data}")

    def trim_history(self, user_id, max_messages=10):
        """Trim the conversation history to the last `max_messages` messages."""
        conversation_key = f"chat_history:{user_id}"
        self.redis_client.ltrim(conversation_key, -max_messages, -1)
        print(f"DEBUG: Trimmed conversation history for user {user_id} to last {max_messages} messages")

    def clear_history(self, user_id):
        """Clear the conversation history for a user."""
        conversation_key = f"chat_history:{user_id}"
        self.redis_client.delete(conversation_key)
        print(f"DEBUG: Cleared conversation history for user {user_id}")

    def sync_with_redis(self, user_id, role, content):
        """
        Add a new message to Redis STM and sync with PostgreSQL LTM.
        """
        try:
            # Add to Redis
            self.add_message_to_history(user_id, {"role": role, "content": content})

            # Fetch embedding from PostgreSQL
            if content:  # Only generate embeddings if content is not empty
                embedding_response = embeddings("nomic-embed-text:latest", [{"role": role, "content": content}])
                embedding = embedding_response[0]["embedding"]

            # Store the embedding in PostgreSQL
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversations_embeddings (id, embedding)
                    VALUES (%s, %s)
                """, (user_id, embedding))
                conn.commit()

            print(f"DEBUG: Successfully synced Redis STM with PostgreSQL LTM for User ID {user_id}")
        except Exception as e:
            print(f"ERROR: Failed to sync STM with LTM: {e}")

    def fetch_contextual_memory(self,   user_id, embedding_vector):
        """
        Fetch both Redis STM and similar conversations from PostgreSQL embeddings.
        """
        try:
            # Fetch recent conversation history from Redis
            recent_history = self.get_conversation_history(user_id)

            # Fetch similar conversations from PostgreSQL
            similar_conversations = find_similar_conversations(embedding_vector)

            # Combine STM and similar conversations
            context = recent_history + [{"role": "assistant", "content": conv["response"]} for conv in similar_conversations]

            print(f"DEBUG: Context fetched for User ID {user_id}")
            return context
        except Exception as e:
            print(f"ERROR: Failed to fetch contextual memory for User ID {user_id}: {e}")
            return []

