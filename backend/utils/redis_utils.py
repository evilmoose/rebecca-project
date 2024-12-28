import redis
import os
import json

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
        
        print(f"DEBUG: Retrieved conversation history for user {user_id}: {messages}")
        
        return [json.loads(message) for message in messages] if messages else []

    def add_message_to_history(self, user_id, message):
        """Add a message to the user's conversation history."""
        conversation_key = f"chat_history:{user_id}"
        self.redis_client.rpush(conversation_key, json.dumps(message))

        print(f"DEBUG: Added message to history for user {user_id}: {message}")

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
