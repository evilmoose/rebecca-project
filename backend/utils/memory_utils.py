import redis
import json
from langchain.memory import ConversationBufferMemory

# Initialize Redis client
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)

def save_stm_to_redis(user_id, buffer_memory):
    stm_data = [{"role": msg["role"], "content": msg["content"]} for msg in buffer_memory.load_memory_variables({})["chat_history"]]
    redis_client.set(f"stm:{user_id}", json.dumps(stm_data))

def load_stm_from_redis(user_id):
    stm_data = redis_client.get(f"stm:{user_id}")
    return json.loads(stm_data) if stm_data else []

def initialize_stm_from_redis(user_id):
    stm_data = load_stm_from_redis(user_id)
    return ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        initial_messages=stm_data
    )
