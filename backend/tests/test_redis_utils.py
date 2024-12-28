from backend.utils.redis_utils import RedisClient

# Initialize Redis client
redis_client = RedisClient()

# Test data
user_id = "123"
test_message_user = {"role": "user", "content": "Hello, Redis!"}
test_message_assistant = {"role": "assistant", "content": "Hi there, user!"}

# Test functions
def test_redis_utils():
    print("Testing Redis Client...")

    # Clear any existing data for the user
    redis_client.clear_history(user_id)
    print(f"History cleared for user {user_id}")

    # Add a user message to history
    redis_client.add_message_to_history(user_id, test_message_user)
    print(f"Added user message: {test_message_user}")

    # Add an assistant message to history
    redis_client.add_message_to_history(user_id, test_message_assistant)
    print(f"Added assistant message: {test_message_assistant}")

    # Retrieve and print conversation history
    history = redis_client.get_conversation_history(user_id)
    print(f"Retrieved conversation history for user {user_id}: {history}")

    # Trim history (optional test for max limit)
    redis_client.trim_history(user_id, max_messages=1)
    trimmed_history = redis_client.get_conversation_history(user_id)
    print(f"Trimmed conversation history for user {user_id}: {trimmed_history}")

    print("All tests completed successfully!")

# Run the test
if __name__ == "__main__":
    test_redis_utils()
